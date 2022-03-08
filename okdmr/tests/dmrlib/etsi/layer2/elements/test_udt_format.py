from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.udt_format import UDTFormat


def test_udt_format():
    assert UDTFormat(0b1001) == UDTFormat.ManufacturerSpecific
    assert UDTFormat(0b1110) == UDTFormat.Reserved

    ba = bitarray("0100")
    assert UDTFormat.from_bits(ba).as_bits() == ba
