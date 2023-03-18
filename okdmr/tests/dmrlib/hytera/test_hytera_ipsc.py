from typing import List

from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync
from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup


def test_sync():
    msgs: List[str] = [
        "5a5a5a5a0000000042000501010000001111eeee555511114028000000000000000000006f0023003700fa00342a2c10942a2c10f42a2c10835600f0360801006f000000fa372300",
        "5a5a5a5a0000000042000501010000001111eeee5555eeee40000500000000005000000046000000410000004100000000000024000000000000b543000001006f000000fa372300",
        "5a5a5a5a0000000042000501010000001111eeee555511114028000000000000000000006f0023003700fa00342a2c10942a2c10f42a2c10835600f0360801006f000000fa372300",
    ]
    for msg in msgs:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(msg)
        )
        b: Burst = Burst.from_hytera_ipsc(ipsc=ipsc)
        assert isinstance(b, HyteraIPSCSync)
        assert len(repr(b))
        # no objects serialization, so bits are equal
        assert b.full_bits == b.as_bits()
        # no deinterleave
        assert (
            b.deinterleave(bits=b.full_bits, data_type=DataTypes.Reserved)
            == b.full_bits
        )


def test_wakeup():
    msgs: List[str] = [
        "5a5a5a5a0000000042000501010000001111dddd555500004000000000000000000000000100020002000100000000000000000000000000ffffef082a00000000000000fb372300",
        "5a5a5a5a0000000042000501020000002222dddd555500004000000000000000000000000100020002000100000000000000000000000000ffffef082a00000000000000fb372300",
        "5a5a5a5a0000000042000501010000001111dddd555500004000000000000000000000000100020002000100000000000000000000000000ffffef082a0000000000000000000000",
        "5a5a5a5a0000000042000501020000002222dddd555500004000000000000000000000000100020002000100000000000000000000000000ffffef0891d1000000000000fa372300",
    ]
    for msg in msgs:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(msg)
        )
        b: Burst = Burst.from_hytera_ipsc(ipsc=ipsc)
        assert isinstance(b, HyteraIPSCWakeup)
        assert len(repr(b))
        # no objects serialization, so bits are equal
        assert b.full_bits == b.as_bits()
        # no deinterleave
        assert (
            b.deinterleave(bits=b.full_bits, data_type=DataTypes.Reserved)
            == b.full_bits
        )
