import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_15_11_3 import Hamming15113

HAMMING_15_11_3_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
]


def test_hamming15113_check():
    for valid in HAMMING_15_11_3_VALID_WORDS:
        assert Hamming15113.check(bitarray(valid)) is True


def test_hamming15113_generate():
    for valid in HAMMING_15_11_3_VALID_WORDS:
        assert numpy.array_equal(Hamming15113.generate(bitarray(valid)[:11]), valid)
