import enum


@enum.unique
class AnnouncementType(enum.Enum):
    AnnounceOrWithdrawTSCC = 0x00
    """Ann_WD_TSCC"""
    SpecifyCallTimers = 0x01
    """CallTimer_Parms"""
    VoteNowAdvice = 0x02
    """Vote_Now"""
    LocalTime = 0x03
    """Local_Time"""
    BroadcastMassRegistration = 0x04
    """MassReg"""
    LogicalPhysicalChannelRelationship = 0x05
    """Chan_Freq"""
    AdjacentSiteInformation = 0x06
    """Adjacent_Site"""
    GeneralSiteParams = 0x07
    """Gen_Site_Params"""
    Reserved = 0x08
    """0b0_1000 through 0b1_1101 (incl.)"""
    ManufacturerSpecific = 0x1E
    """0b1_1110 and 0b1_1111 are for manufacturers"""

    @classmethod
    def _missing_(cls, value: int) -> "AnnouncementType":
        if AnnouncementType.Reserved.value <= value <= 0b1_1101:
            return AnnouncementType.Reserved
        if 0b1_1110 <= value <= 0b1_1111:
            return AnnouncementType.ManufacturerSpecific
        raise ValueError(f"Unknown ANnouncement Type {value}")
