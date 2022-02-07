import enum
from typing import Any


@enum.unique
class SourceType(enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.5  Source Type
    """

    BSSourced = 0b0
    MSSourced = 0b1

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"SourceType value {value} is undefined")
