import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class DynamicIdentifier(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.9  Dynamic Identifier (DI)
    """

    InitialUnknown = 0b00
    LeaderPreferenceLow = 0b01
    LeaderPreferenceMedium = 0b10
    LeaderPreferenceHigh = 0b11

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"DynamicIdentifier value {value} is undefined")

    def as_bits(self) -> bitarray:
        return int2ba(self.value)

    @staticmethod
    def from_bits(bits: bitarray) -> "DynamicIdentifier":
        return DynamicIdentifier(ba2int(bits[0:2]))