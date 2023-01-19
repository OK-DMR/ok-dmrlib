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

    def encode(self, string: str) -> bytes:
        if self.value == TalkerAliasDataFormat.SevenBitCharacters.value:
            return string.encode("646")
        elif self.value == TalkerAliasDataFormat.UnicodeUTF16LE.value:
            return string.encode("utf-16-le")
        elif self.value == TalkerAliasDataFormat.UnicodeUTF8.value:
            return string.encode("utf8")
        elif self.value == TalkerAliasDataFormat.ISOEightBitCharacters.value:
            return string.encode("latin")

        raise NotImplementedError(
            f"TalkerAliasDataFormat.encode not implemented for {self.value}"
        )

    def decode(self, raw: bytes) -> str:
        if self.value == TalkerAliasDataFormat.SevenBitCharacters.value:
            return raw.decode("646")
        elif self.value == TalkerAliasDataFormat.UnicodeUTF16LE.value:
            return raw.decode("utf-16-le")
        elif self.value == TalkerAliasDataFormat.UnicodeUTF8.value:
            return raw.decode("utf8")
        elif self.value == TalkerAliasDataFormat.ISOEightBitCharacters.value:
            return raw.decode("latin")

        raise NotImplementedError(
            f"TalkerAliasDataFormat.decode not implemented for {self.name}"
        )

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=2)

    @staticmethod
    def from_bits(bits: bitarray) -> "TalkerAliasDataFormat":
        return TalkerAliasDataFormat(ba2int(bits[0:2]))

    @classmethod
    def _missing_(cls, value: int) -> Any:
        if not (0b00 <= value <= 0b11):
            raise ValueError(f"TalkerAliasDataFormat value out of range, got {value}")
