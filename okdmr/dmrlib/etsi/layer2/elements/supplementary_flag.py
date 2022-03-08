import enum


@enum.unique
class SupplementaryFlag(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.41 Supplementary Flag (SF)
    """

    ShortData = 0
    SupplementaryData = 1

    @classmethod
    def _missing_(cls, value: int) -> "SupplementaryFlag":
        raise ValueError(f"SupplementaryFlag value {value} is undefined")
