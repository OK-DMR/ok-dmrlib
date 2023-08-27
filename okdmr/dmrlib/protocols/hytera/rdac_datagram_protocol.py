from asyncio import DatagramProtocol, transports
from binascii import hexlify
from typing import Optional, Dict, Callable
from uuid import UUID

from okdmr.dmrlib.storage import ADDRESS_TYPE
from okdmr.dmrlib.storage.repeater_storage import RepeaterStorage
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


RDAC_FINISHED_CALLBACK_TYPE = Callable[[UUID], None]


class RDACDatagramProtocol(DatagramProtocol, LoggingTrait):
    STEP0_REQUEST = bytes(
        [0x7E, 0x04, 0x00, 0xFE, 0x20, 0x10, 0x00, 0x00, 0x00, 0x0C, 0x60, 0xE1]
    )
    STEP0_RESPONSE = bytes([0x7E, 0x04, 0x00, 0xFD])
    STEP1_REQUEST = bytes(
        [
            0x7E,
            0x04,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x01,
            0x00,
            0x18,
            0x9B,
            0x60,
            0x02,
            0x04,
            0x00,
            0x05,
            0x00,
            0x64,
            0x00,
            0x00,
            0x00,
            0x01,
            0xC4,
            0x03,
        ]
    )
    STEP1_RESPONSE = bytes([0x7E, 0x04, 0x00, 0x10])
    STEP2_RESPONSE = bytes([0x7E, 0x04, 0x00, 0x00])
    STEP3_REQUEST = bytes(
        [0x7E, 0x04, 0x00, 0x10, 0x20, 0x10, 0x00, 0x01, 0x00, 0x0C, 0x61, 0xCE]
    )
    STEP3_RESPONSE = bytes([0x7E, 0x04, 0x00, 0x00])
    STEP4_REQUEST_1 = bytes(
        [0x7E, 0x04, 0x00, 0x10, 0x20, 0x10, 0x00, 0x02, 0x00, 0x0C, 0x61, 0xCD]
    )
    STEP4_REQUEST_2 = bytes(
        [
            0x7E,
            0x04,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x02,
            0x00,
            0x19,
            0x58,
            0xA0,
            0x02,
            0xD4,
            0x02,
            0x06,
            0x00,
            0x64,
            0x00,
            0x00,
            0x00,
            0x02,
            0x00,
            0xF0,
            0x03,
        ]
    )
    STEP4_RESPONSE_1 = bytes([0x7E, 0x04, 0x00, 0x10])
    STEP4_RESPONSE_2 = bytes([0x7E, 0x04, 0x00, 0x00])
    STEP6_REQUEST_1 = bytes(
        [0x7E, 0x04, 0x00, 0x10, 0x20, 0x10, 0x00, 0x03, 0x00, 0x0C, 0x61, 0xCC]
    )
    STEP6_REQUEST_2 = bytes(
        [
            0x7E,
            0x04,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x03,
            0x00,
            0x19,
            0x73,
            0x84,
            0x02,
            0xD6,
            0x82,
            0x06,
            0x00,
            0x00,
            0x64,
            0x00,
            0x00,
            0x00,
            0x02,
            0x6E,
            0x03,
        ]
    )
    STEP6_RESPONSE = bytes([0x7E, 0x04, 0x00, 0x10])
    STEP7_REQUEST = bytes(
        [
            0x7E,
            0x04,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x04,
            0x00,
            0x19,
            0x57,
            0x9F,
            0x02,
            0xD4,
            0x02,
            0x06,
            0x00,
            0x64,
            0x00,
            0x00,
            0x00,
            0x02,
            0x01,
            0xEF,
            0x03,
        ]
    )
    STEP7_RESPONSE_1 = bytes([0x7E, 0x04, 0x00, 0x10])
    STEP7_RESPONSE_2 = bytes([0x7E, 0x04, 0x00, 0x00])
    STEP10_REQUEST = bytes(
        [
            0x7E,
            0x04,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x15,
            0x00,
            0x18,
            0x9C,
            0x4B,
            0x02,
            0x05,
            0x00,
            0x05,
            0x00,
            0x64,
            0x00,
            0x00,
            0x00,
            0x01,
            0xC3,
            0x03,
        ]
    )
    STEP10_RESPONSE_1 = bytes([0x7E, 0x04, 0x00, 0x10])
    STEP10_RESPONSE_2 = bytes([0x7E, 0x04, 0x00, 0x00])
    STEP12_REQUEST_1 = bytes(
        [0x7E, 0x04, 0x00, 0x10, 0x20, 0x10, 0x00, 0x15, 0x00, 0x0C, 0x61, 0xBA]
    )
    STEP12_REQUEST_2 = bytes(
        [0x7E, 0x04, 0x00, 0xFB, 0x20, 0x10, 0x00, 0x16, 0x00, 0x0C, 0x60, 0xCE]
    )
    STEP12_RESPONSE = bytes([0x7E, 0x04, 0x00, 0xFA])

    STORAGE_ATTR_CALLSIGN: str = "callsign"
    STORAGE_ATTR_HARDWARE: str = "rdac_hardware"
    STORAGE_ATTR_FIRMWARE: str = "rdac_firmware"
    STORAGE_ATTR_SERIALNO: str = "serial"
    STORAGE_ATTR_RX_FREQ: str = "rx_freq"
    STORAGE_ATTR_TX_FREQ: str = "tx_freq"

    def __init__(
        self, storage: RepeaterStorage, callback: RDAC_FINISHED_CALLBACK_TYPE = None
    ):
        self.transport: Optional[transports.DatagramTransport] = None
        self.callback: RDAC_FINISHED_CALLBACK_TYPE = callback
        self.storage: RepeaterStorage = storage
        self.step: Dict[str, int] = dict()

    def step0(self, _: bytes, address: ADDRESS_TYPE) -> None:
        self.log_debug("RDAC identification started")
        self.step[address[0]] = 1
        self.transport.sendto(self.STEP0_REQUEST, address)

    def step1(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP0_RESPONSE)] == self.STEP0_RESPONSE:
            self.step[address[0]] = 2
            self.transport.sendto(self.STEP1_REQUEST, address)

    def step2(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP1_RESPONSE)] == self.STEP1_RESPONSE:
            self.step[address[0]] = 3

    def step3(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP2_RESPONSE)] == self.STEP2_RESPONSE:
            self.storage.match_incoming(
                address=address,
                patch={"dmr_id": int.from_bytes(data[18:21], byteorder="little")},
            )
            self.step[address[0]] = 4
            self.transport.sendto(self.STEP3_REQUEST, address)

    def step4(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP3_RESPONSE)] == self.STEP3_RESPONSE:
            self.step[address[0]] = 5
            self.transport.sendto(self.STEP4_REQUEST_1, address)
            self.transport.sendto(self.STEP4_REQUEST_2, address)

    def step5(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP4_RESPONSE_1)] == self.STEP4_RESPONSE_1:
            self.step[address[0]] = 6

    def step6(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP4_RESPONSE_2)] == self.STEP4_RESPONSE_2:
            hytera_callsign: str = (
                data[88:108]
                .decode("utf_16_le")
                .encode("utf-8")
                .strip(b"\x00")
                .decode("utf-8")
            )
            hytera_hardware: str = (
                data[120:184]
                .decode("utf_16_le")
                .encode("utf-8")
                .strip(b"\x00")
                .decode("utf-8")
            )
            hytera_firmware: str = (
                data[56:88]
                .decode("utf_16_le")
                .encode("utf-8")
                .strip(b"\x00")
                .decode("utf-8")
            )
            hytera_serial_number: str = (
                data[184:216]
                .decode("utf_16_le")
                .encode("utf-8")
                .strip(b"\x00")
                .decode("utf-8")
            )
            self.step[address[0]] = 7
            self.storage.save(
                self.storage.match_incoming(address=address),
                {
                    self.STORAGE_ATTR_FIRMWARE: hytera_firmware,
                    self.STORAGE_ATTR_HARDWARE: hytera_hardware,
                    self.STORAGE_ATTR_CALLSIGN: hytera_callsign,
                    self.STORAGE_ATTR_SERIALNO: hytera_serial_number,
                },
            )
            self.transport.sendto(self.STEP6_REQUEST_1, address)
            self.transport.sendto(self.STEP6_REQUEST_2, address)

    def step7(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP6_RESPONSE)] == self.STEP6_RESPONSE:
            self.step[address[0]] = 8
            self.transport.sendto(self.STEP7_REQUEST, address)

    def step8(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP7_RESPONSE_1)] == self.STEP7_RESPONSE_1:
            self.step[address[0]] = 10

    def step10(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP7_RESPONSE_2)] == self.STEP7_RESPONSE_2:
            hytera_repeater_mode = data[26]
            self.log_error(f"Unknown HyteraRepeaterMode value {hytera_repeater_mode}")
            tx_freq = int.from_bytes(data[29:33], byteorder="little")
            rq_freq = int.from_bytes(data[33:37], byteorder="little")
            self.step[address[0]] = 11
            self.storage.match_incoming(
                address=address,
                patch={
                    self.STORAGE_ATTR_RX_FREQ: tx_freq,
                    self.STORAGE_ATTR_TX_FREQ: rq_freq,
                },
            )
            self.transport.sendto(self.STEP10_REQUEST, address)

    def step11(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP10_RESPONSE_1)] == self.STEP10_RESPONSE_1:
            self.step[address[0]] = 12

    def step12(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP10_RESPONSE_2)] == self.STEP10_RESPONSE_2:
            self.step[address[0]] = 13
            self.transport.sendto(self.STEP12_REQUEST_1, address)
            self.transport.sendto(self.STEP12_REQUEST_2, address)

    def step13(self, data: bytes, address: ADDRESS_TYPE) -> None:
        if data[: len(self.STEP12_RESPONSE)] == self.STEP12_RESPONSE:
            self.step[address[0]] = 14
            self.log_debug("rdac completed identification")

            rpt = self.storage.match_incoming(address=address)
            rpt.read_snmp_values()

            if self.callback:
                self.callback(rpt.id)

    def step14(self, data: bytes, address: ADDRESS_TYPE) -> None:
        pass

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.log_info("connection lost")
        if exc:
            self.log_exception(exc)

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        self.log_debug("connection prepared")

    def datagram_received(self, data: bytes, addr: ADDRESS_TYPE) -> None:
        self.storage.match_incoming(address=addr, auto_create=True)

        if not self.step.get(addr[0]):
            self.step[addr[0]] = 0

        if len(data) == 1 and self.step[addr[0]] != 14:
            if self.step[addr[0]] == 4:
                self.log_error(
                    "check repeater zone programming, if Digital IP"
                    "Multi-Site Connect mode allows data pass from timeslots"
                )
            self.log_error(
                "restart process if response is protocol reset and current step is not 14"
            )
            self.step[addr[0]] = 0
            self.step0(data, addr)
        elif len(data) != 1 and self.step[addr[0]] == 14:
            self.log_error("RDAC finished, received extra data %s" % hexlify(data))
        elif len(data) == 1 and self.step[addr[0]] == 14:
            if data[0] == 0x00:
                # no data available response
                self.transport.sendto(bytes(0x41), addr)
        else:
            getattr(self, "step%d" % self.step[addr[0]])(data, addr)
