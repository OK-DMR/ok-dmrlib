import enum
from typing import Union

from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class Rate12DataTypes(enum.Enum):
    Unconfirmed = 12
    Confirmed = 10
    UnconfirmedLastBlock = 8
    ConfirmedLastBlock = 6
    Undefined = 0

    @classmethod
    def _missing_(cls, value: int) -> "Rate12DataTypes":
        raise ValueError(f"Unknown Rate 1/2 DataType for data length {value}")

    @staticmethod
    def resolve(confirmed: bool, last: bool) -> "Rate12DataTypes":
        return {
            # confirmed, last data block
            (True, True): Rate12DataTypes.ConfirmedLastBlock,
            (True, False): Rate12DataTypes.Confirmed,
            (False, True): Rate12DataTypes.UnconfirmedLastBlock,
            (False, False): Rate12DataTypes.Unconfirmed,
        }.get((confirmed, last), Rate12DataTypes.Undefined)


class Rate12Data(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.7 Rate 1/2 coded packet Data (R_1_2_DATA) PDU
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.8 Rate 1/2 coded Last Data block (R_1_2_LDATA) PDU
    """

    def __init__(
        self,
        data: Union[bytes, bitarray],
        packet_type: Rate12DataTypes = Rate12DataTypes.Undefined,
        dbsn: Union[int, bitarray] = 0,
        crc9: Union[int, bitarray] = 0,
        crc32: Union[int, bytes] = 0,
    ):
        self.data: bytes = data if isinstance(data, bytes) else bits_to_bytes(data)
        self.validate_packet_type(packet_type=packet_type, data_length=len(self.data))
        self.dbsn: int = dbsn if isinstance(dbsn, int) else ba2int(dbsn)
        self.packet_type: Rate12DataTypes = Rate12DataTypes(len(self.data))
        self.crc32: int = (
            crc32 if isinstance(crc32, int) else int.from_bytes(crc32, byteorder="big")
        )

        crc9 = crc9 if isinstance(crc9, int) else ba2int(crc9)
        self.crc9: int = self.calculate_crc9() if self.is_confirmed() else crc9
        self.crc9_ok: bool = self.crc9 == crc9 if crc9 > 0 else False

    @staticmethod
    def validate_packet_type(packet_type: Rate12DataTypes, data_length: int) -> bool:
        if data_length == 0 or packet_type == Rate12DataTypes.Undefined:
            return True
        else:
            assert (
                data_length == packet_type.value
            ), f"{packet_type} data must be {packet_type.value} bytes, got {data_length} bytes"

    def is_confirmed(self) -> bool:
        return self.packet_type in (
            Rate12DataTypes.Confirmed,
            Rate12DataTypes.ConfirmedLastBlock,
        )

    def is_last_block(self) -> bool:
        return self.packet_type in (
            Rate12DataTypes.ConfirmedLastBlock,
            Rate12DataTypes.UnconfirmedLastBlock,
        )

    def calculate_crc9(self) -> int:
        return CRC9.calculate_from_parts(
            data=self.data,
            serial_number=self.dbsn,
            crc32=self.crc32,
            mask=CrcMasks.Rate12DataContinuation,
        )

    def __repr__(self) -> str:
        if self.packet_type in (Rate12DataTypes.Unconfirmed, Rate12DataTypes.Undefined):
            return f"[RATE 1/2 DATA UNCONFIRMED] [DATA(12) {self.data.hex()}]"
        elif self.packet_type == Rate12DataTypes.Confirmed:
            return (
                f"[RATE 1/2 DATA CONFIRMED] [DATA(10) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
            )
        elif self.packet_type == Rate12DataTypes.UnconfirmedLastBlock:
            return (
                f"[RATE 1/2 DATA UNCONFIRMED - LAST BLOCK] [DATA(8) {self.data.hex()}]"
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )
        elif self.packet_type == Rate12DataTypes.ConfirmedLastBlock:
            return (
                f"[RATE 1/2 DATA CONFIRMED - LAST BLOCK] [DATA(6) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )

    @staticmethod
    def from_bits(bits: bitarray) -> "Rate12Data":
        return Rate12Data.from_bits_typed(bits, Rate12DataTypes.Undefined)

    @staticmethod
    def from_bits_typed(
        bits: bitarray, data_type: Rate12DataTypes = Rate12DataTypes.Undefined
    ) -> "Rate12Data":
        assert (
            len(bits) == 96
        ), f"Rate 1/2 Data packet must be 96 bits (12 bytes) long, got {len(bits)} bits"
        if data_type in (Rate12DataTypes.Undefined, Rate12DataTypes.Unconfirmed):
            return Rate12Data(data=bits, packet_type=data_type)
        elif data_type == Rate12DataTypes.Confirmed:
            return Rate12Data(
                dbsn=bits[0:7], crc9=bits[7:16], data=bits[16:96], packet_type=data_type
            )
        elif data_type == Rate12DataTypes.ConfirmedLastBlock:
            return Rate12Data(
                dbsn=bits[0:7],
                crc9=bits[7:16],
                data=bits[16:64],
                crc32=bits[64:96],
                packet_type=data_type,
            )
        elif data_type == Rate12DataTypes.UnconfirmedLastBlock:
            return Rate12Data(data=bits[0:64], crc32=bits[64:96], packet_type=data_type)

    def convert(self, new_type: Rate12DataTypes):
        return Rate12Data.from_bits_typed(bits=self.as_bits(), data_type=new_type)

    def as_bits(self):
        if self.packet_type == Rate12DataTypes.Unconfirmed:
            # R_1_2_DATA PDU content for unconfirmed data
            return bytes_to_bits(self.data)
        elif self.packet_type == Rate12DataTypes.Confirmed:
            # R_1_2_DATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9)
                + bytes_to_bits(self.data)
            )
        elif self.packet_type == Rate12DataTypes.UnconfirmedLastBlock:
            # R_1_2_LDATA PDU content for unconfirmed data
            return bytes_to_bits(self.data) + int2ba(self.crc32, length=32)
        elif self.packet_type == Rate12DataTypes.ConfirmedLastBlock:
            # R_1_2_LDATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9)
                + bytes_to_bits(self.data)
                + int2ba(self.crc32, length=32)
            )
