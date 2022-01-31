import enum


@enum.unique
class TransmissionTypes(enum.Enum):
    Idle = 0
    VoiceTransmission = 1
    DataTransmission = 2
