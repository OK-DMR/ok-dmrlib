import enum


@enum.unique
class CallType(enum.Enum):
    PrivateCall = 0x00
    GroupCall = 0x01
    WakeupCall_2 = 0x02
    WakeupCall_c = 0x0C
