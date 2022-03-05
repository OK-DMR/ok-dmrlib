from okdmr.dmrlib.etsi.layer3.elements.activity_id import ActivityID


def test_activity_id():
    assert ActivityID(0b1110) == ActivityID.Reserved
