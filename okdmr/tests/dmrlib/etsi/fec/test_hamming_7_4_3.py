from random import randint

import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_7_4_3 import Hamming743

HAMMING_7_4_3_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 1, 0],
]


def test_hamming743_check():
    for valid in HAMMING_7_4_3_VALID_WORDS:
        assert Hamming743.check(bitarray(valid)) is True


def test_hamming743_generate():
    for valid in HAMMING_7_4_3_VALID_WORDS:
        assert numpy.array_equal(Hamming743.generate(bitarray(valid)[:4]), valid)


def test_hamming743_repair():
    for valid in HAMMING_7_4_3_VALID_WORDS:
        invalid = bitarray(valid)
        # flip single bit
        invalid.invert(randint(0, len(valid) - 1))
        is_valid, corrected = Hamming743.check_and_correct(invalid)
        assert is_valid, "single bit-flips should be repaired"
        assert bitarray(valid) == corrected
