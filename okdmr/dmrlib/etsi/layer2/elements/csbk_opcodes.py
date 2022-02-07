import enum


@enum.unique
class CsbkOpcodes(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.32 Control Signalling BlocK Opcode (CSBKO)
    """

    UnitToUnitVoiceServiceRequest = 0b000100
    UnitToUnitVoiceServiceAnswerResponse = 0b000101
    ChannelTimingCSBK = 0b000111
    NegativeAcknowledgementResponse = 0b100110
    BSOutboundActivation = 0b111000
    PreambleCSBK = 0b111101
