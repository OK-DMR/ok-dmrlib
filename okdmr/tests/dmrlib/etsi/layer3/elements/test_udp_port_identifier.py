from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.udp_port_identifier import UDPPortIdentifier


def test_spid_dpid():
    assert UDPPortIdentifier(1) == UDPPortIdentifier.UTF16BE_TextMessage
    assert UDPPortIdentifier.from_bits(bitarray("0000010")).as_bits() == bitarray(
        "0000010"
    )
    assert UDPPortIdentifier(4) == UDPPortIdentifier.Reserved
