import enum
import warnings


@enum.unique
class FrameType(enum.Enum):
    Data = 0x0000
    VoiceSync = 0x1111
    DataSyncOrCSBK = 0x3333
    DataHeader = 0x6666
    Voice = 0xBBBB
    Sync = 0xEEEE

    @classmethod
    def _missing_(cls, value):
        assert (
            isinstance(value, int) and 0x0000 <= value <= 0xFFFF
        ), f"{value} is not in range 0x0000 and 0xFFFF"
        warnings.warn(f"Hytera IPSC FrameType unknown {value}")
        return FrameType.Data
