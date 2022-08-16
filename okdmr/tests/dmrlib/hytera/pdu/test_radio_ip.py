from typing import List, Tuple

from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP


def test_radio_ip():
    rips: List[Tuple] = [
        # rcp
        ("0800000a", "10.0.0.8", 8, "little"),
        # rrs, lp, tp, dtp
        ("0a000001", "10.0.0.1", 1, "big"),
        ("0a000050", "10.0.0.80", 80, "big"),
        ("0a2110dd", "10.33.16.221", 2167005, "big"),
    ]
    for rip_bytes, ip_str, radio_id, endian in rips:
        rip = RadioIP.from_bytes(data=bytes.fromhex(rip_bytes), endian=endian)
        assert rip.subnet == 10
        assert rip.radio_id == radio_id
        assert rip.as_ip() == ip_str
        assert len(repr(rip))

    rip = RadioIP.from_ip(ip="10.33.16.221", endian="big")
    assert rip.as_ip() == "10.33.16.221"
