import pytest
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP

from okdmr.dmrlib.hytera.pdu.radio_registration_service import (
    RRSTypes,
    RRSResult,
    RRSRadioState,
    RadioRegistrationService,
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


def test_rrs_answer():
    rrs_bytes = b"\x91\x00\x80\x00\t\n\x00\x00P\x00\x00\x00\x0e\x101\x03"
    rrs = RadioRegistrationService(
        opcode=RRSTypes.RadioRegistrationAnswer,
        is_reliable=True,
        radio_ip=RadioIP.from_ip("10.0.0.80"),
        result=RRSResult.Success,
        renew_time_seconds=3600,
    )
    assert RadioRegistrationService.from_bytes(rrs_bytes).as_bytes() == rrs_bytes
    assert rrs.as_bytes() == rrs_bytes
    assert len(repr(rrs))


def test_rrs_status_check_request():
    rrs_bytes = b"\x91\x00\x02\x00\x04\n\x00\x00\x14\x0e\x03"
    rrs = RadioRegistrationService(
        opcode=RRSTypes.RegistrationStatusCheckRequest,
        is_reliable=True,
        radio_ip=RadioIP.from_ip("10.0.0.20"),
    )
    assert RadioRegistrationService.from_bytes(rrs_bytes).as_bytes() == rrs_bytes
    assert rrs.as_bytes() == rrs_bytes
    assert len(repr(rrs))


def test_rrs_status_check_answer():
    rrs_bytes = b"\x11\x00\x82\x00\x05\n\x00\x00!\x00\x80\x03"
    rrs = RadioRegistrationService(
        opcode=RRSTypes.RegistrationStatusCheckAnswer,
        radio_ip=RadioIP.from_ip("10.0.0.33"),
        radio_state=RRSRadioState.Online,
    )
    assert RadioRegistrationService.from_bytes(rrs_bytes).as_bytes() == rrs_bytes
    assert rrs.as_bytes() == rrs_bytes
    assert len(repr(rrs))
