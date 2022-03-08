import enum


@enum.unique
class ResynchronizeFlag(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.23 Re-Synchronize Flag (S)
    """

    DoNotSync = 0
    SyncSeqNumberWithDataHeader = 1

    @classmethod
    def _missing_(cls, value: object) -> "ResynchronizeFlag":
        raise ValueError(f"Re-Synchronize Flag (S) is not defined for value {value}")
