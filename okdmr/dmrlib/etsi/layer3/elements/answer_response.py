import enum
from typing import Any


@enum.unique
class AnswerResponse(enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.2  Answer Response
    """

    Proceed = 0b00100000
    Deny = 0b00100001

    @classmethod
    def _missing_(cls, value: object) -> Any:
        # no fallback defined in standard
        raise ValueError(f"AnswerResponse value {value} is unknown")
