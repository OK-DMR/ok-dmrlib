import enum


@enum.unique
class FullMessageFlag(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.20 Full message flag (F)
    """

    FirstTryToCompletePacket = 1
    SubsequentTry = 0

    @classmethod
    def _missing_(cls, value: object) -> "FullMessageFlag":
        raise ValueError(f"Full message flag (F) is not defined for value {value}")
