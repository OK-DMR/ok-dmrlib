from unittest import TestCase

import numpy
from bitarray import bitarray
from numpy import array_equal

from okdmr.dmrlib.utils.bits_bytes import (
    byteswap_bytes,
    numpy_array_to_bitarray,
    bitarray_to_numpy_array,
)


def test_byteswap_odd():
    """
    When swapping bytes payload containing odd amount of bytes, the last byte should stay in place
    :return:
    """
    testdata: bytes = b"\x33\xC7\x88"
    swap: bytes = byteswap_bytes(testdata)
    assert testdata[-1] == swap[-1]


class BitsBytesTest(TestCase):
    def test_shape(self):
        with self.assertRaises(ValueError):
            numpy_array_to_bitarray(numpy.array([[0, 1], [1, 0]]))

    @staticmethod
    def test_bitarray_to_numpy_array():
        assert array_equal(
            bitarray_to_numpy_array(bitarray("01011011")),
            numpy.array([0, 1, 0, 1, 1, 0, 1, 1]),
        )
