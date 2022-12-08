import logging
import os
from asyncio import (
    DatagramProtocol,
    DatagramTransport,
    get_running_loop,
    AbstractEventLoop,
    new_event_loop,
    BaseTransport,
)
from datetime import datetime
from signal import SIGINT, SIGTERM
from typing import Union, Tuple, Any, Optional, List, Dict

from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType
from okdmr.dmrlib.hytera.pdu.radio_registration_service import (
    RRSRadioState,
    RadioRegistrationService,
    RRSTypes,
    RRSResult,
)
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HSTRPLayer(DatagramProtocol, LoggingTrait):
    """
    HSTRP Protocol, handling HSTRP itself setup/teardown/timeout and passing data down to application protocol layer
    """

    T_HEARTBEAT: int = 6
    """number of seconds between heartbeats to maintain NAT-T"""
    T_NUMBEAT: int = 10
    """number of max lost/missed heartbeats, exceeding it means connection is considered lost"""
    T_NUMRETRY: int = 3
    """number of retries to deliver single HSTRP packet, not being able (or not receiving ACK in timeout) means HSTRP packet was not-delivered and should be discarded"""

    def __init__(self, port: int) -> None:
        self.transport: Optional[DatagramTransport] = None
        self.hstrp_connected: bool = False
        self.hstrp_last_contact: datetime = datetime.now()
        self.hstrp_last_heartbeat: datetime = datetime.now()
        self.port: int = port
        self.sn: int = 0

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
        self, addr: Tuple[Union[str, Any], int], request: HSTRP
    ) -> HSTRP:
        """
        Will directly send out ACK for given request to provided addr

        @param addr:
        @param request:
        @return: ACK HSTRP object
        """
        ack: HSTRP = request
        request.pkt_type.is_ack = True
        request.payload = None
        if self.transport:
            # self.log_debug(f"hstrp_send_ack {repr(ack)}")
            self.transport.sendto(data=ack.as_bytes(), addr=addr)
        return ack

    def hstrp_send_heartbeat(
        self, addr: Tuple[Union[str, Any], int], request: Optional[HSTRP]
    ) -> HSTRP:
        """
        Will directly send out HEARTBEAT to provided addr

        @param addr:
        @param request:
        @return:
        """
        hb: HSTRP = HSTRP(pkt_type=HSTRPPacketType(is_heartbeat=True), sn=0)
        if self.transport:
            # self.log_debug(f"hstrp_send_heartbeat {repr(hb)}")
            self.transport.sendto(data=hb.as_bytes(), addr=addr)
        return hb

    def connection_made(self, transport: BaseTransport) -> None:
        if self.transport and not self.transport.is_closing():
            self.log_warning(
                f"HSTRP transport being replaced, old not yet disconnected"
            )
            self.transport.close()
        self.transport = transport

    def connection_lost(self, exc: Union[Exception, None]) -> None:
        self.hstrp_connected = False

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        """
        In case invalid-HSTRP or non-HSTRP datagram arrives, it will not be passed to upper layers

        @param data:
        @param addr:
        @return: Tuple[(pdu was handled, by HSTRPLayer itself), (optionally parsed HSTRP object)]
        """
        pdu = HSTRP.from_bytes(data=data)
        was_handled: bool = False
        was_confirmed: bool = False
        if (
            not pdu
            or not isinstance(pdu, HSTRP)
            or (
                isinstance(pdu, HSTRP)
                and not pdu.pkt_type.is_ack
                and not pdu.pkt_type.is_heartbeat
            )
        ):
            self.log_debug(
                f"datagram_received on {self.port} from {addr} data {data.hex()}"
            )

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
        if pdu.pkt_type.is_heartbeat:
            # heartbeat
            was_handled = True
            # HEARTBEAT is not confirmed protocol
            was_confirmed = True
            if self.hstrp_connected:
                # TODO use T_HEARTBEAT and send own heartbeats (not-just copy peer timer/heartbeats)
                self.hstrp_send_heartbeat(addr, pdu)
        if pdu.pkt_type.is_close:
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


class RCPLayer(HSTRPLayer):
    def __init__(self, port: int) -> None:
        super().__init__(port=port)
        self.radios: Dict[int, HSTRP] = {}

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        was_handled, pdu = super().datagram_received(data=data, addr=addr)
        if not pdu:
            return was_handled, pdu

        if not was_handled:
            self.log_warning(f"RCP did not handle {data.hex()}")
            self.log_warning(repr(pdu))

        return was_handled, pdu


class RRSLayer(HSTRPLayer):
    def __init__(self, port: int):
        super().__init__(port=port)
        self.registry: Dict[str, RRSRadioState] = {}

    def rrs_confirm(self, pdu: HSTRP, addr: Tuple[Union[str, Any], int]):
        assert isinstance(pdu.payload, RadioRegistrationService)
        rrs = RadioRegistrationService(
            opcode=RRSTypes.RadioRegistrationAnswer,
            radio_ip=pdu.payload.radio_ip,
            result=RRSResult.Success,
            renew_time_seconds=60 * 5,
        )
        hstrp = HSTRP(
            pkt_type=HSTRPPacketType(
                have_options=True,
            ),
            payload=rrs,
            sn=self.hstrp_increment_sn(),
        )
        self.transport.sendto(data=hstrp.as_bytes(), addr=addr)

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        was_handled, pdu = super().datagram_received(data=data, addr=addr)
        if not pdu:
            return was_handled, pdu

        rrs: RadioRegistrationService = (
            pdu.payload if isinstance(pdu.payload, RadioRegistrationService) else None
        )

        if rrs.opcode == RRSTypes.RadioRegistrationRequest:
            was_handled = True
            self.registry[rrs.radio_ip.as_ip()] = RRSRadioState.Online
            self.rrs_confirm(pdu, addr)
        elif rrs.opcode == RRSTypes.RadioGoingOffline:
            was_handled = True
            self.registry[rrs.radio_ip.as_ip()] = RRSRadioState.Offline

        if not was_handled:
            self.log_warning(f"RRS did not handle {data.hex()}")
            self.log_warning(repr(pdu))

        return was_handled, pdu


class RRSApp(LoggingTrait):
    DEF_PORT_SLOT1: int = 30_001
    DEF_PORT_SLOT2: int = 30_002
    EXTRA_PORTS: List[int] = [
        # mobile
        3_002,
        3_003,
        5_016,
        3_005,
        3_006,
        3_007,
        3_009,
        # GPS
        30_003,
        30_004,
        # telemetry
        30_005,
        30_006,
        # tms
        30_007,
        30_008,
        # radio control
        30_009,
        30_010,
        # voice service
        30_012,
        30_014,
        # analog call control
        30_015,
        30_016,
        # e2e
        30_017,
        30_018,
        # sdmp
        3_017,
        3_018,
    ]

    def __init__(
        self,
        ip: str = "10.0.0.1",  # "192.168.22.13",
        slot1_port: int = DEF_PORT_SLOT1,
        slot2_port: int = DEF_PORT_SLOT2,
    ):
        self.loop: Optional[AbstractEventLoop] = None
        self.ip: str = ip
        self.port_slot1: int = slot1_port
        self.port_slot2: int = slot2_port
        self.slot1: RRSLayer = RRSLayer(port=self.port_slot1)
        self.slot2: RRSLayer = RRSLayer(port=self.port_slot2)
        self.extras: Dict[int, HSTRPLayer] = {}

    async def go(self) -> None:
        self.log_info("RRSApp.go")
        self.loop = get_running_loop()

        await self.loop.create_datagram_endpoint(
            lambda: self.slot1, local_addr=(self.ip, self.port_slot1)
        )
        await self.loop.create_datagram_endpoint(
            lambda: self.slot2, local_addr=(self.ip, self.port_slot2)
        )
        for extra_port in self.EXTRA_PORTS:
            self.extras[extra_port] = (
                RCPLayer(port=extra_port)
                if extra_port
                in (
                    30_009,
                    30_010,
                )
                else HSTRPLayer(port=extra_port)
            )
            await self.loop.create_datagram_endpoint(
                lambda: self.extras[extra_port], local_addr=(self.ip, extra_port)
            )

    def stop(self) -> None:
        self.log_info("stop at signal handler")
        self.loop.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app: RRSApp = RRSApp()
    loop = new_event_loop()

    if os.name != "nt":
        for signal in [SIGINT, SIGTERM]:
            loop.add_signal_handler(signal, app.stop)

    loop.run_until_complete(future=app.go())
    loop.run_forever()
