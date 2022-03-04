import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class PositionError(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.15 Position Error
    """

    LessThan2m = 0b000
    LessThan20m = 0b001
    LessThan200m = 0b010
    LessThan2km = 0b011
    LessThan20km = 0b100
    LessThan200km = 0b101
    MoreThan200km = 0b110
    PositionErrorNotKnown = 0b111

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=3)

    @staticmethod
    def from_bits(bits: bitarray) -> "PositionError":
        return PositionError(ba2int(bits[0:3]))

    @classmethod
    def _missing_(cls, value: int) -> Any:
        raise ValueError(f"Value for PositionError out of range, got {value}")
