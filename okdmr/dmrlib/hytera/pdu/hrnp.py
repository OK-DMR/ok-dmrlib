import enum
from typing import Optional, Union, Tuple, Literal

from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


@enum.unique
class HRNPOpcodes(enum.Enum):
    CONNECT = 0xFE
    ACCEPT = 0xFD
    REJECT = 0xFC
    CLOSE = 0xFB
    CLOSE_ACK = 0xFA
    DATA = 0x00
    DATA_ACK = 0x10


class HRNP(BytesInterface):
    """
    Hytera Radio Network Protocol - big-endian, transport wrapper for Hytera PDUs over IP or USB interface

    | Header (0x7E) | HRNP Version (0x00 - 0x04) | Fragment number (0x00 - 0xFF) | Opcode (0x00 - 0xFF) |
    | Source (0x00 - 0xFF) | Destination (0x00 - 0xFF) | Packet Number (0x0000 - 0xFFFF) | Data Length (0x0000 - 0xFFFF) |
    | HRNP Header Checksum (0x0000 - 0xFFFF) | Data (Payload, HDAP in case Opcode == DATA)
    """

    def __init__(
        self,
        data: Optional[Union[bytes, HDAP]] = None,
        opcode: HRNPOpcodes = HRNPOpcodes.CONNECT,
        source: int = 0x20,
        destination: int = 0x10,
        block_number: int = 0x00,
        packet_number: int = 0x00,
        checksum: Union[int, bytes] = b"\x00\x00",
        header: Union[int, bytes] = b"\x7E",
        version: Union[int, bytes] = b"\x04",
    ):
        """

        :param data: inner (wrapped) data, can be HDAP
        :param checksum: if non-zero checksum provided, it will be checked
        :param header: constant 0x7E
        :param version: current (last) version is 0x04
        :param opcode: from HRNPOpcodes enum
        :param source: single-byte (0x20 or random in 0x20-0x30 range until master assigns address to slave)
        :param destination: single-byte (0x10
        :param packet_number: two-byte big-endian number (0-65535)
        """
        self.opcode: HRNPOpcodes = opcode
        self.source: int = source
        self.destination: int = destination
        self.block_number: int = block_number
        self.packet_number: int = packet_number
        self.data: Optional[HDAP] = (
            HDAP.from_bytes(data) if isinstance(data, bytes) else data
        )
        self.header: bytes = (
            header.to_bytes(length=1, byteorder="big")
            if isinstance(header, int)
            else header
        )
        self.version: bytes = (
            version.to_bytes(length=1, byteorder="big")
            if isinstance(version, int)
            else version
        )
        (
            self.checksum_correct,
            self.checksum,
        ) = self.verify_checksum(checksum=checksum)

    @staticmethod
    def from_bytes(data: bytes, endian: Literal["big", "little"] = "big") -> "HRNP":
        assert (
            len(data) >= 12
        ), f"At least 12-bytes for HRNP required, got {len(data)} bytes instead"
        hrnp_packet_len = int.from_bytes(data[8:10], byteorder="big")
        return HRNP(
            header=data[0:1],
            version=data[1:2],
            block_number=data[2],
            opcode=HRNPOpcodes(data[3]),
            source=data[4],
            destination=data[5],
            packet_number=int.from_bytes(data[6:8], byteorder="big"),
            checksum=data[10:12],
            data=data[12:hrnp_packet_len],
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return (
            self.header
            + self.version
            + bytes(
                [self.block_number, self.opcode.value, self.source, self.destination]
            )
            + self.packet_number.to_bytes(length=2, byteorder="big")
            + len(self).to_bytes(2, byteorder="big")
            + self.checksum
            + (self.data.as_bytes() if self.has_data() else b"")
        )

    def has_data(self):
        return self.opcode == HRNPOpcodes.DATA

    def __len__(self):
        return 12 + (len(self.data) if self.has_data() else 0)

    def __repr__(self):
        return (
            f"[HRNP v{self.version.hex()}] [SOURCE: {self.source}] [DESTINATION: {self.destination}] "
            f"[PN: {self.packet_number}] [BLOCK: {self.block_number}] [{self.opcode}] "
            + (repr(self.data) if self.opcode == HRNPOpcodes.DATA else "")
        )

    def verify_checksum(
        self, checksum: Union[bytes, int] = b"\x00\x00"
    ) -> Tuple[bool, bytes]:
        checked_data: bytes = (
            self.header
            + self.version
            + bytes(
                [self.block_number, self.opcode.value, self.source, self.destination]
            )
            + self.packet_number.to_bytes(length=2, byteorder="big")
            + len(self).to_bytes(2, byteorder="big")
        )
        if self.has_data():
            checked_data += self.data.as_bytes()
        if len(checked_data) % 2 == 1:
            # pad with single zero byte, to allow for crc16 checksum
            checked_data += b"\x00"

        checksum: int = (
            checksum
            if isinstance(checksum, int)
            else int.from_bytes(checksum, byteorder="big")
        )

        # weird quirk, checksum is always off-by-one when opcode is HRNPOpcodes.DATA
        check: int = 1 if self.has_data() else 0

        for i in range(0, len(checked_data), 2):
            check = (
                check + int.from_bytes(checked_data[i : i + 2], byteorder="big")
            ) & 0xFFFF
        check = (check ^ 0xFFFF) & 0xFFFF

        return check == checksum, check.to_bytes(length=2, byteorder="big")
