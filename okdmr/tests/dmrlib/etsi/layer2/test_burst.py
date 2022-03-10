import sys
from typing import List, Tuple

from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.fec.trellis import Trellis34
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync
from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup


def test_burst_info(capsys):
    bursts: List[str] = [
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d5244192807220000090028072290864b516baded847205ae0062959308849047f7d5dd57dfd9537a101efe3ed4206e153827e70139",
        # [BsSourcedData] [CC 5] [DATA TYPE CSBK] [FEC 0f2b VERIFIED]
        "444d52440223383b2338630006690f632e40c70153df0a83b7a8282c2509625014fdff57d75df5dcadde429028c87ae3341e24191c003c",
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d5244492807220000090028072290864b516beab8e5564609e61dc5eaa8e55647f7d5dd57dfd709e61dd5eaa8e5564709e73cc5013a",
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d52449128072200000900280722907cd1c462d8bac5704529d00ed0c8aac57047f7d5dd57dfd529d00fd1c8aac570452bd11fd10130",
        # [EmbeddedData] [CC 1] [DATA TYPE Reserved] [PI 0] [LCSS 3] [EMB Parity 0091 VERIFIED]
        "444d52440320baef0000090020baef8100000001b9e881526173002a6bb9e8815261303000a0391173002a6bb9e881526173002a6b3334",
    ]
    for burst_hex in bursts:
        mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(burst_hex))
        assert isinstance(mmdvm.command_data, Mmdvm2020.TypeDmrData)
        burst: Burst = Burst.from_mmdvm(mmdvm=mmdvm.command_data)
        if burst.has_emb:
            assert burst.emb.emb_parity
            assert burst.sync_or_embedded_signalling == SyncPatterns.EmbeddedSignalling
            assert burst.data_type == DataTypes.Reserved
        elif burst.has_slot_type:
            assert burst.slot_type.fec_parity_ok
            assert isinstance(burst.data_type, DataTypes)

        burst.set_sequence_no(128)
        assert burst.sequence_no == 128

        burst.set_stream_no(b"\xFF\xAA")
        assert burst.stream_no == b"\xFF\xAA"

        noprintdebug: str = repr(burst)
        assert len(noprintdebug) > 0

        printdebug: str = burst.debug(printout=True)
        assert len(printdebug) > 0
        out, err = capsys.readouterr()
        assert len(out) > 0
        assert len(err) < 1

        assert burst.as_bits().tobytes() == mmdvm.command_data.dmr_data


def test_burst_info_hytera():
    bursts: List[str] = [
        "5a5a5a5a0000000042000501020000002222eeee555533334000bd0000008000150000000800fd00230038003b0038003b00b41200447eb7ffffef0844400000fd0800003b382300",
        "5a5a5a5a0000000042000501020000002222dddd555500004000000000000000000000000000020002000000000000000000000000000000b2dd503250380c00000014000000ff01",
        "5a5a5a5a0300000041000501020000002222999911110000100038d424a26d410436c0dda2f46165307000904607a54d4715ff8e3685dd23255501e3000001000900000022072800",
        "5a5a5a5a8f00000043000501020000002222222255550000409c5e06ca0ac804e823d04aa04b9d1457ff5dd7dff52001600d7039003cc12d031c003cca0a01006f0000003c382300",
        "5a5a5a5a0000000042000501020000002222eeee11111111402800000000000000000000090028000700220068291110c8291110282a1110801d0067080901000900000022072800",
        "5a5a5a5aff00000041000501020000002222bbbb1111000040548adb76e648040a81cad1c5ba0176635063f37200816df708c868af68a235db99008e76e601000900000022072800",
        "5a5a5a5a0001000041000501020000002222cccc111100004006b83a07c49456750ece2681f6413100100000250e1c20ff8689eb34e57f442cc500f607c401000900000022072800",
        "5a5a5a5afb0000004100050102000000222277771111000040569bec50c139eee49d9eeae5fba716fd55f77d735f89eb6e689fea30a64bc52248002e50c101000900000022072800",
        "5a5a5a5ad40100004100050102000000222211111111000040f08047a3158e16287641f422596dc457ff5dd7def548310023e03c002e5124042a00fba315000075d40300a9352600",
        "5a5a5a5ad6010000410005010200000022227777111100004013e8b9528173612a00b96b81e86752fd55f77d715f00736b2ae8b9528173612a00006b5281000075d40300a9352600",
        "5a5a5a5add0100004100050102000000222288881111000040449eec52e0d60074d5ec1de09e01521032220111d9d5d61d749eec52e0d60174d5001d52e0000075d40300a9352600",
        "5a5a5a5adc0100004100050102000000222277771111000040568efd52e0d60075c5fd0de08e0752fd55f77d705fd5d61d759eec52e0d60174d5001d52e0000075d40300a9352600",
        "5a5a5a5adb01000041000501020000002222cccc111100004006dc8c16e4574cb8c4dfddc3ae417600100000260ec5f60d75aedf76c3f64675c5000d16e4000075d40300a9352600",
        "5a5a5a5ad22b00004100050102000000222244445555000040950a391d32802bb93b9221c163bd1557ff5dd7d5f52d5c5211f0218729d34aaa06006d1d3200003b38230063382300",
        "5a5a5a5a872a00004100050102000000222244445555000040910f39d932282ba139b224016ebd1557ff5dd7d5f5105c9a1132208b2d1b43aa0c006bd93200003b38230063382300",
        "5a5a5a5a862a00004100050102000000222266665555000040b02f25b5e2b622e2f2d276e5320d9657ff5dd7dcf51fe3a1ef2f2202032df2207200e2b5e20000633823003b382300",
        "5a5a5a5a852a00004100050102000000222244445555000040903b3141203d2865701a3761f6bd1557ff5dd7d5f5185cde1de0314f24db13ba15002141200000633823003b382300",
    ]
    for burst_hex in bursts:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(burst_hex)
        )
        burst: Burst = Burst.from_hytera_ipsc(ipsc=ipsc)
        # slot type matching
        if ipsc.slot_type == IpSiteConnectProtocol.SlotTypes.slot_type_sync:
            assert isinstance(burst, HyteraIPSCSync)
        elif ipsc.slot_type == IpSiteConnectProtocol.FrameTypes.frame_type_data_header:
            assert burst.data_type == DataTypes.DataHeader
        elif ipsc.slot_type == IpSiteConnectProtocol.SlotTypes.slot_type_rate_34_data:
            assert burst.data_type == DataTypes.Rate34Data
        elif ipsc.slot_type == IpSiteConnectProtocol.SlotTypes.slot_type_wakeup_request:
            assert isinstance(burst, HyteraIPSCWakeup)
        # common features
        if burst.has_emb or burst.has_slot_type:
            assert burst.colour_code == ipsc.color_code


def test_burst_as_bits():
    bursts: List[Tuple[str, BurstTypes]] = [
        (
            "51cf0ded894c0dec1ff8fcf294fdff57d75df5dcae7a16d064197982bf5824914c",
            BurstTypes.DataAndControl,
        ),
        (
            "2522222222a632b222222222560dff57d75df5dce2822222222791522222222c11",
            BurstTypes.DataAndControl,
        ),
        (
            "3a1f36af232d7afda01bd78255bdff57d75df5d55c045c2e3361260e501f863363",
            BurstTypes.DataAndControl,
        ),
        (
            "00e527076f2a4b0f03ed010115ddff57d75df5d6f145422817d6234b6e08802018",
            BurstTypes.DataAndControl,
        ),
    ]
    for (hexstr, burst_type) in bursts:
        _bytes: bytes = bytes.fromhex(hexstr)
        b: Burst = Burst.from_bytes(data=_bytes, burst_type=burst_type)
        assert (
            b.data.as_bits() == b.info_bits_deinterleaved
        ), f"Mismatch in {repr(b)} {b.as_bits().tobytes().hex()}"
        assert b.as_bits().tobytes() == _bytes, f"Mismatch in {repr(b)}"


if __name__ == "__main__":
    ks_mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(sys.argv[1]))
    assert isinstance(ks_mmdvm.command_data, Mmdvm2020.TypeDmrData)
    m_burst_info: Burst = Burst.from_mmdvm(mmdvm=ks_mmdvm.command_data)
    m_burst_info.debug(printout=True)
