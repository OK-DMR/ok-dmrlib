from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats


def test_dpf():
    assert DataPacketFormats(0b0100) == DataPacketFormats.Reserved
    assert DataPacketFormats.Reserved.as_bits() == bitarray("1100")
