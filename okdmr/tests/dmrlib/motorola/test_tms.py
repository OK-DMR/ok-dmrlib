from okdmr.dmrlib.motorola.text_messaging_service import (
    FirstHeader,
    TMSPDUType,
    TMSEncoding,
    TMSDeviceCapability,
    TextMessagingService,
)


def test_first_header():
    fh: FirstHeader = FirstHeader(
        has_more_headers=True,
        pdu_type=TMSPDUType.SERVICE_AVAILABILITY,
        is_control_message=True,
        is_acknowledged=True,
    )
    fh_bytes: bytes = fh.as_bytes()
    fh_2: FirstHeader = FirstHeader.from_bytes(fh_bytes)
    assert fh_2.as_bytes() == fh.as_bytes()
    assert fh_2.is_acknowledged
    assert fh_2.is_control_message
    assert fh_2.has_more_headers
    assert len(repr(fh_2))
    assert repr(fh_2) == repr(fh)


def test_encoding():
    assert TMSEncoding(0) == TMSEncoding.UNDEFINED
    assert TMSEncoding(0x10) == TMSEncoding.UNDEFINED
    assert TMSEncoding(0x04) == TMSEncoding.UCS2_LE


def test_capability():
    assert TMSDeviceCapability(0b00) == TMSDeviceCapability.LIMITED
    assert TMSDeviceCapability(0b01) == TMSDeviceCapability.INTERNAL
    assert TMSDeviceCapability(0b10) == TMSDeviceCapability.EXTERNAL
    assert TMSDeviceCapability(0b11) == TMSDeviceCapability.FULL


def test_availability():
    msg_bytes: bytes = bytes([0x00, 0x03, 0xD0, 0x00, 0x01])
    msg_pdu: TextMessagingService = TextMessagingService.from_bytes(msg_bytes)
    assert msg_pdu.header.pdu_type == TMSPDUType.SERVICE_AVAILABILITY
    assert msg_pdu.header.has_more_headers
    assert msg_pdu.availability_header.capability == TMSDeviceCapability.INTERNAL
    assert len(repr(msg_pdu))
    assert msg_bytes == msg_pdu.as_bytes()


def test_ack_availability():
    msg_bytes: bytes = bytes([0x00, 0x02, 0x1F, 0x00])
    msg_pdu: TextMessagingService = TextMessagingService.from_bytes(msg_bytes)
    assert msg_pdu.header.pdu_type == TMSPDUType.TMS_ACKNOWLEDGEMENT
    assert not msg_pdu.header.has_more_headers
    assert len(repr(msg_pdu))
    assert msg_bytes == msg_pdu.as_bytes()


def test_ack_message():
    msg_bytes: bytes = bytes([0x00, 0x04, 0x9F, 0x00, 0x95, 0x20])
    msg_pdu: TextMessagingService = TextMessagingService.from_bytes(msg_bytes)
    assert msg_pdu.header.pdu_type == TMSPDUType.TMS_ACKNOWLEDGEMENT
    assert msg_pdu.header.has_more_headers
    assert msg_pdu.sequence_number == 53
    assert msg_pdu.as_bytes() == msg_bytes
    assert len(repr(msg_pdu))


def test_message():
    msg_bytes: bytes = bytes(
        [
            0x00,
            0x0D,
            0xE0,
            0x01,
            0x01,
            0x95,
            0x44,
            0x61,
            0x00,
            0x68,
            0x00,
            0x6F,
            0x00,
            0x6A,
            0x00,
        ]
    )
    msg_pdu: TextMessagingService = TextMessagingService.from_bytes(msg_bytes)
    assert msg_pdu.header.pdu_type == TMSPDUType.SIMPLE_TEXT_MESSAGE
    assert msg_pdu.sequence_number == 85
    assert msg_pdu.message.decode("utf-16-le") == "ahoj"
    assert msg_pdu.as_bytes() == msg_bytes
    assert len(repr(msg_pdu))
    assert msg_pdu.address == b"\x01"
