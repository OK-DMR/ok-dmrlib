import enum


@enum.unique
class VoiceBursts(enum.Enum):
    """
    Utility class, not standardized in ETSI DMR TierII specs
    """

    Unknown = (1,)

    VoiceBurstA = (100,)
    VoiceBurstB = (101,)
    VoiceBurstC = (102,)
    VoiceBurstD = (103,)
    VoiceBurstE = (104,)
    VoiceBurstF = (105,)

    @classmethod
    def _missing_(cls, value: int):
        assert (
            100 <= value <= 105
        ) or value == 1, f"Unknown VoiceBurst value, got {value}"

        return VoiceBursts.Unknown
