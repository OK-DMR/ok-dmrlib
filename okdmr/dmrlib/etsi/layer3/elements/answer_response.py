import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class AnswerResponse(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.2  Answer Response
    """

    Proceed = 0b00100000
    Deny = 0b00100001

    @classmethod
    def _missing_(cls, value: object) -> Any:
        # no fallback defined in standard
        raise ValueError(f"AnswerResponse value {value} is unknown")

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=8)

    @staticmethod
    def from_bits(bits: bitarray) -> "AnswerResponse":
        return AnswerResponse(ba2int(bits[0:8]))
