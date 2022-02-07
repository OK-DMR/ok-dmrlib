import enum


@enum.unique
class BurstTypes(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 6. Layer 2 burst format (sections 6.1 and 6.2)
    """

    Undefined = (-1,)
    Vocoder = (0,)
    DataAndControl = 1
