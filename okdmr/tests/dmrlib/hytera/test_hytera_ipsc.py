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


def test_multisite():
    msgs: List[str] = [
        "c35200502004000001000501010000001111cccc1111000040b8f29632653297a5f9d0886591215700100000210ee0b344a48ee2024c54298e23d4e3000000009a0204008d062800",
        "c35200501f04000001000501010000001111bbbb1111000040b8c7a07322128f500fb22e20f49172625000b37bc04b517a06e692166398b1effcd417000000009a0204008d062800",
        "c35200502004000001000501010000001111cccc1111000040b8f29632653297a5f9d0886591215700100000210ee0b344a48ee2024c54298e23d4e3000000009a0204008d062800",
        "c3520050210400000100050101000000111177771111000040b8f9e1e24a262f2d7dd15e2b9227d3fd55f77d785f80c2b9fea7f6f61c2c3c90a7d420000000009a0204008d062800",
        "c3520050220400000100050101000000111188881111000040b897e61f28165d9829c12a0ae801c66030a0901109a8bc40c746df22e42a041f40d43d000000009a0204008d062800",
        "c3520050230400000100050101000000111199991111000040b857ec00e51c404a33da3be161214290702201472764e6b114ae968ebfcf22d19ad4d5000000009a0204008d062800",
        "c35200502404000001000501010000001111aaaa1111000040b8a595be387fb9242de0f73dd741518071c36049f7c8a545398cd16e47e14a375cd44d000000009a0204008d062800",
        "c35200502504000001000501010000001111bbbb1111000040b8e8c06745ba1ccb8fc2fd44e90152625000b37bc0e8b9ddd9ecd67002f8156a68d47e000000009a0204008d062800",
        "c35200502604000001000501010000001111cccc1111000040b8fce67640302bd5f8e466248a51b000100000210e20ccb2dcbff09240ae6a3cb0d402000000009a0204008d062800",
        "c3520050270400000100050101000000111177771111000040b8baf0924352e4dfdbd6d727ab37a3fd55f77d745f30ddc498d8e0b46b551c6f0ed45c000000009a0204008d062800",
        "c3520050280400000100050101000000111188881111000040b8aee130a3560d1888f1adc08e21506030a09014096c8fd196feb254a5e605e7add45c000000009a0204008d062800",
    ]
    for msg in msgs:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(msg)
        )
        b: Burst = Burst.from_hytera_ipsc(ipsc=ipsc)
        print(repr(b))
        assert len(repr(b))
        # no objects serialization, so bits are equal
        assert b.full_bits == b.as_bits()


def test_rc():
    msgs: List[str] = [
        "c35200503203000001000501010000001111cccc1111000040b8efdaf48911064091ff93519401ac00809207b622a1f52e62afef70c2f76446b5b80a00000000060100007f592800"
    ]
    for msg in msgs:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(msg)
        )
        b: Burst = Burst.from_hytera_ipsc(ipsc=ipsc)
        print(repr(b))
        assert len(repr(b))
        # no objects serialization, so bits are equal
        assert b.full_bits == b.as_bits()
