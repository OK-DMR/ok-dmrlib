from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier


def test_sap_identifier():
    assert SAPIdentifier(0b1011) == SAPIdentifier.Reserved
    assert SAPIdentifier.ARP.as_bits() == bitarray("0101")
