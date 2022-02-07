import enum


@enum.unique
class FLCOs(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.11 Full Link Control Opcode (FLCO)
    ETSI TS 102 361-2 V2.4.1 (2017-10) - B.1    Full Link Control Opcode List
    ETSI TS 102 361-3 V1.3.1 (2017-10) - B.1    PDP Full Link Control Opcode list
    """

    GroupVoiceChannelUser = 0b000000
    """
    koment pod
    """
    UnitToUnitVoiceChannelUser = 0b000011
    TalkerAliasHeader = 0b000100
    TalkerAliasBlock1 = 0b000101
    TalkerAliasBlock2 = 0b000110
    TalkerAliasBlock3 = 0b000111
    GPSInfo = 0b001000
    TerminatorDataLinkControl = 0b110000
