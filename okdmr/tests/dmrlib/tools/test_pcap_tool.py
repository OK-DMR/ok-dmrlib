import os
import tempfile
from argparse import ArgumentParser
from typing import Tuple, List, Optional

from _pytest.capture import CaptureFixture
from scapy.layers.inet import IP

from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.tools.pcap_tool import PcapTool, EmbeddedExtractor


class PcapCounterHelper:
    def __init__(self):
        self.counter: int = 0

    def packet_callback(self, data, packet):
        self.counter += 1


def test_pcap_tool(capsys: CaptureFixture):
    # following is pcapng containing one packet on each of ports 50.000, 50.001, 50.002 and 162
    pcapng_data = (
        "0a0d0d0ac80000004d3c2b1a01000000ffffffffffffffff02003700496e"
        "74656c28522920436f726528544d292069352d3634343048512043505520"
        "4020322e363047487a20287769746820535345342e32290003001a004c69"
        "6e757820352e31352e302d302e62706f2e322d616d643634000004004500"
        "44756d70636170202857697265736861726b2920332e342e313020284769"
        "742076332e342e3130207061636b6167656420617320332e342e31302d30"
        "2b646562313175312900000000000000c800000001000000500000000100"
        "00000000040002000900656e703073333166360000000900010009000000"
        "0c001a004c696e757820352e31352e302d302e62706f2e322d616d643634"
        "000000000000500000000600000060000000000000008109d4165d258961"
        "3e0000003e0000006469bc2134cd6469bc0429a6080045b8003001514000"
        "40118b47c0a81612c0a8160ac350c350001ceab398e329100a0000001400"
        "00000000010000000000000060000000060000005c000000000000008109"
        "d41641808b613c0000003c0000006469bc2134cd6469bc0429a6080045b8"
        "001d0152400040118b59c0a81612c0a8160ac351c3510009cbcb00000000"
        "00000000000000000000000000005c000000060000005c00000000000000"
        "8109d416973996613c0000003c0000006469bc2134cd6469bc0429a60800"
        "45b8001d0153400040118b58c0a81612c0a8160ac352c3520009cbc90000"
        "000000000000000000000000000000005c00000006000000cc0000000000"
        "00008109d41607ae4da1a9000000a9000000f8cab82bb45f6469bc2134cd"
        "08004500009b00250000ff110dc5c0a8160ac0a8160d00a200a200874a4c"
        "307d02010004407075626c69630000000000000000000000000000000000"
        "000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000a436060e2b0601040182ba6901020101020040"
        "04c0a8160a02010602010143010030153013060e2b0601040182ba690102"
        "01010200020100000000cc000000050000006c0000000000000015d80500"
        "d13f104301001c00436f756e746572732070726f76696465642062792064"
        "756d706361700200080012d80500435666ba0300080015d805002f3f1043"
        "04000800ebab060000000000050008000000000000000000000000006c00"
        "0000"
    )
    # convert bytes above to file that can be supplied to PcapTool
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    try:
        tmpfile.write(bytes.fromhex(pcapng_data))
        tmpfile.flush()
        tmpfile.close()

        stats = PcapTool.iter_pcap(files=[tmpfile.name], callback=None)
        # stats contain both count of incoming and outgoing ports
        assert stats.get(50000) == 2
        assert stats.get(50001) == 2
        assert stats.get(162) == 2

        PcapTool.print_pcap(
            files=[tmpfile.name],
            print_statistics=False,
            callback=PcapTool.void_packet_callback,
        )
        # assert no statistics were printed
        assert capsys.readouterr().out == ""

        PcapTool.print_pcap(files=[tmpfile.name])
        # packets and statistics were printed out
        assert len(capsys.readouterr().out) > 0

        helper = PcapCounterHelper()
        PcapTool.iter_pcap(files=[tmpfile.name], callback=helper.packet_callback)
        # 4 by-default whitelisted packets
        assert helper.counter == 4
        helper.counter = 0

        PcapTool.iter_pcap(
            files=[tmpfile.name],
            ports_blacklist=[50001, 50002, 162],
            callback=helper.packet_callback,
        )
        # there should be single packet on udp.port == 50.000 that is now whitelisted
        assert helper.counter == 1
        helper.counter = 0

        PcapTool.iter_pcap(
            files=[tmpfile.name],
            ports_blacklist=[],
            ports_whitelist=[50001, 50002],
            callback=helper.packet_callback,
        )
        # only two packets should be now whitelisted
        assert helper.counter == 2

        stats = PcapTool.main(["-q", "-e", tmpfile.name], return_stats=True)
        assert len(stats) == 4

        # this will test that providing no arguments, will gather arguments from sys.argv and fail
        try:
            PcapTool.main()
        except BaseException as e:
            assert isinstance(e, SystemExit)
            # clear captured
            captured = capsys.readouterr()
            assert len(captured.err)
            assert not len(captured.out)
    finally:
        tmpfile.close()
        os.unlink(tmpfile.name)


def test_pcap_tool_main():
    assert isinstance(PcapTool._arguments(), ArgumentParser)


def test_embedded_extractor(capsys: CaptureFixture):
    # fmt:off
    # @formatter:off
    # expect FullLinkControl returned (and printed to stdout as well), dmr packet byte data as hex, ip packet byte data as hex
    testdata: List[Tuple[bool, str, str]] = [
        (False, "444d5244632807220000090028072281f9d3565bfd956f6e8bb53d09817a4e6b26d1347030900914b4e255cceadac1b1d881e71ceb0339", "45000053530140003b11509e5e107bfdc0a80145d2f2b8b0003ffdd0444d5244632807220000090028072281f9d3565bfd956f6e8bb53d09817a4e6b26d1347030900914b4e255cceadac1b1d881e71ceb0339"),
        (False, "444d5244642807220000090028072282f9d3565bd1d67d01757969c64857b2f2620170309410074435ed05f7c85e8a7770ce40a44f0339", "45000053530d40003b1150925e107bfdc0a80145d2f2b8b0003fd323444d5244642807220000090028072282f9d3565bd1d67d01757969c64857b2f2620170309410074435ed05f7c85e8a7770ce40a44f0339"),
        (False, "444d5244652807220000090028072283f9d3565b439c06c8a6fc011d59bd9970611170a051e4e7440306a7d3c578a37c9c8dec2ced0239", "45000053531540003b11508a5e107bfdc0a80145d2f2b8b0003f7e28444d5244652807220000090028072283f9d3565b439c06c8a6fc011d59bd9970611170a051e4e7440306a7d3c578a37c9c8dec2ced0239"),
        (True, "444d5244662807220000090028072284f9d3565b5a2fabb90dad361a16ff298e6a91547181117079c68d87f72340d8c1bdaafa96200139", "45000053531d40003b1150825e107bfdc0a80145d2f2b8b0003f99a5444d5244662807220000090028072284f9d3565b5a2fabb90dad361a16ff298e6a91547181117079c68d87f72340d8c1bdaafa96200139"),
    ]
    # fmt:on
    # @formatter:on

    ee: EmbeddedExtractor = EmbeddedExtractor()
    full_lc: Optional[FullLinkControl] = None
    for (expect_full_lc, pkt_data, ip_data) in testdata:
        full_lc = ee.process_packet(
            data=bytes.fromhex(pkt_data), packet=IP(bytes.fromhex(ip_data))
        )
        if not expect_full_lc:
            assert not len(capsys.readouterr().out)
        else:
            captured = capsys.readouterr()
            assert not len(captured.err)
            assert len(captured.out)
            assert "PRIVACY" in captured.out
            assert "PRIORITY:0" in captured.out

    assert isinstance(full_lc, FullLinkControl)
    assert full_lc.group_address == 9
    assert full_lc.source_address == 2623266
    assert full_lc.full_link_control_opcode == FLCOs.GroupVoiceChannelUser
