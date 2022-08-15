import pytest

from okdmr.dmrlib.hytera.pdu.radio_registration_service import (
    RRSTypes,
    RRSResult,
    RRSRadioState,
)


def test_rrs_enums():
    with pytest.raises(ValueError):
        RRSTypes(0x05)
    assert RRSTypes.RadioGoingOffline.as_bytes() == b"\x01"

    with pytest.raises(ValueError):
        RRSResult(0x03)
    assert RRSResult.Success.as_bytes() == b"\x00"

    with pytest.raises(ValueError):
        RRSRadioState(0x02)
    assert RRSRadioState.Offline.as_bytes() == b"\x01"
