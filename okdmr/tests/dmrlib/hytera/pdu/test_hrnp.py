from typing import Dict

from okdmr.dmrlib.hytera.pdu.hrnp import HRNP, HRNPOpcodes
from okdmr.tests.dmrlib.tests_utils import assert_expected_attribute_values


def test_defaults():
    hrnp = HRNP()
    assert hrnp.block_number == 0x00
    assert hrnp.version == b"\x04"
    assert hrnp.header == b"\x7E"


def test_hrnp_frombytes():
    hexmessages: Dict[str, Dict[str, any]] = {
        # hrnp connect
        "7e0400fe20100000000c60e1": {
            "block_number": 0,
            "checksum": b"`\xe1",
            "checksum_correct": True,
            "data": None,
            "destination": 16,
            "header": b"~",
            "opcode": HRNPOpcodes.CONNECT,
            "packet_number": 0,
            "source": 32,
            "version": b"\x04",
        },
        "7e0300fe20100000000c60e2": {
            "block_number": 0,
            "checksum": b"`\xe2",
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
            "checksum": b"\xd6$",
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
            "checksum": b"p\xd2",
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
            "checksum": b"\xc6g",
            "checksum_correct": False,
            "destination": 32,
            "header": b"~",
            "opcode": HRNPOpcodes.DATA,
            "packet_number": 3,
            "source": 16,
            "version": b"\x04",
        },
        "7E04000020100000001873890241080500006F0000007503": {
            "block_number": 0,
            "checksum": b"s\x89",
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
        if (
            "checksum_correct" not in expectations
            or expectations["checksum_correct"] is True
        ):
            assert msg_bytes == msg.as_bytes()
        assert_expected_attribute_values(msg, expectations)
        assert len(repr(msg)) > 0
