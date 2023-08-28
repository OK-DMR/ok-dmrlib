from asyncio import DatagramProtocol, DatagramTransport, BaseTransport
from socket import socket
from typing import Optional

from okdmr.dmrlib.storage import ADDRESS_TYPE
from okdmr.dmrlib.storage.repeater_storage import RepeaterStorage
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class P2PDatagramProtocol(DatagramProtocol, LoggingTrait):
    COMMAND_PREFIX: bytes = bytes([0x50, 0x32, 0x50])
    PING_PREFIX: bytes = bytes([0x0A, 0x00, 0x00, 0x00, 0x14])
    ACK_PREFIX: bytes = bytes([0x0C, 0x00, 0x00, 0x00, 0x14])

    PACKET_TYPE_REQUEST_REGISTRATION = 0x10
    PACKET_TYPE_REQUEST_DMR_STARTUP = 0x11
    PACKET_TYPE_REQUEST_RDAC_STARTUP = 0x12
    KNOWN_PACKET_TYPES = [
        PACKET_TYPE_REQUEST_DMR_STARTUP,
        PACKET_TYPE_REQUEST_RDAC_STARTUP,
        PACKET_TYPE_REQUEST_REGISTRATION,
    ]

    STORAGE_ATTR_IS_REGISTERED = "p2p_is_registered"

    def __init__(
        self,
        storage: RepeaterStorage,
        p2p_port: int = 50000,
        rdac_port: int = 50002,
    ):
        """ """
        self.p2p_port: int = p2p_port
        self.rdac_port: int = rdac_port
        self.transport: Optional[DatagramTransport] = None
        self.storage: RepeaterStorage = storage

    @staticmethod
    def packet_is_command(data: bytes) -> bool:
        return data[:3] == P2PDatagramProtocol.COMMAND_PREFIX

    @staticmethod
    def packet_is_ping(data: bytes) -> bool:
        return data[4:9] == P2PDatagramProtocol.PING_PREFIX

    @staticmethod
    def packet_is_ack(data: bytes) -> bool:
        return data[4:9] == P2PDatagramProtocol.ACK_PREFIX

    @staticmethod
    def command_get_type(data: bytes) -> int:
        return data[20] if len(data) > 20 else 0

    def handle_registration(self, data: bytes, address: ADDRESS_TYPE) -> None:
        data = bytearray(data)
        data[3] = 0x50
        # set repeater ID
        data[4] += 1
        # set operation result status code
        data[13] = 0x01
        data[14] = 0x01
        data[15] = 0x5A
        data.append(0x01)

        rpt = self.storage.match_incoming(address=address, auto_create=True)

        self.transport.sendto(data, rpt.address_out)

        rpt.read_snmp_values(self.storage)
        rpt.attr(self.STORAGE_ATTR_IS_REGISTERED, True)

    def handle_rdac_request(self, data: bytes, address: ADDRESS_TYPE) -> None:
        rpt = self.storage.match_incoming(address)
        if not rpt or not rpt.attr(self.STORAGE_ATTR_IS_REGISTERED):
            self.log_debug(
                f"Rejecting RDAC request for not-registered repeater {address[0]}"
            )
            self.transport.sendto(bytes([0x00]), address)
            return

        data = bytearray(data)
        # set RDAC id
        data[4] += 1
        # set operation result status code
        data[13] = 0x01
        data.append(0x01)

        # todo: verify address was response_address
        self.transport.sendto(data, rpt.address_out)
        self.log_debug("RDAC Accept for %s:%s" % address)

        # redirect repeater to correct RDAC port
        data = self.get_redirect_packet(data, self.rdac_port)
        self.transport.sendto(data, rpt.address_out)

    def get_redirect_packet(self, data: bytearray, target_port: int):
        self.log_debug(f"Providing redirect packet to port {target_port}")
        data = data[: len(data) - 1]
        data[4] = 0x0B
        data[12] = 0xFF
        data[13] = 0xFF
        data[14] = 0x01
        data[15] = 0x00
        data += bytes([0xFF, 0x01])
        data += target_port.to_bytes(2, "little")
        return data

    def handle_dmr_request(self, data: bytes, address: ADDRESS_TYPE) -> None:
        rpt = self.storage.match_incoming(address)
        if not rpt or not rpt.attr(self.STORAGE_ATTR_IS_REGISTERED):
            self.log_debug(
                f"Rejecting DMR request for not-registered repeater {address[0]}"
            )
            self.transport.sendto(bytes([0x00]), address)
            return

        response_address = (address[0], self.p2p_port)

        data = bytearray(data)
        # set DMR id
        data[4] += 1
        data[13] = 0x01
        data.append(0x01)

        self.transport.sendto(data, response_address)
        self.log_debug("DMR Accept for %s:%s" % address)

        # use configured
        data = self.get_redirect_packet(data, rpt.address_in[1])
        self.transport.sendto(data, response_address)

    def handle_ping(self, data: bytes, address: ADDRESS_TYPE) -> None:
        rpt = self.storage.match_incoming(address=address)
        if not rpt or not rpt.attr(self.STORAGE_ATTR_IS_REGISTERED):
            self.log_debug(
                f"Rejecting ping request for not-registered repeater {address[0]}"
            )
            self.transport.sendto(bytes([0x00]), address)
            return
        data = bytearray(data)
        data[12] = 0xFF
        data[14] = 0x01
        self.transport.sendto(data, address)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.log_debug("connection lost")
        if exc:
            self.log_exception(exc)

    def connection_made(self, transport: BaseTransport) -> None:
        self.transport = transport
        sock: socket = transport.get_extra_info("socket")
        if sock:
            self.log_debug(f"new peer {sock}")
        self.log_debug("connection prepared")

    def datagram_received(self, data: bytes, address: ADDRESS_TYPE) -> None:
        packet_type = self.command_get_type(data)
        is_command = self.packet_is_command(data)
        # must be handled outside
        # self.settings.ensure_repeater_data(address)
        if is_command:
            if packet_type not in self.KNOWN_PACKET_TYPES:
                if not self.packet_is_ack(data):
                    self.log_error("Received %s bytes from %s" % (len(data), address))
                    self.log_error(data.hex())
                    self.log_error("Idle packet of type:%s received" % packet_type)
            if packet_type == self.PACKET_TYPE_REQUEST_REGISTRATION:
                self.handle_registration(data, address)
            elif packet_type == self.PACKET_TYPE_REQUEST_RDAC_STARTUP:
                self.handle_rdac_request(data, address)
            elif packet_type == self.PACKET_TYPE_REQUEST_DMR_STARTUP:
                self.handle_dmr_request(data, address)
        elif self.packet_is_ping(data):
            self.handle_ping(data, address)
        else:
            self.log_error(
                "Idle packet received, %d bytes from %s" % (len(data), address)
            )
            self.log_debug(data.hex())

    def disconnect(self) -> None:
        if self.transport and not self.transport.is_closing():
            # reset connection state
            self.transport.sendto(bytes([0x00]))
