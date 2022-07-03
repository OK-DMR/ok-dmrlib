from typing import Dict

from okdmr.dmrlib.hytera.pdu.location_protocol import LocationProtocol
from okdmr.tests.dmrlib.tests_utils import prettyprint


def test_location_protocol():
    msgs: Dict[str, Dict[str, any]] = {
        "08a0020032000000010a2110dd0000413138333634383236313031354e343731382e383035314530313835342e34333837302e313132310b03": {}
    }
    for msg in msgs:
        msg_bytes = bytes.fromhex(msg)
        lp = LocationProtocol.from_bytes(msg_bytes)
        assert lp.as_bytes() == msg_bytes
        assert len(repr(lp)) > 0
