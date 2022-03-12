import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class FeatureSetIDs(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.5  Feature set ID (FID)
    """

    StandardizedFID = 0b00000000
    ReservedForFutureStandardization = 0b00000001
    ManufacturerFID = 0b00000100
    HyteraFID = 0b00010000
    ReservedForFutureMFID = 0b10000000

    @classmethod
    def _missing_(cls, value: int) -> Any:
        assert (
            0b00000000 <= value <= 0b11111111
        ), f"FID (Feature Set ID) value out of range, got {value}"
        if (
            FeatureSetIDs.ReservedForFutureStandardization.value
            <= value
            < FeatureSetIDs.ManufacturerFID.value
        ):
            return FeatureSetIDs.ReservedForFutureStandardization
        elif (
            FeatureSetIDs.ManufacturerFID.value
            <= value
            < FeatureSetIDs.ReservedForFutureMFID.value
        ):
            return FeatureSetIDs.ManufacturerFID
        elif FeatureSetIDs.ReservedForFutureMFID.value <= value:
            return FeatureSetIDs.ReservedForFutureMFID

    @staticmethod
    def from_bits(bits: bitarray) -> "FeatureSetIDs":
        return FeatureSetIDs(ba2int(bits[0:8]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=8)
