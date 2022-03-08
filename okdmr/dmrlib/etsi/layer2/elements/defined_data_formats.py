import enum

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class DefinedDataFormats(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.38 Defined Data Formats
    """

    Binary = 0b000000
    BCD = 0b000001
    Charset7bit = 0b000010
    CharsetISO_8859_1 = 0b000011
    CharsetISO_8859_2 = 0b000100
    CharsetISO_8859_3 = 0b000101
    CharsetISO_8859_4 = 0b000110
    CharsetISO_8859_5 = 0b000111
    CharsetISO_8859_6 = 0b001000
    CharsetISO_8859_7 = 0b001001
    CharsetISO_8859_8 = 0b001010
    CharsetISO_8859_9 = 0b001011
    CharsetISO_8859_10 = 0b001100
    CharsetISO_8859_11 = 0b001101
    CharsetISO_8859_13 = 0b001110
    CharsetISO_8859_14 = 0b001111
    CharsetISO_8859_15 = 0b010000
    CharsetISO_8859_16 = 0b010001
    CharsetUTF8 = 0b010010
    CharsetUTF16 = 0b010011
    CharsetUTF16_BE = 0b010100
    CharsetUTF16_LE = 0b010101
    CharsetUTF32 = 0b010110
    CharsetUTF32_BE = 0b010111
    CharsetUTF32_LE = 0b011000
    Reserved = 0b111111

    @classmethod
    def _missing_(cls, value: int) -> "DefinedDataFormats":
        assert (
            0b000000 <= value <= 0b111111
        ), f"DefinedDataFormats value out of range {value}"
        # all undefined values are Reserved per specification
        return DefinedDataFormats.Reserved

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=6)

    @staticmethod
    def from_bits(bits: bitarray) -> "DefinedDataFormats":
        return DefinedDataFormats(ba2int(bits[0:6]))
