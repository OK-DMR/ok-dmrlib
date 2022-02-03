import enum


@enum.unique
class PreemptionPowerIndicator(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.2 Pre-emption and power control Indicator (PI)
    """

    CarriesSameChannelOrNullEmbeddedMessage = 0
    CarriesReverseChannelInformation = 1
