import enum

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class ActivityID(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.1.3.2 Activity Update (simplified)
    """

    NoActivity = 0b0000
    Reserved = 0b0001
    GroupCSBK = 0b0010
    IndividualCSBK = 0b0011
    # 0b0100 - 0b0111 Reserved
    GroupVoice = 0b1000
    IndividualVoice = 0b1001
    IndividualData = 0b1010
    GroupData = 0b1011
    EmergencyGroupVoice = 0b1100
    EmergencyIndividualVoice = 0b1101

    # 0b1110 - 0b1111 Reserved

    @classmethod
    def _missing_(cls, value: int) -> "ActivityID":
        if 0b0100 <= value <= 0b0111 or 0b1110 <= value <= 0b1111:
            return ActivityID.Reserved

        raise ValueError(f"Unknown ActivityID for value {value}")

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)

    @staticmethod
    def from_bits(bits: bitarray) -> "ActivityID":
        assert (
            len(bits) >= 4
        ), f"ActivityID cannot be constructed from {len(bits)}, min. is 4 bits"
        return ActivityID(ba2int(bits[:4]))
