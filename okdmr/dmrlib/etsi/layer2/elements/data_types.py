import enum


@enum.unique
class DataTypes(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.6 Data Type
    """

    PIHeader = 0
    VoiceLCHeader = 1
    TerminatorWithLC = 2
    CSBK = 3
    MBCHeader = 4
    MBCContinuation = 5
    DataHeader = 6
    Rate12Data = 7
    Rate34Data = 8
    Idle = 9
    Rate1Data = 10
    UnifiedSingleBlockData = 11

    # ETSI Reserved values, first one (int:12) is used as fallback for unknown bursts/data
    Reserved = 12

    @classmethod
    def _missing_(cls, value: int):
        assert (
            0b0000 <= value <= 0b1111
        ), f"DT (Data Type) value out of range, got {value}"

        if 0b1100 <= value <= 0b1111:
            return DataTypes.Reserved
