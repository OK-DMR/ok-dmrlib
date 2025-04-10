import enum
import warnings


@enum.unique
class PacketType(enum.Enum):
    TypeA = 65
    TypeB = 66
    TerminatorWithLC = 67
    PIHeader = 1

    @classmethod
    def _missing_(cls, value):
        assert (
            isinstance(value, int) and 0x00 <= value <= 0xFF
        ), f"{value} is not an integer between 0x00 and 0xFF"
        warnings.warn(f"Hytera IPSC PacketType unknown {value}")
        return PacketType.TypeA
