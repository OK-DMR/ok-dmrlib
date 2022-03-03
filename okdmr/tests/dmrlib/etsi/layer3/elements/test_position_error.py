from unittest import TestCase

from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.etsi.layer3.elements.position_error import PositionError


class TestPositionError(TestCase):
    def test_values(self):
        for i in range(0, 0b1000):
            PositionError(i)

    def test_bits(self):
        for i in range(0, 0b1000):
            ba: bitarray = int2ba(i, length=3)
            assert PositionError(i).as_bits() == ba
            assert PositionError.from_bits(ba) == PositionError(i)
