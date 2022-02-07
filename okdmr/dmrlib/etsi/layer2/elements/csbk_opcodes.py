import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class CsbkOpcodes(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.32 Control Signalling BlocK Opcode (CSBKO)
    """

    UnitToUnitVoiceServiceRequest = 0b000100
    UnitToUnitVoiceServiceAnswerResponse = 0b000101
    ChannelTimingCSBK = 0b000111
    NegativeAcknowledgementResponse = 0b100110
    BSOutboundActivation = 0b111000
    PreambleCSBK = 0b111101

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"CSBKO value {value} is undefined")

    def as_bits(self) -> bitarray:
        return int2ba(self.value)

    @staticmethod
    def from_bits(bits: bitarray) -> "CsbkOpcodes":
        return CsbkOpcodes(ba2int(bits))
