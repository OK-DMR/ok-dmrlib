from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)


def test_extended_headers():
    both: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader.from_bits(
        bitarray("0" * 72)
    )
    assert both.extended_header_2 is not None
    assert both.extended_header_1 is not None
    assert both.as_bits() == bitarray("0" * 72)

    single: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader.from_bits(
        bitarray("0" * 31 + "1" + "0" * 40)
    )
    assert single.extended_header_1 is not None
    assert single.extended_header_2 is None
    assert single.as_bits() == bitarray("0" * 31 + "1" + "0" * 40)
