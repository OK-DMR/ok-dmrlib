from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.channel_timing_opcode import ChannelTimingOpcode


def test_cto():
    assert (
        ChannelTimingOpcode.from_bits(bitarray("01"))
        == ChannelTimingOpcode.UnalignedTerminator
    )
