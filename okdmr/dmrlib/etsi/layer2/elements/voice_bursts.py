import enum


@enum.unique
class VoiceBursts(enum.Enum):
    Unknown = (1,)

    VoiceBurstA = (100,)
    VoiceBurstB = (101,)
    VoiceBurstC = (102,)
    VoiceBurstD = (103,)
    VoiceBurstE = (104,)
    VoiceBurstF = 105

    @classmethod
    def _missing_(cls, key: object):
        return VoiceBursts.Unknown
