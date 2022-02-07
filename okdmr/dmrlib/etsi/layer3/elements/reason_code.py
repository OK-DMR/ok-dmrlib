import enum
from typing import Any


@enum.unique
class ReasonCode(enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.3  Reason Code
    """

    MSDoesNotSupportThisFeatureOrService = 0b00100001

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"ReasonCode value {value} is undefined")
