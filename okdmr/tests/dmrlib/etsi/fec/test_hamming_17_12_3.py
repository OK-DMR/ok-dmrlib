import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_17_12_3 import Hamming16114

HAMMING_17_12_3_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0],
]


def test_hamming17123_check():
    for valid in HAMMING_17_12_3_VALID_WORDS:
        assert Hamming16114.check(bitarray(valid)) is True


def test_hamming17123_generate():
    for valid in HAMMING_17_12_3_VALID_WORDS:
        assert numpy.array_equal(Hamming16114.generate(bitarray(valid)[:12]), valid)
