from enum import Enum


class DataTypes(Enum):
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
    Reserved = 12

    def __missing__(self, key):
        return DataTypes.Reserved
