import sys
from typing import List, Tuple

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync
from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup
from okdmr.dmrlib.transmission.transmission import Transmission
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol


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
        # MMDVM TS:2 SEQ: 2 [MsSourcedData] [DataTypes.Rate12Data] [CC: 1] [RATE 1/2 DATA UNCONFIRMED] [DATA(12) 000501737311000100040a23]
        "444d5244022338630008fd0023383be76f944918117b3090722540f9233581a285ed5d7f77fd75709464602846c3022109c3050079002f",
        # MMDVM TS:2 SEQ: 1 [MsSourcedData] [DataTypes.PIHeader] [CC: 1] [PI Header] [Data(10) 211003d537d57a000009]
        "444d52440128072200000900280722a02b2d896f167b90897c009bb941434301840d5d7f77fd757d9d6b51e02230cac7011f149419002f",
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

        burst.set_stream_no(b"\xff\xaa")
        assert burst.stream_no == b"\xff\xaa"

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
        # pi header IPSC TS:2 SEQ: 2 [MsSourcedData] [DataTypes.PIHeader] [CC: 1] [PI Header] [Data(10) 211003d537d57a000009]
        "5a5a5a5a02e0000001000501020000002222222211110000405c7b168990007cb99b434101430d847f5dfd777d756b9de0513022c7ca1f0194140000630201000900000022072800",
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

        assert len(repr(burst))


def test_guess_target_radio_id():
    bursts: List[Tuple[str, int]] = [
        (
            "5a5a5a5a570300004100050102000000222233335555000040f5c545f705e8bd0c26080850b4fd9457ff5dd7dcf5e6ae3877796501781fbb1a330046f7050000fc372300fe372300",
            2308092,
        ),
        (
            "5a5a5a5a50030000410005010200000022224444555500004091613a89349c25697b03a66368bd5557ff5dd7d5f5785db87af534662b1d4a3794000989340000fc372300fe372300",
            2308092,
        ),
    ]
    for ipsc_burst, expected_id in bursts:
        ipsc: IpSiteConnectProtocol = IpSiteConnectProtocol.from_bytes(
            bytes.fromhex(ipsc_burst)
        )
        burst: Burst = Burst.from_hytera_ipsc(ipsc)
        assert burst.guess_target_radio_id() == expected_id


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
        (
            "015149880ba01b3816406c80c46d5d7f77fd757e32990118206005a02341391033",
            BurstTypes.DataAndControl,
        ),
        # this one does not match for valid reason, crc is nulled out, don't know why hytera sends voice lc header without set crc
        # (
        #    "015149880ba01b3816406c80c46d5d7f77fd757e32990118206005a02341391000",
        #    BurstTypes.DataAndControl
        # )
    ]
    for hexstr, burst_type in bursts:
        _bytes: bytes = bytes.fromhex(hexstr)
        b: Burst = Burst.from_bytes(data=_bytes, burst_type=burst_type)
        assert (
            b.data.as_bits() == b.info_bits_deinterleaved
        ), f"Mismatch in {repr(b)} {b.as_bits().tobytes().hex()}"
        assert (
            b.as_bits().tobytes() == _bytes
        ), f"Mismatch in {repr(b)} {b.as_bits().tobytes().hex()} {_bytes.hex()}"


def test_vocoder_socket():
    bursts: List[Tuple[str, VoiceBursts]] = [
        (
            "5a5a5a5a0d05000041000501020000002222777755550000401382a900c0a043ce88a4ee83f82770fd55f77d775fca2cc4aec5e043821a3162c2004200c001006f000000fc372300",
            VoiceBursts.VoiceBurstA,
        ),
        (
            "5a5a5a5a0e05000041000501020000002222888855550000405039d447807d326646b3e88005352530200230f4885a4c48c824a101825937a85a006a478001006f000000fc372300",
            VoiceBursts.VoiceBurstB,
        ),
        (
            "5a5a5a5a0f05000041000501020000002222999955550000407775dc07c518074810ef0ee74405069a600850a2164238080c2882e8cc5c3764f200ce07c501006f000000fc372300",
            VoiceBursts.VoiceBurstC,
        ),
        (
            "5a5a5a5a1005000041000501020000002222aaaa555500004033738fc8529055805a9cca706335cc0160a010a5c64bb4ca804aaf12a2d4c4c4f500aac85201006f000000fc372300",
            VoiceBursts.VoiceBurstD,
        ),
        (
            "5a5a5a5a1105000041000501020000002222bbbb55550000402194aa9ed656db622cc12234cff55331432be89bd127e946e221e84027e4ed622e00629ed601006f000000fc372300",
            VoiceBursts.VoiceBurstE,
        ),
        (
            "5a5a5a5a1205000041000501020000002222cccc55550000405303c82326d1ed005fce062125a512c10964d1cb3f5b4dea0a24ce12205dbb2a4800ea232601006f000000fc372300",
            VoiceBursts.VoiceBurstF,
        ),
    ]
    transmission: Transmission = Transmission()
    transmission.new_transmission(TransmissionTypes.VoiceTransmission)
    for hexstr, burst_type in bursts:
        b: Burst = Burst.from_hytera_ipsc(
            IpSiteConnectProtocol.from_bytes(bytes.fromhex(hexstr))
        )
        returned: Burst = transmission.process_packet(burst=b)
        assert b.voice_burst == burst_type
        assert returned.voice_burst == burst_type
        assert b.is_vocoder
    transmission.end_voice_transmission()


if __name__ == "__main__":
    ks_mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(sys.argv[1]))
    assert isinstance(ks_mmdvm.command_data, Mmdvm2020.TypeDmrData)
    m_burst_info: Burst = Burst.from_mmdvm(mmdvm=ks_mmdvm.command_data)
    m_burst_info.debug(printout=True)
