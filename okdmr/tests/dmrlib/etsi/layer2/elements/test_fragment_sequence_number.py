from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.fragment_sequence_number import (
    FragmentSequenceNumber,
)


def test_fsn():
    assert FragmentSequenceNumber.from_bits(bitarray("0111")).as_bits() == bitarray(
        "0111"
    )
    fsn: FragmentSequenceNumber = FragmentSequenceNumber(0b1000)
    assert fsn.is_last()
    assert len(repr(fsn))
    fsn = FragmentSequenceNumber(0b0000)
    assert fsn.is_last()
    assert len(repr(fsn))
    fsn = FragmentSequenceNumber(0b1111)
    assert fsn.is_last()
    assert len(repr(fsn))
    fsn = FragmentSequenceNumber(0b0010)
    assert not fsn.is_last()
    assert len(repr(fsn))
