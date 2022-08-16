from typing import List, Tuple

import pytest

from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP


@pytest.mark.skip
def test_radio_ip():
    rips: List[Tuple] = [
        # rrs, lp, tp, dtp
        ("0a000001", "10.0.0.1", 1, "big"),
        ("0a000050", "10.0.0.80", 80, "big"),
        ("0a2110dd", "10", 10, "big"),
        # rcp
        ("0800000a", "10.0.0.8", 8, "little"),
    ]
    for rip_bytes, ip_str, radio_id, endian in rips:
        rip = RadioIP.from_bytes(data=bytes.fromhex(rip_bytes), endian=endian)
        assert rip.subnet == 10
        assert rip.radio_id == radio_id
        assert rip.as_ip() == ip_str
