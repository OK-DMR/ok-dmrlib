import enum


@enum.unique
class DataTypes(enum.Enum):
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
    Reserved13 = 13
    Reserved14 = 14
    Reserved15 = 15

    @classmethod
    def _missing_(cls, value: object):
        return DataTypes.Reserved
