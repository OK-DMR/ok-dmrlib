import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class TalkerAliasDataFormat(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.18 Talker Alias Data Format
    """

    SevenBitCharacters = 0b00
    ISOEightBitCharacters = 0b01
    UnicodeUTF8 = 0b10
    UnicodeUTF16LE = 0b11

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=2)

    @staticmethod
    def from_bits(bits: bitarray) -> "TalkerAliasDataFormat":
        return TalkerAliasDataFormat(ba2int(bits[0:2]))

    @classmethod
    def _missing_(cls, value: int) -> Any:
        if not (0b00 <= value <= 0b11):
            raise ValueError(f"TalkerAliasDataFormat value out of range, got {value}")
