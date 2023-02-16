from typing import Dict

from okdmr.dmrlib.hytera.pdu.hrnp import HRNP, HRNPOpcodes
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RadioControlProtocol,
    RCPOpcode,
    RCPResult,
    RadioIpIdTarget,
)
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.hytera.pdu.text_message_protocol import (
    TextMessageProtocol,
    TMPService,
)
from okdmr.tests.dmrlib.tests_utils import assert_expected_attribute_values


def test_defaults():
    hrnp = HRNP()
    assert hrnp.block_number == 0x00
    assert hrnp.version == b"\x04"
    assert hrnp.header == b"\x7E"


def test_hrnp_rcp_stability():
    h = HRNP(
        opcode=HRNPOpcodes.DATA,
        data=RadioControlProtocol(
            opcode=RCPOpcode.RadioIDAndRadioIPQueryRequest,
            target=RadioIpIdTarget.RADIO_IP,
            raw_value=b"\x04\x03\x02\x01",
            result=RCPResult.Success,
        ),
    )
    assert h.as_bytes() == HRNP.from_bytes(h.as_bytes()).as_bytes()

    # checksum sometimes comes out invalid, this is to fix that
    checked: bytes = bytes.fromhex(
        "7e04000020100001001b43b502471808000700000000000000c403"
    )
    h = HRNP.from_bytes(checked)
    assert h.as_bytes() == checked

    h = HRNP(
        opcode=HRNPOpcodes.DATA,
        packet_number=1,
        data=RadioControlProtocol(
            opcode=RCPOpcode.BroadcastMessageConfigurationRequest,
        ),
    )
    assert h.as_bytes() == checked


def test_sds_stability():
    group = True
    pkt = HRNP(
        opcode=HRNPOpcodes.DATA,
        data=TextMessageProtocol(
            opcode=TMPService.GroupShortData if group else TMPService.PrivateShortData,
            source_ip=RadioIP(radio_id=1001),
            destination_ip=RadioIP(radio_id=1),
            short_data=bytes.fromhex("A0B0"),
            is_confirmed=True,
            is_reliable=True,
            request_id=1,
        ),
    )
    assert pkt.as_bytes() == HRNP.from_bytes(pkt.as_bytes()).as_bytes()


def test_hrnp_frombytes():
    hexmessages: Dict[str, Dict[str, any]] = {
        # hrnp v04 connect
        "7e0400fe20100000000c60e1": {
            "block_number": 0,
            "checksum": b"\x60\xe1",
            "checksum_correct": True,
            "data": None,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.CONNECT,
            "packet_number": 0,
            "source": 32,
            "version": b"\x04",
        },
        # hrnp v03 connect
        "7e0300fe20100000000c60e2": {
            "block_number": 0,
            "checksum": b"\x60\xe2",
            "checksum_correct": True,
            "data": None,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.CONNECT,
            "packet_number": 0,
            "source": 32,
            "version": b"\x03",
        },
        # data (hdap inside) - non standard RCP identification request
        "7e0400002010000100189b6002040005006400000001c403": {
            "block_number": 0,
            "checksum": b"\x9b\x60",
            "checksum_correct": True,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 1,
            "source": 32,
            "version": b"\x04",
        },
        "7e040000102000010019d6240204800600000f690600012903": {
            "block_number": 0,
            "checksum": b"\xd6\x24",
            "checksum_correct": True,
            "destination": 32,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 1,
            "source": 16,
            "version": b"\x04",
        },
        # accept
        "7e0400fd10200000000c70d2": {
            "block_number": 0,
            "checksum": b"\x70\xd2",
            "checksum_correct": True,
            "data": None,
            "destination": 32,
            "header": b"~",
            "opcode": HRNPOpcodes.ACCEPT,
            "packet_number": 0,
            "source": 16,
            "version": b"\x04",
        },
        # RCP data inside
        "7e030000201000000018fefe02c910050002000101014f03": {
            "block_number": 0,
            "checksum": b"\xfe\xfe",
            "checksum_correct": True,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 0,
            "source": 32,
            "version": b"\x03",
        },
        "7e0400001020000300e1c65702d482ce00000f6906000200440039002e00300030002e00300037002e003200310030002e0069004d000000410039002e00300030002e00300038002e003300300038002e0069004d0000004f004b00300044004d0052000000000000000000000000000000000000000000520044003900380035002d00300030003000300030003000300030002d003000300030003000300030002d00550031002d0030002d004600000000000000000031003200330032003000410030003300310032000000000000000000000000000f6906000000001b03": {
            "block_number": 0,
            "checksum": b"\xc6\x57",
            "checksum_correct": True,
            "destination": 32,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 3,
            "source": 16,
            "version": b"\x04",
        },
        "7e04000020100000001873890241080500006f0000007503": {
            "block_number": 0,
            "checksum": b"\x73\x89",
            "checksum_correct": True,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 0,
            "source": 32,
            "version": b"\x04",
        },
    }
    for hexmsg, expectations in hexmessages.items():
        msg_bytes = bytes.fromhex(hexmsg)
        msg = HRNP.from_bytes(msg_bytes)
        assert len(repr(msg)) > 0
        print(repr(msg))
        assert msg_bytes == msg.as_bytes(), f"{hexmsg} is not {msg.as_bytes().hex()}"
        assert_expected_attribute_values(msg, expectations)


def test_valid_checksums():
    testdata: Dict[str, bytes] = {
        "7E0400FD10200000000C70D2": b"\x70\xD2",
        "7E04001010200001000C71BE": b"\x71\xBE",
        "7e04000020100001001b43b502471808000700000000000000c403": b"\x43\xB5",
        "7E040000102000010014857A0247880100006203": b"\x85\x7A",
        "7E040000102000030019FDF9025284060000010A0003E95F03": b"\xFD\xF9",
        "7E040000102000020019E41402528406000000E90300006A03": b"\xE4\x14",
        "7E04000010200004002767790980B1001400000001000000010A000835610068006F006A000203": b"\x67\x79",
    }
    for hexmsg, expected_checksum in testdata.items():
        print("=" * 20)
        print(f"hex: {hexmsg.upper()}")

        h_bytes = bytes.fromhex(hexmsg)
        h = HRNP.from_bytes(h_bytes)
        print(repr(h))
        # (h.checksum_correct, h.checksum) = h.verify_checksum(h.checksum)

        # assert (
        #    h.checksum == expected_checksum
        # ), f"{h_bytes.hex().upper()} checksum orig {h_bytes[10:12].hex()} calculated {h.checksum.hex()}"
        # assert h.as_bytes() == h_bytes


def test_tt():
    h = HRNP(
        opcode=HRNPOpcodes.DATA,
        data=TextMessageProtocol(
            opcode=TMPService.GroupShortData,
            short_data=b"\xA0\xB0\xC0\xD0",
            is_reliable=False,
            is_confirmed=False,
            source_ip=RadioIP(1001),
            destination_ip=RadioIP(1),
            request_id=1,
        ),
    )
    print(repr(h))
    print(h.as_bytes().hex())
    assert h.as_bytes() == HRNP.from_bytes(h.as_bytes()).as_bytes()

    h = HRNP(
        opcode=HRNPOpcodes.DATA,
        data=RadioControlProtocol(
            opcode=RCPOpcode.ZoneAndChannelOperationRequest,
            raw_payload=b"\x01\x00\x00\x00\x00",
        ),
    )
    print(h.as_bytes().hex())
    assert h.as_bytes() == HRNP.from_bytes(h.as_bytes()).as_bytes(), f"unstable"

    h = HRNP.from_bytes(bytes.fromhex("7E0400FD10200000000C70D2"))
    assert h.as_bytes() == HRNP.from_bytes(h.as_bytes()).as_bytes(), f"unstable"
