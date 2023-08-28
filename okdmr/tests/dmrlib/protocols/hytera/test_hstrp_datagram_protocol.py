import pytest

from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType
from okdmr.dmrlib.protocols.hytera.hstrp_datagram_protocol import HSTRPDatagramProtocol


def test_hstrpdp():
    hstrp = HSTRPDatagramProtocol(123, be_active_peer=True)
    assert hstrp.sn == 0
    hstrp.hstrp_increment_sn()
    assert hstrp.sn == 1
    assert not hstrp.hstrp_connected
    hstrp.hstrp_set_connected(True)
    assert hstrp.hstrp_connected
    hstrp.connection_lost(None)
    assert not hstrp.hstrp_connected

    # check that routines do not modify the original HSTRP object
    h: HSTRP = HSTRP(
        pkt_type=HSTRPPacketType(is_connect=True, have_options=False), sn=123
    )
    h_ack = hstrp.hstrp_send_ack(addr=("", 0), request=h)
    assert h_ack.sn == h.sn
    assert not h.pkt_type.is_ack
    assert h_ack.pkt_type.is_ack

    # check that heartbeat is correctly returned
    hb = hstrp.hstrp_send_heartbeat(addr=("", 0))
    assert isinstance(hb, HSTRP)

    # passing none to check assert
    with pytest.raises(AssertionError):
        hstrp.connection_made(None)
