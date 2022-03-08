import enum
from typing import Any


@enum.unique
class SARQ(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.37 Selective Automatic Repeat reQuest (SARQ)
    """

    NotRequired = 0
    Required = 1

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"SARQ undefined for value {value}")
