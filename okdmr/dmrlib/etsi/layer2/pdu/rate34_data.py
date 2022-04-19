import enum
from typing import Union

from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class Rate34DataTypes(enum.Enum):
    Undefined = 0
    Unconfirmed = 18
    Confirmed = 16
    UnconfirmedLastBlock = 14
    ConfirmedLastBlock = 12

    @classmethod
    def _missing_(cls, value: int) -> "Rate34DataTypes":
        raise ValueError(f"Unknown Rate 3/4 DataType for data length {value}")

    @staticmethod
    def resolve(confirmed: bool, last: bool) -> "Rate34DataTypes":
        return {
            # confirmed, last data block
            (True, True): Rate34DataTypes.ConfirmedLastBlock,
            (True, False): Rate34DataTypes.Confirmed,
            (False, True): Rate34DataTypes.UnconfirmedLastBlock,
            (False, False): Rate34DataTypes.Unconfirmed,
        }.get((confirmed, last), Rate34DataTypes.Undefined)


class Rate34Data(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.2 Rate ¾ coded packet Data (R_3_4_DATA) PDU
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.3 Rate ¾ coded Last Data block (R_3_4_LDATA) PDU
    """

    def __init__(
        self,
        data: Union[bytes, bitarray],
        packet_type: Rate34DataTypes = Rate34DataTypes.Undefined,
        dbsn: Union[int, bitarray] = 0,
        crc9: Union[int, bitarray] = 0,
        crc32: Union[int, bytes] = 0,
    ):
        self.data: bytes = data if isinstance(data, bytes) else bits_to_bytes(data)
        self.validate_packet_type(packet_type=packet_type, data_length=len(self.data))
        self.dbsn: int = dbsn if isinstance(dbsn, int) else ba2int(dbsn)
        self.packet_type: Rate34DataTypes = Rate34DataTypes(len(self.data))
        self.crc32: int = (
            crc32 if isinstance(crc32, int) else int.from_bytes(crc32, byteorder="big")
        )

        self.crc9: int = self.calculate_crc9()
        crc9 = crc9 if isinstance(crc9, int) else ba2int(crc9)
        self.crc9_ok: bool = self.crc9 == crc9 if crc9 > 0 else False

    def calculate_crc9(self) -> int:
        return CRC9.calculate_from_parts(
            data=self.data,
            serial_number=self.dbsn,
            crc32=self.crc32,
            mask=CrcMasks.Rate34DataContinuation,
        )

    def __repr__(self) -> str:
        if self.packet_type in (Rate34DataTypes.Unconfirmed, Rate34DataTypes.Undefined):
            return f"[RATE 3/4 DATA UNCONFIRMED] [DATA(18) {self.data.hex()}]"
        elif self.packet_type == Rate34DataTypes.Confirmed:
            return (
                f"[RATE 3/4 DATA CONFIRMED] [DATA(16) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
            )
        elif self.packet_type == Rate34DataTypes.UnconfirmedLastBlock:
            return (
                f"[RATE 3/4 DATA UNCONFIRMED - LAST BLOCK] [DATA(14) {self.data.hex()}]"
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )
        elif self.packet_type == Rate34DataTypes.ConfirmedLastBlock:
            return (
                f"[RATE 3/4 DATA CONFIRMED - LAST BLOCK] [DATA(12) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )

    @staticmethod
    def validate_packet_type(packet_type: Rate34DataTypes, data_length: int) -> bool:
        if data_length == 0 or packet_type == Rate34DataTypes.Undefined:
            return True
        else:
            assert (
                data_length == packet_type.value
            ), f"{packet_type} data must be {packet_type.value} bytes, got {data_length} bytes"

    @staticmethod
    def from_bits(bits: bitarray) -> "Rate34Data":
        return Rate34Data.from_bits_typed(bits, Rate34DataTypes.Undefined)

    @staticmethod
    def from_bits_typed(
        bits: bitarray, data_type: Rate34DataTypes = Rate34DataTypes.Undefined
    ) -> "Rate34Data":
        assert (
            len(bits) == 144
        ), f"Rate 3/4 Data packet must be 144 bits (18 bytes) long, got {len(bits)} bits"
        if data_type in (Rate34DataTypes.Undefined, Rate34DataTypes.Unconfirmed):
            return Rate34Data(data=bits, packet_type=data_type)
        elif data_type == Rate34DataTypes.Confirmed:
            return Rate34Data(
                dbsn=bits[0:7],
                crc9=bits[7:16],
                data=bits[16:144],
                packet_type=data_type,
            )
        elif data_type == Rate34DataTypes.ConfirmedLastBlock:
            return Rate34Data(
                dbsn=bits[0:7],
                crc9=bits[7:16],
                data=bits[16:112],
                crc32=bits[112:144],
                packet_type=data_type,
            )
        elif data_type == Rate34DataTypes.UnconfirmedLastBlock:
            return Rate34Data(
                data=bits[0:112], crc32=bits[112:144], packet_type=data_type
            )

    def convert(self, new_type: Rate34DataTypes):
        return Rate34Data.from_bits_typed(bits=self.as_bits(), data_type=new_type)

    def is_confirmed(self) -> bool:
        return self.packet_type in (
            Rate34DataTypes.Confirmed,
            Rate34DataTypes.ConfirmedLastBlock,
        )

    def is_last_block(self) -> bool:
        return self.packet_type in (
            Rate34DataTypes.ConfirmedLastBlock,
            Rate34DataTypes.UnconfirmedLastBlock,
        )

    def as_bits(self):
        if self.packet_type == Rate34DataTypes.Unconfirmed:
            # R_3_4_DATA PDU content for unconfirmed data
            return bytes_to_bits(self.data)
        elif self.packet_type == Rate34DataTypes.Confirmed:
            # R_3_4_DATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9, endian="little")
                + bytes_to_bits(self.data)
            )
        elif self.packet_type == Rate34DataTypes.UnconfirmedLastBlock:
            # R_3_4_LDATA PDU content for unconfirmed data
            return bytes_to_bits(self.data) + int2ba(self.crc32, length=32)
        elif self.packet_type == Rate34DataTypes.ConfirmedLastBlock:
            # R_3_4_LDATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9, endian="little")
                + bytes_to_bits(self.data)
                + int2ba(self.crc32, length=32)
            )
