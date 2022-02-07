import enum
from typing import Any


@enum.unique
class ChannelTimingOpcode(enum.Enum):
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
