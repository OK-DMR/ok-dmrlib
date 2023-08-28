import asyncio
from asyncio import DatagramProtocol, DatagramTransport, BaseTransport
from copy import deepcopy
from datetime import datetime
from typing import Optional, Tuple, Union, Any

from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HSTRPDatagramProtocol(DatagramProtocol, LoggingTrait):
    """
    HSTRP Protocol, handling HSTRP itself setup/teardown/timeout and passing data down to application protocol layer
    """

    T_HEARTBEAT: int = 6
    """number of seconds between heartbeats to maintain NAT-T"""
    T_NUMBEAT: int = 10
    """number of max lost/missed heartbeats, exceeding it means connection is considered lost"""
    T_NUMRETRY: int = 3
    """number of retries to deliver single HSTRP packet, not being able (or not receiving ACK in timeout) means HSTRP packet was not-delivered and should be discarded"""

    def __init__(self, port: int, be_active_peer: bool = False) -> None:
        self.transport: Optional[DatagramTransport] = None
        self.hstrp_connected: bool = False
        self.hstrp_last_contact: datetime = datetime.now()
        self.hstrp_last_heartbeat: datetime = datetime.now()
        self.port: int = port
        self.sn: int = 0
        self.be_active_peer: bool = be_active_peer

    def hstrp_increment_sn(self) -> int:
        # HSTRP S/N is 2-bytes (16-bit) value
        self.sn = (self.sn + 1) % 0xFFFF
        return self.sn

    def hstrp_set_connected(self, connected: bool = True) -> None:
        if connected != self.hstrp_connected:
            self.log_info(
                f"HSTRP({self.port}) {'CONNECTED' if connected else 'DISCONNECTED'}"
            )
            self.hstrp_connected = connected

    def hstrp_send_ack(
        self, addr: Tuple[Union[str, any], int], request: HSTRP, reject: bool = False
    ) -> HSTRP:
        """
        Will directly send out ACK for given request to provided addr

        @param addr:
        @param request:
        @param reject:
        @return: ACK HSTRP object
        """
        ack: HSTRP = deepcopy(request)
        ack.pkt_type.is_ack = not reject
        ack.pkt_type.is_reject = reject
        ack.payload = None
        if self.transport:
            self.transport.sendto(data=ack.as_bytes(), addr=addr)
        return ack

    def hstrp_send_heartbeat(self, addr: Tuple[Union[str, Any], int]) -> HSTRP:
        """
        Will directly send out HEARTBEAT to provided addr

        @param addr:
        @return:
        """
        hb: HSTRP = HSTRP(pkt_type=HSTRPPacketType(is_heartbeat=True), sn=0)
        if self.transport:
            # self.log_debug(f"hstrp_send_heartbeat {repr(hb)}")
            self.transport.sendto(data=hb.as_bytes(), addr=addr)
        return hb

    def connection_made(self, transport: BaseTransport) -> None:
        assert isinstance(
            transport, BaseTransport
        ), f"transport is of unexpected type {type(transport)}"
        if self.transport and not self.transport.is_closing():
            self.log_warning(
                f"HSTRP transport being replaced, old not yet disconnected"
            )
            self.transport.close()
        self.transport = transport

    def connection_lost(self, exc: Union[Exception, None]) -> None:
        self.hstrp_connected = False

    async def periodic_maintenance(self) -> None:
        self.log_info(f"periodic maintenance START")
        while asyncio.get_running_loop() and not asyncio.get_running_loop().is_closed():
            if not self.hstrp_connected:
                self.log_info(f"sending connect")
                self.transport.sendto(
                    data=HSTRP(
                        pkt_type=HSTRPPacketType(is_connect=True), sn=0
                    ).as_bytes(),
                    addr=("192.168.22.18", self.port),
                )
            await asyncio.sleep(5)
        self.log_info(f"periodic maintenance STOP")

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        """
        In case invalid-HSTRP or non-HSTRP datagram arrives, it will not be passed to upper layers

        @param data:
        @param addr:
        @return: Tuple[(pdu was handled, by HSTRPLayer itself), (optionally parsed HSTRP object)]
        """
        # noinspection PyBroadException
        try:
            pdu = HSTRP.from_bytes(data=data)
        except:
            pdu = None
            self.log_error(
                f"Could not decode HSTRP from {addr} received UDP datagram {data.hex()}"
            )

        was_handled: bool = False
        was_confirmed: bool = False

        if not isinstance(pdu, HSTRP):
            self.log_warning(f"received non HSTRP on {self.transport}")
            return was_handled, None

        self.hstrp_last_contact = datetime.now()

        if pdu.pkt_type.is_connect:
            # connection request
            was_handled = True
            was_confirmed = True
            self.hstrp_set_connected(connected=True)
            self.hstrp_send_ack(addr, pdu)
        elif pdu.pkt_type.is_heartbeat:
            # heartbeat
            was_handled = True
            # HEARTBEAT is not confirmed protocol
            was_confirmed = True
            if self.hstrp_connected:
                # TODO use T_HEARTBEAT and send own heartbeats (not-just copy peer timer/heartbeats)
                self.hstrp_send_heartbeat(addr)
        elif pdu.pkt_type.is_close:
            # connection teardown
            self.hstrp_set_connected(connected=False)
            was_handled = True
            # CLOSE is not confirmed protocol
            was_confirmed = True
            # confirm connection closing hstrp message
            self.hstrp_send_ack(addr, pdu)
        elif pdu.pkt_type.is_ack:
            # received confirmation from peer
            was_handled = True
            was_confirmed = True
        elif pdu.pkt_type.is_reject:
            was_handled = True
            self.log_warning(f"peer REJECT-ed our request S/N:{pdu.sn}")
            self.log_warning(repr(pdu))

        if not was_confirmed and not pdu.pkt_type.is_ack:
            # confirm all hstrp incoming messages, that are not confirmations
            self.hstrp_send_ack(addr, pdu)

        return (
            (was_handled, pdu) if isinstance(pdu.payload, HDAP) else (was_handled, None)
        )
