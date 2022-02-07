import enum


@enum.unique
class AccessTypes(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.8  Access Type (AT)
    """

    InboundChannelIdle = 0
    InboundChannelBusy = 1
