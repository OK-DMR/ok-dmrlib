import enum


@enum.unique
class SlotType(enum.Enum):
    PrivacyIndicator = 0x0000
    VoiceLCHeader = 0x1111
    TerminatorWithLC = 0x2222
    CSBK = 0x3333
    DataHeader = 0x4444
    Rate12Data = 0x5555
    Rate34Data = 0x6666
    VoiceFrameA = 0x7777
    VoiceFrameB = 0x8888
    VoiceFrameC = 0x9999
    VoiceFrameD = 0xAAAA
    VoiceFrameE = 0xBBBB
    VoiceFrameF = 0xCCCC
    Wakeup = 0xDDDD
    VoiceOrDataSync = 0xEEEE
    Undefined = 0xFFFF

    @staticmethod
    def is_vocoder(s: "SlotType") -> bool:
        return s in [
            SlotType.PrivacyIndicator,
            SlotType.VoiceLCHeader,
            SlotType.VoiceFrameA,
            SlotType.VoiceFrameB,
            SlotType.VoiceFrameC,
            SlotType.VoiceFrameD,
            SlotType.VoiceFrameE,
            SlotType.VoiceFrameF,
        ]
