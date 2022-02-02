from random import randint

import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_16_11_4 import Hamming16114

HAMMING_16_11_4_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1],
]


def test_hamming16114_check():
    for valid in HAMMING_16_11_4_VALID_WORDS:
        assert Hamming16114.check(bitarray(valid)) is True


def test_hamming16114_generate():
    for valid in HAMMING_16_11_4_VALID_WORDS:
        assert numpy.array_equal(Hamming16114.generate(bitarray(valid)[:11]), valid)


def test_hamming1393_repair():
    for valid in HAMMING_16_11_4_VALID_WORDS:
        invalid = bitarray(valid)
        # flip single bit
        invalid.invert(randint(0, len(valid) - 1))
        is_valid, corrected = Hamming16114.check_and_correct(invalid)
        assert not is_valid, "No bits was flipped for test purposes?"
        assert bitarray(valid) == corrected
