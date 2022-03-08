import enum
from typing import Any


@enum.unique
class UDTOptionFlag(enum.Enum):
    OACSU = 0
    FOACSU = 1

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"UDT_Option_flag is undefined for value {value}")
