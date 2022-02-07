import enum
from typing import Any


@enum.unique
class AdditionalInformationField(enum.Enum):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.6  Additional Information Field
    """

    Ignore = 0b0
    Valid = 0b1

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"AdditionalInformationField value {value} is undefined")
