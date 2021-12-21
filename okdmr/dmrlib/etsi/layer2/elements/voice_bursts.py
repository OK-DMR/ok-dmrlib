from enum import Enum


class VoiceBursts(Enum):
    Unknown = (1,)

    VoiceBurstA = (100,)
    VoiceBurstB = (101,)
    VoiceBurstC = (102,)
    VoiceBurstD = (103,)
    VoiceBurstE = (104,)
    VoiceBurstF = 105

    def __missing__(self, key):
        return VoiceBursts.Unknown
