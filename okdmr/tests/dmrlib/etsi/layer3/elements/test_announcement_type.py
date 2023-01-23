from okdmr.dmrlib.etsi.layer3.elements.announcement_type import AnnouncementType


def test_announcement_type():
    assert AnnouncementType(0b1_1101) == AnnouncementType.Reserved
    assert AnnouncementType(0b1_1111) == AnnouncementType.ManufacturerSpecific
