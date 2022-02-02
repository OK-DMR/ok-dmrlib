from random import randint

import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_17_12_3 import Hamming17123

HAMMING_17_12_3_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0],
]


def test_hamming17123_check():
    for valid in HAMMING_17_12_3_VALID_WORDS:
        assert Hamming17123.check(bitarray(valid)) is True


def test_hamming17123_generate():
    for valid in HAMMING_17_12_3_VALID_WORDS:
        assert numpy.array_equal(Hamming17123.generate(bitarray(valid)[:12]), valid)


def test_hamming17123_repair():
    for valid in HAMMING_17_12_3_VALID_WORDS:
        invalid = bitarray(valid)
        # flip single bit
        invalid.invert(randint(0, len(valid) - 1))
        is_valid, corrected = Hamming17123.check_and_correct(invalid)
        assert not is_valid, "No bits was flipped for test purposes?"
        assert bitarray(valid) == corrected
