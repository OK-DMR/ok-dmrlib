from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.hytera.pdu.text_message_protocol import (
    TextMessageProtocol,
    TMPResultCodes,
    TMPService,
)


def test_tmp():
    pdu_bytes: bytes = bytes.fromhex(
        "0980a10022000000010a01b2070a03640e4f004c004900560045005200200054004500530054007a03"
    )
    pdu: HDAP = HDAP.from_bytes(pdu_bytes)
    assert isinstance(pdu, TextMessageProtocol)
    assert not pdu.is_group()
    assert not pdu.has_option
    assert len(repr(pdu))
    assert pdu_bytes == pdu.as_bytes()


def test_result_codes():
    rc_bytes: bytes = b"\x0c"
    rc: TMPResultCodes = TMPResultCodes.from_bytes(rc_bytes)
    assert rc.as_bytes() == rc_bytes
    assert rc == TMPResultCodes.TX_INTERRUPTED


def test_ack():
    pdu_bytes: bytes = bytes.fromhex("0980a2000D000000010a01b2070a030000003103")
    pdu: HDAP = HDAP.from_bytes(pdu_bytes)
    assert isinstance(pdu, TextMessageProtocol)
    assert not pdu.is_group()
    assert not pdu.has_option
    assert pdu.result_code == TMPResultCodes.OK
    assert len(repr(pdu))
    assert pdu_bytes == pdu.as_bytes()


def test_ack_with_option_field():
    pdu0: TextMessageProtocol = TextMessageProtocol(
        is_reliable=False,
        is_confirmed=True,
        has_option=True,
        option_data=b"\x01\x02\x03",
        opcode=TMPService.SendPrivateMessageAck,
        source_ip=RadioIP(radio_id=196608, subnet=10),
        destination_ip=RadioIP(radio_id=111111, subnet=10),
        request_id=2,
        result_code=TMPResultCodes.OK,
    )
    pdu0_bytes: bytes = pdu0.as_bytes()
    pdu1: TextMessageProtocol = TextMessageProtocol.from_bytes(pdu0_bytes)
    assert pdu0_bytes == pdu1.as_bytes()

    pdu_bytes: bytes = bytes.fromhex(
        "09c0a200120003000000020a01b2070a03000000010203e203"
    )
    pdu: TextMessageProtocol = TextMessageProtocol.from_bytes(pdu_bytes)
    assert pdu_bytes == pdu0.as_bytes()
    assert pdu.as_bytes()
    assert isinstance(pdu, TextMessageProtocol)
    assert not pdu.is_group()
    assert pdu.has_option
    assert len(repr(pdu))
    assert len(pdu.option_data)
    assert pdu_bytes == pdu.as_bytes()
