import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class FeatureSetIDs(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.5  Feature set ID (FID)

    list of specific manufacturers: http://www.etsi.org/images/files/DMRcodes/dmrs-mfid.xls
    """

    StandardizedFID = 0x0
    ReservedForFutureStandardization = 0x01
    # first MFID
    # Flyde Micro Ltd.	UK
    FlydeMicroLtd = 0x04
    # PROD-EL SPA	Italy
    ProdElSpa = 0x05
    # Trident Datacom DBA Trident Micro Systems	USA
    TridentMicroSystems = 0x06
    # RADIODATA GmbH Germany
    RadiodataGmbh = 0x07
    # HYT science tech 	China
    HytScienceTech = 0x08
    # ASELSAN Elektronik Sanayi ve Ticaret A.S.	TURKEY
    AselsanElektronik = 0x09
    # Kirisun Communications Co. Ltd	China
    KirisunCommunications = 0x0A
    # DMR Association Ltd.	UK
    DmrAssociationLtd = 0x0B
    # Motorola Ltd.	UK
    MotorolaLtd = 0x10
    # EMC S.p.A. (Electronic Marketing Company)	Italy
    ElectronicMarketingCompany = 0x13
    # EMC S.p.A. (Electronic Marketing Company)	Italy
    ElectronicMarketingCompany2 = 0x1C
    # JVCKENWOOD Corporation 	Japan
    JvcKenwood = 0x20
    # Radio Activity Srl	Italy
    RadioActivity = 0x33
    # Radio Activity Srl	Italy
    RadioActivity2 = 0x3C
    # Tait Electronics Ltd	New Zealand
    TaitElectronicsLtd = 0x58
    # HYT science tech 	China
    HytScienceTech2 = 0x68
    # Vertex Standard	Uk
    VertexStandard = 0x77
    ReservedForFutureMFID = 0x80

    @classmethod
    def _missing_(cls, value: int) -> Any:
        assert (
            0x00 <= value <= 0xFF
        ), f"FID (Feature Set ID) value out of range, got {value}"
        if (
            FeatureSetIDs.ReservedForFutureStandardization.value
            <= value
            < FeatureSetIDs.FlydeMicroLtd.value
        ):
            return FeatureSetIDs.ReservedForFutureStandardization
        elif (
            FeatureSetIDs.FlydeMicroLtd.value
            <= value
            < FeatureSetIDs.ReservedForFutureMFID.value
        ):
            return FeatureSetIDs.FlydeMicroLtd
        elif FeatureSetIDs.ReservedForFutureMFID.value <= value:
            return FeatureSetIDs.ReservedForFutureMFID

    @staticmethod
    def from_bits(bits: bitarray) -> "FeatureSetIDs":
        return FeatureSetIDs(ba2int(bits[0:8]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=8)
