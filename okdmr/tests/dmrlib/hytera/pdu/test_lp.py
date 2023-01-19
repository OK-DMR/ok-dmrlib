from typing import Dict

from okdmr.dmrlib.hytera.pdu.location_protocol import LocationProtocol


def test_location_protocol():
    msgs: Dict[str, Dict[str, any]] = {
        "08a0020032000000010a2110dd0000413138333634383236313031354e343731382e383035314530313835342e34333837302e313132310b03": {},
        "08a002003200000003002337fb0000410000000000000000000000004e353030332e383737314530313432362e353330320000000000007003": {},
    }
    for msg in msgs:
        msg_bytes = bytes.fromhex(msg)
        lp = LocationProtocol.from_bytes(msg_bytes)
        if msg_bytes != lp.as_bytes():
            print(msg.lower())
            print(lp.as_bytes().hex().lower())
        assert lp.as_bytes() == msg_bytes
        assert len(repr(lp)) > 0
        print(repr(lp))
