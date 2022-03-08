import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class ChannelTimingOpcode(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.11 Channel Timing Opcode (CTO)
    """

    UnalignedRequest = 0b00
    UnalignedTerminator = 0b01
    AlignedChannelTimingStatus = 0b10
    AlignedChannelTimingPush = 0b11

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"CTO (Channel Timing Opcode) value {value} is undefined")

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=2)

    @staticmethod
    def from_bits(bits: bitarray) -> "ChannelTimingOpcode":
        assert len(bits) >= 2, f"Need at least 2 bits for ChannelTimingOpcode"
        return ChannelTimingOpcode(ba2int(bits[0:2]))
