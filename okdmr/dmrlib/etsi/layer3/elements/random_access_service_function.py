import enum


@enum.unique
class RandomAccessServiceFunction(enum.Enum):
    ALL_SERVICES = 0b00
    REGISTRATION_AND_PAYLOAD_CHANNEL = 0b01
    REGISTRATION_WITHOUT_PAYLOAD_CHANNEL = 0b10
    REGISTRATION_ONLY = 0b11
