from random import randint

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


def test_hamming1393_repair():
    for valid in HAMMING_15_11_3_VALID_WORDS:
        invalid = bitarray(valid)
        # flip single bit
        invalid.invert(randint(0, len(valid) - 1))
        is_valid, corrected = Hamming15113.check_and_correct(invalid)
        assert not is_valid, "No bits was flipped for test purposes?"
        assert bitarray(valid) == corrected
