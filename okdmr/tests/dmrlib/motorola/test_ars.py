from okdmr.dmrlib.motorola.automatic_registration_service import (
    AutomaticRegistrationService,
    ARSPDUType,
    RegistrationRequestHeader,
    FailureReason,
    ResponseSecondHeader,
)


def test_ars_device_reg():
    msg_bytes: bytes = bytes.fromhex("0007F0200231310000")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert msg_pdu.header.pdu_type == ARSPDUType.DEVICE_REGISTRATION_REQUEST
    assert msg_pdu.header.is_priority
    assert msg_pdu.header.is_acknowledged
    assert msg_pdu.header.is_control_message
    assert msg_pdu.header.has_more_headers
    assert msg_pdu.as_bytes() == msg_bytes
    assert len(msg_pdu) == len(msg_bytes)
    assert len(repr(msg_pdu))


def test_ars_device_dereg():
    msg_bytes: bytes = bytes.fromhex("000131")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert len(msg_pdu) == len(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes


def test_ars_device_user_registration():
    msg_bytes: bytes = bytes.fromhex("0010F5000231310939393939393939393900")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert msg_pdu.header.has_more_headers
    assert isinstance(msg_pdu.registration_request_header, RegistrationRequestHeader)


def test_ars_response():
    msg_bytes: bytes = bytes.fromhex("0002BF01")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert msg_pdu.header.pdu_type == ARSPDUType.ARS_DEVICE_OR_QUERY_RESPONSE
    assert msg_pdu.header.is_priority
    assert msg_pdu.header.is_control_message
    # for response, is_acknowledged=0 means successfull response
    assert not msg_pdu.header.is_acknowledged
    assert msg_pdu.header.has_more_headers
    # this particular message has 30 minutes session refresh time
    assert msg_pdu.response_second_header.refresh_time == 1
    assert len(msg_pdu) == len(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes
    assert len(repr(msg_pdu))


def test_su_query():
    msg_bytes: bytes = bytes.fromhex("000174")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert msg_pdu.header.is_priority
    assert msg_pdu.header.is_acknowledged
    assert msg_pdu.header.is_control_message
    assert not msg_pdu.header.has_more_headers
    assert len(msg_pdu) == len(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes


def test_su_query_response():
    msg_bytes: bytes = bytes.fromhex("00013F")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert isinstance(msg_pdu, AutomaticRegistrationService)
    assert msg_pdu.header.is_priority
    assert msg_pdu.header.is_control_message
    # meaning the response indicates SUCCESS
    assert not msg_pdu.header.is_acknowledged
    assert not msg_pdu.header.has_more_headers
    assert len(repr(msg_pdu))
    assert len(msg_pdu) == len(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes


def test_failure_reason_transmission_failure():
    assert FailureReason(0x01) == FailureReason.USER_ID_NOT_VALID
    assert FailureReason(0x02) == FailureReason.USER_VALIDATION_TIMEOUT
    assert FailureReason(0x00) == FailureReason.DEVICE_NOT_AUTHORIZED
    assert FailureReason(0x03) == FailureReason.TRANSMISSION_FAILURE


def test_response_second_header_failure():
    rsh: ResponseSecondHeader = ResponseSecondHeader.from_bytes(b"\x00")
    assert rsh.as_bytes() == b"\x00"


def test_csbk_ars():
    msg_bytes: bytes = bytes.fromhex("00033F1080")
    msg_pdu: AutomaticRegistrationService = AutomaticRegistrationService.from_bytes(
        msg_bytes
    )
    assert msg_pdu.is_csbk_ars
    assert len(msg_pdu) == len(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes
    assert len(repr(msg_pdu))
