from typing import List, Tuple

from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType, HSTRPOptionType


def test_hstrp_option_byte():
    assert HSTRPPacketType.from_bytes(b"\x0f").as_bytes() == b"\x0f"
    assert HSTRPPacketType.from_bytes(b"\x20").have_options
    assert HSTRPPacketType.from_bytes(b"\x10").is_reject
    assert HSTRPPacketType.from_bytes(b"\x08").is_close
    assert HSTRPPacketType.from_bytes(b"\x04").is_connect
    assert HSTRPPacketType.from_bytes(b"\x02").is_heartbeat
    assert HSTRPPacketType.from_bytes(b"\x01").is_ack


def test_hstrp():
    # fmt:off
    hexmessages: List[Tuple[str, int, int]] = [
        # RRS registration
        ("32420020000183040001869f04010211000300040a000064bd03", 2, 9),
        # RCP call request
        ("324200000001024108050000d20400000e03", 0, 12),
        # RCP call reply
        ("32420020001383040001869f0401010241880100006803", 2, 9),
        # RCP repeater broadcast transmit status
        ("32420020000b830400066b0e0401010245b810000100040004000000fd080000fa372300c303", 2, 9),
    ]
    # fmt:on
    for hexmsg, num_of_options, len_of_options in hexmessages:
        bytemsg = bytes.fromhex(hexmsg)
        msg = HSTRP.from_bytes(bytemsg)
        print(repr(msg))
        assert len(repr(msg))
        if num_of_options > 0:
            assert len(msg.options.options) == num_of_options
            # 2 options, one payload 4 bytes (device id), second 1 byte (channel id)
            # gives (2+4 + 2+1)
            assert len(msg.options) == len_of_options
        for option_type, option_data in msg.options.options:
            if option_type == HSTRPOptionType.DeviceID:
                assert int.from_bytes(option_data, byteorder="big") in (99999, 420622)
            elif option_type == HSTRPOptionType.ChannelID:
                assert int.from_bytes(option_data, byteorder="big") in (1, 2)
        assert msg.as_bytes() == bytemsg
        if isinstance(msg.payload, HDAP):
            assert msg.payload.as_bytes().hex() in hexmsg
            print(f"payload hex {msg.payload.as_bytes().hex()}")

    # content less than necessary-minimum of HSTRP PDU
    assert HSTRP.from_bytes(b"") is None
