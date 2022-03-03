import os
import tempfile
from argparse import ArgumentParser

from _pytest.capture import CaptureFixture

from okdmr.dmrlib.tools.pcap_tool import PcapTool


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
    finally:
        tmpfile.close()
        os.unlink(tmpfile.name)


def test_pcap_tool_main():
    assert isinstance(PcapTool._arguments(), ArgumentParser)
