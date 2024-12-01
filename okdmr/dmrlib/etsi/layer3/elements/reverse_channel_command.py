import enum

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class ReverseChannelCommand(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-4 V1.10.1 (2019-08) - 6.4.14.1 Reverse Channel
        Table 6.31: MS Reverse Channel information elements for Power Control and Transmitter Control
    """

    IncreasePowerOneStep = 0
    DecreasePowerOneStep = 1
    SetPowerToHighest = 2
    SetPowerToLowest = 3
    CeaseTransmissionCommand = 4
    CeaseTransmissionRequest = 5
    # range 0110 - 1111 is reserved
    Reserved = 0b1111

    @staticmethod
    def from_bits(bits: bitarray) -> "ReverseChannelCommand":
        return ReverseChannelCommand(ba2int(bits[0:4]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, 4)

    @classmethod
    def _missing_(cls, value: int) -> "ReverseChannelCommand":
        print(f"Cannot find RC Command value {value}")
        return ReverseChannelCommand.Reserved
