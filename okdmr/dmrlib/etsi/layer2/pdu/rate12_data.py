from typing import Union

from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class Rate12Data(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.7 Rate 1/2 coded packet Data (R_1_2_DATA) PDU
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.2.8 Rate 1/2 coded Last Data block (R_1_2_LDATA) PDU
    """

    def __init__(
        self,
        data: bytes,
        dbsn: int = 0,
        crc9: int = 0,
        crc32: Union[int, bytes] = 0,
    ):
        self.data: bytes = data
        self.dbsn: int = dbsn
        self.crc32: int = (
            crc32 if isinstance(crc32, int) else int.from_bytes(crc32, byteorder="big")
        )

        self.crc9: int = self.calculate_crc9()
        self.crc9_ok: bool = self.crc9 == crc9 if crc9 > 0 else True

    def calculate_crc9(self) -> int:
        return CRC9.calculate_from_parts(
            data=self.data,
            serial_number=self.dbsn,
            crc32=self.crc32,
            mask=CrcMasks.Rate12DataContinuation,
        )

    def __repr__(self) -> str:
        if len(self.data) == 12:
            return f"[RATE 1/2 DATA] [DATA(12) {self.data.hex()}]"
        elif len(self.data) == 10:
            return (
                f"[RATE 1/2 DATA CONFIRMED] [DATA(10) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
            )
        elif len(self.data) == 8:
            return (
                f"[RATE 1/2 DATA - LAST BLOCK UNCONFIRMED] [DATA(8) {self.data.hex()}]"
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )
        elif len(self.data) == 6:
            return (
                f"[RATE 1/2 DATA - LAST BLOCK CONFIRMED] [DATA(6) {self.data.hex()}]"
                + f" [CRC9: {self.crc9}]"
                + (" [CRC9 INVALID]" if not self.crc9_ok else "")
                + f" [CRC32 int({self.crc32}) hex({self.crc32.to_bytes(4, byteorder='big').hex()})]"
            )
        raise ValueError(f"__repr__ not implemented for data len {len(self.data)}")

    @staticmethod
    def from_bits(bits: bitarray) -> "Rate12Data":
        assert (
            len(bits) == 96
        ), f"Rate 1/2 Data packet must be 96 bits (12 bytes) long, got {len(bits)} bits"
        return Rate12Data(data=bits_to_bytes(bits))

    def as_bits(self):
        if len(self.data) == 12:
            # R_1_2_DATA PDU content for unconfirmed data
            return bytes_to_bits(self.data)
        elif len(self.data) == 10:
            # R_1_2_DATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9)
                + bytes_to_bits(self.data)
            )
        elif len(self.data) == 8:
            # R_1_2_LDATA PDU content for confirmed data
            return bytes_to_bits(self.data) + int2ba(self.crc32, length=32)
        elif len(self.data) == 6:
            # R_3_4_LDATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.calculate_crc9(), length=9)
                + bytes_to_bits(self.data)
                + int2ba(self.crc32, length=32)
            )
