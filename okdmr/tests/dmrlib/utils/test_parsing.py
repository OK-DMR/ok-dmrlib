from typing import Optional

from kaitaistruct import KaitaiStruct
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.hytera_radio_network_protocol import HyteraRadioNetworkProtocol
from okdmr.kaitai.hytera.hytera_simple_transport_reliability_protocol import (
    HyteraSimpleTransportReliabilityProtocol,
)
from okdmr.kaitai.hytera.ip_site_connect_heartbeat import IpSiteConnectHeartbeat
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol
from okdmr.kaitai.hytera.real_time_transport_protocol import RealTimeTransportProtocol

from okdmr.dmrlib.utils.parsing import try_parse_packet


def test_parsing_detection():
    mmdvm_hex: str = (
        "444d5244952807220000090028072281bee8c299fd0dc56349160c51c39810c43211100000000e2c2173ad11a06ca3047c3104f4c0"
    )
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(mmdvm_hex))
    assert isinstance(pkt, Mmdvm2020)

    ipsc_hex: str = (
        "5a5a5a5a0c01000041000501020000002222cccc1111000040430dfd63c51649510c98c3c4101132001000002c0e732111ad6ca004a3317cf40400c063c501000900000022072800"
    )
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(ipsc_hex))
    assert isinstance(pkt, IpSiteConnectProtocol)

    ipsc_hb_hex: str = "00"
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(ipsc_hb_hex))
    assert isinstance(pkt, IpSiteConnectHeartbeat)

    ipsc_hb_hex: str = "5a5a5a5a0000000014"
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(ipsc_hb_hex))
    assert isinstance(pkt, IpSiteConnectHeartbeat)

    rttp_hex: str = (
        "900005e30001920c00000000001500030000000000000000000000007efdfe7efefcfe7d7e7e7c7dfefefefffefd7efdfe7d7eff7d7c7b7efdfffbfb7d7dfd7efeff7efbfc7e7eff7dfeff7dfe7e7efefffdfcfeffff7d7d7d7b7efffefdfefffefe7d7d7dfefaffff7e7efffefffefe7d7efeffff7e7efdfdff7e7c7c7e7efffcfffdfbff7e7dfffeff7e7e7e7efffdfefffe7effff7efefffdfbff7d7d7c7dfffefdfefffefe7c7c7dffff7d7efcff7dfdfffffefffdfe7d7cfefc"
    )
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(rttp_hex))
    assert isinstance(pkt, RealTimeTransportProtocol)

    hstrp_hex: str = "32420024000083040001869f040101"
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(hstrp_hex))
    assert isinstance(pkt, HyteraSimpleTransportReliabilityProtocol)

    hrnp_hex: str = "7e31d0100a000000140000005a5a595a00000000"
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(hrnp_hex))
    assert isinstance(pkt, HyteraRadioNetworkProtocol)

    unknown: str = "0011223344556677889900"
    pkt: Optional[KaitaiStruct] = try_parse_packet(bytes.fromhex(unknown))
    assert pkt is None

    hdap_hex: str = (
        "08a0030034000000000a2338630000413131323534303237303932314e353030332e383734364530313432362e35313932302e32323533ff1cae03"
    )
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(hdap_hex))
    assert pkt

    mmdvm_hex: str = (
        "52505443002338c84f4b314c5044202034333331303030303034333331303030303030313031302e30303030303030302e3030303030303030304e6f7768657265202020202020202020202020204d756c74692d4d6f6465205265706561746572347777772e676f6f676c652e636f2e756b202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020323031393031333120202020202020202020202020202020202020202020202020202020202020204d4d44564d5f4d4d44564d5f48535f48617420202020202020202020202020202020202020202020"
    )
    pkt: KaitaiStruct = try_parse_packet(bytes.fromhex(mmdvm_hex))
    assert isinstance(pkt, Mmdvm2020)

    usrp_hex: str = (
        "55535250000000730000000000000001000000000000000000000000000000001e00faffe2ffeeff00000c0012000c00e2ffcaffe2ff0c0048008400b400a2005a00060094ff3aff2eff4cff7cffd6ff1e00420066007e005a002a001800e2ffc4ffbeffacff9affa0ffcaff1200540084007e003600eeffbeffb2ffd6fffaff0c0012000600eefff4fffaff12003c003c001800f4ffd6ffc4ffdcff0c002a002a001e000000e2ffe8fffaff12002a001e00f4ffdcffcaffcaff00004e0084009c009c005a001200d0ff88ff58ff58ff64ff88ffd0ff240060006c0072005a0030001800eeffc4ffa6ff88ff82ffa6ffdcff12003c0054005400360018000600faffeeffe2ffe8ffe8ffeefffaff060006000c00180024001e0018000000eefff4ffeeff000018000c00faff06000600faff0c000c00faff06000000e8ffe8fffaff0c003c009000b40096004e00e2ff6aff2eff4cff7cffb8ffeeff00001200"
    )
    pkt: Optional[KaitaiStruct] = try_parse_packet(bytes.fromhex(usrp_hex))
    assert pkt is None
