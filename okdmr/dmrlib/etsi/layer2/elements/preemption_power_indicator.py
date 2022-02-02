import enum


@enum.unique
class PreemptionPowerIndicator(enum.Enum):
    CarriesSameChannelOrNullEmbeddedMessage = 0
    CarriesReverseChannelInformation = 1
