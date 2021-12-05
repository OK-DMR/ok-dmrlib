from enum import Enum


class CrcMasks(Enum):
    PiHeader = 0x6969
    VoiceLCHeader = 0x969696
    TerminatorWithLC = 0x999999
    CSBK = 0xA5A5
    MBCHeader = 0xAAAA
    DataHeader = 0xCCCC
    UnifiedSingleBlockData = 0x3333
    Rate12DataContinuation = 0x0F0
    Rate34DataContinuation = 0x1FF
    Rate1DataContinuation = 0x10F
    ReverseChannel = 0x7A