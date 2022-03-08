from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.defined_data_formats import DefinedDataFormats


def test_undefined():
    assert DefinedDataFormats(0b110011) == DefinedDataFormats.Reserved
    assert bitarray("010010") == DefinedDataFormats.CharsetUTF8.as_bits()
