import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class SLCOs(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - B.3    Short LC (Link Control) Opcode
    ETSI TS 102 361-4 V1.10.1 (2019-08) - B.2   Short Link Control Opcode List
    """

    NullMessage = 0b0000
    ActivityUpdate = 0b0001
    ControlChannelSystemParams = 0b0010
    PayloadChannelSystemParams = 0b0011

    Reserved = 0b0100
    ManufacturerSelectable = 0b1100

    @classmethod
    def _missing_(cls, value: int) -> Any:
        assert 0b0000 <= value <= 0b1111, f"SLCO value out of range, got {value}"

        if 0b0100 <= value <= 0b1011:
            return SLCOs.Reserved
        elif 0b1100 <= value <= 0b1111:
            return SLCOs.ManufacturerSelectable

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)

    @staticmethod
    def from_bits(bits: bitarray) -> "SLCOs":
        assert len(bits) == 4, f"SLCO is exactly bits long, got {len(bits)} bits"
        return SLCOs(ba2int(bits[:4]))
