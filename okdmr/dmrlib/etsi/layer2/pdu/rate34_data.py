from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class Rate34Data(BitsInterface):
    def __init__(
        self,
        data: bytes,
        dbsn: int = 0,
        crc9: int = 0,
        crc32: int = 0,
    ):
        self.data: bytes = data
        self.dbsn: int = dbsn
        self.crc9: int = crc9
        self.crc32: int = crc32

        if len(data) in (14, 12):
            # verify crc32
            pass
        if len(data) in (16, 12):
            # verify crc9
            pass

    @staticmethod
    def from_bits(bits: bitarray) -> "Rate34Data":
        assert (
            len(bits) == 144
        ), f"Rate 3/4 Data packet must be 144 bits (18 bytes) long, got {len(bits)} bits"
        return Rate34Data(data=bits_to_bytes(bits))

    def as_bits(self):
        if len(self.data) == 18:
            # R_3_4_DATA PDU content for unconfirmed data
            return bytes_to_bits(self.data)
        elif len(self.data) == 16:
            # R_3_4_DATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9)
                + bytes_to_bits(self.data)
            )
        elif len(self.data) == 14:
            # R_3_4_LDATA PDU content for unconfirmed data
            return bytes_to_bits(self.data) + int2ba(self.crc32, length=32)
        elif len(self.data) == 12:
            # R_3_4_LDATA PDU content for confirmed data
            return (
                int2ba(self.dbsn, length=7)
                + int2ba(self.crc9, length=9)
                + bytes_to_bits(self.data)
                + int2ba(self.crc32, length=32)
            )
