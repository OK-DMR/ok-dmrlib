import enum


@enum.unique
class LCSS(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.3 LC Start/Stop (LCSS)
    """

    SingleFragmentLCorCSBK = 0
    FirstFragmentLC = 1
    LastFragmentLCorCSBK = 2
    ContinuationFragmentLCorCSBK = 3
