import enum
from typing import Union

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class Rate1DataTypes(enum.Enum):
    Unconfirmed = 24
    Confirmed = 22
    UnconfirmedLastBlock = 20
    ConfirmedLastBlock = 18
    Undefined = 0

    @classmethod
    def _missing_(cls, value: int) -> "Rate1DataTypes":
        raise ValueError(f"Unknown Rate 1 DataType for data length {value}")

    @staticmethod
    def resolve(confirmed: bool, last: bool) -> "Rate1DataTypes":
        return {
            # confirmed, last data block
            (True, True): Rate1DataTypes.ConfirmedLastBlock,
            (True, False): Rate1DataTypes.Confirmed,
            (False, True): Rate1DataTypes.UnconfirmedLastBlock,
            (False, False): Rate1DataTypes.Unconfirmed,
        }.get((confirmed, last), Rate1DataTypes.Undefined)

    @staticmethod
    def label(rate1_data_type: "Rate1DataTypes") -> str:
        return {
            Rate1DataTypes.Undefined: "UNDEFINED",
            Rate1DataTypes.ConfirmedLastBlock: "CONFIRMED - LAST BLOCK",
            Rate1DataTypes.Confirmed: "CONFIRMED",
            Rate1DataTypes.Unconfirmed: "UNCONFIRMED",
            Rate1DataTypes.UnconfirmedLastBlock: "UNCONFIRMED - LAST BLOCK",
        }.get(rate1_data_type, "UNKNOWN")


class Rate1Data(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.15 Rate 1 coded packet Data (R_1_DATA) PDU
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.16 Rate 1 coded Last Data block (R_1_LDATA) PDU
    """

    def __init__(
        self,
        data: Union[bytes, bitarray],
        packet_type: Rate1DataTypes = Rate1DataTypes.Undefined,
        dbsn: Union[int, bitarray] = 0,
        crc9: Union[int, bitarray] = 0,
        crc32: Union[int, bytes] = 0,
    ):
        self.data: bytes = data if isinstance(data, bytes) else bits_to_bytes(data)
        self.validate_packet_type(packet_type=packet_type, data_length=len(self.data))
        self.dbsn: int = dbsn if isinstance(dbsn, int) else ba2int(dbsn)
        self.packet_type: Rate1DataTypes = Rate1DataTypes(len(self.data))
        self.crc32: int = (
            crc32 if isinstance(crc32, int) else int.from_bytes(crc32, byteorder="big")
        )

        self.crc9: int = crc9 if isinstance(crc9, int) else ba2int(crc9[::-1])
        calculated_crc9 = self.calculate_crc9()
        if self.crc9 <= 0:
            self.crc9 = calculated_crc9
        self.crc9_ok: bool = self.crc9 == calculated_crc9

    @staticmethod
    def validate_packet_type(packet_type: Rate1DataTypes, data_length: int) -> bool:
        if data_length == 0 or packet_type == Rate1DataTypes.Undefined:
            return True
        else:
            assert (
                data_length == packet_type.value
            ), f"{packet_type} data must be {packet_type.value} bytes, got {data_length} bytes"

    def is_confirmed(self) -> bool:
        return self.packet_type in (
            Rate1DataTypes.Confirmed,
            Rate1DataTypes.ConfirmedLastBlock,
        )

    def is_last_block(self) -> bool:
        return self.packet_type in (
            Rate1DataTypes.ConfirmedLastBlock,
            Rate1DataTypes.UnconfirmedLastBlock,
        )

    def calculate_crc9(self) -> int:
        return CRC9.calculate_from_parts(
            data=self.data,
            serial_number=self.dbsn,
            crc32=self.crc32,
            mask=CrcMasks.Rate1DataContinuation,
        )

    def __repr__(self) -> str:
        label: str = (
            f"[RATE 1 DATA {Rate1DataTypes.label(self.packet_type)}] "
            f"[DATA({self.packet_type.value}) {self.data.hex()}] "
        )
        if self.is_confirmed():
            label += f"[DBSN: {self.dbsn}] " f"[CRC9: {self.crc9}] " + (
                " [CRC9 INVALID]" if not self.crc9_ok else ""
            )
        if self.is_last_block():
            label += f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
        return label

    @staticmethod
    def from_bits(bits: bitarray) -> "Rate1Data":
        return Rate1Data.from_bits_typed(bits, Rate1DataTypes.Undefined)

    @staticmethod
    def from_bits_typed(
        bits: bitarray, data_type: Rate1DataTypes = Rate1DataTypes.Undefined
    ) -> "Rate1Data":
        assert (
            len(bits) == 192
        ), f"Rate 1 Data packet must be 192 bits (24 bytes) long, got {len(bits)} bits"
        if data_type in (Rate1DataTypes.Undefined, Rate1DataTypes.Unconfirmed):
            return Rate1Data(data=bits, packet_type=data_type)
        elif data_type == Rate1DataTypes.Confirmed:
            return Rate1Data(
                dbsn=bits[0:7],
                crc9=bits[7:16],
                data=bits[16:192],
                packet_type=data_type,
            )
        elif data_type == Rate1DataTypes.ConfirmedLastBlock:
            return Rate1Data(
                dbsn=bits[0:7],
                crc9=bits[7:16],
                data=bits[16:160],
                crc32=bits[160:192],
                packet_type=data_type,
            )
        elif data_type == Rate1DataTypes.UnconfirmedLastBlock:
            return Rate1Data(
                data=bits[0:160], crc32=bits[160:192], packet_type=data_type
            )

    def convert(self, new_type: Rate1DataTypes):
        return Rate1Data.from_bits_typed(bits=self.as_bits(), data_type=new_type)

    def as_bits(self):
        if self.packet_type == Rate1DataTypes.Unconfirmed:
            # R_1_DATA PDU content for unconfirmed data
            return bytes_to_bits(self.data)
        elif self.packet_type == Rate1DataTypes.Confirmed:
            # R_1_DATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9, endian="little")
                + bytes_to_bits(self.data)
            )
        elif self.packet_type == Rate1DataTypes.UnconfirmedLastBlock:
            # R_1_LDATA PDU content for unconfirmed data
            return bytes_to_bits(self.data) + int2ba(self.crc32, length=32)
        elif self.packet_type == Rate1DataTypes.ConfirmedLastBlock:
            # R_1_LDATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9, endian="little")
                + bytes_to_bits(self.data)
                + int2ba(self.crc32, length=32)
            )
