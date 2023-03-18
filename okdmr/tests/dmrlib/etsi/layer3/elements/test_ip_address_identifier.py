from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.ip_address_identifier import IPAddressIdentifier


def test_said_daid():
    said = IPAddressIdentifier.from_bits(bits=bitarray("0001"))
    assert said == IPAddressIdentifier.USBEthernetInterfaceNetwork
    assert said.as_bits() == bitarray("0001")

    assert IPAddressIdentifier(3) == IPAddressIdentifier.Reserved
    assert IPAddressIdentifier(13) == IPAddressIdentifier.ManufacturerSpecific
    assert IPAddressIdentifier(2) == IPAddressIdentifier.Reserved
    assert IPAddressIdentifier(12) == IPAddressIdentifier.ManufacturerSpecific
