from typing import List

from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType


def test_hstrp_option_byte():
    assert HSTRPPacketType.from_bytes(b"\x0F").as_bytes() == b"\x0F"
    assert HSTRPPacketType.from_bytes(b"\x20").is_option
    assert HSTRPPacketType.from_bytes(b"\x10").is_reject
    assert HSTRPPacketType.from_bytes(b"\x08").is_close
    assert HSTRPPacketType.from_bytes(b"\x04").is_connect
    assert HSTRPPacketType.from_bytes(b"\x02").is_heartbeat
    assert HSTRPPacketType.from_bytes(b"\x01").is_ack


def test_hstrp():
    hexmessages: List[str] = [
        # RRS registration
        "32420020000183040001869f04010211000300040a000064bd03",
    ]
    for hexmsg in hexmessages:
        bytemsg = bytes.fromhex(hexmsg)
        msg = HSTRP.from_bytes(bytemsg)
        assert len(msg.options.options) == 2
        # 2 options, one payload 4 bytes (device id), second 1 byte (channel id)
        # gives (2+4 + 2+1)
        assert len(msg.options) == 9
        assert msg.as_bytes() == bytemsg

    # content less than necessary minimum of HSTRP PDU
    assert HSTRP.from_bytes(b"") is None
