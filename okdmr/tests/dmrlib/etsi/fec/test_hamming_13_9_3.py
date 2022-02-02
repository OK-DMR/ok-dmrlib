from random import randint

import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import get_syndrome_for_word
from okdmr.dmrlib.etsi.fec.hamming_13_9_3 import Hamming1393
from okdmr.dmrlib.etsi.fec.hamming_7_4_3 import Hamming743

HAMMING_13_9_3_VALID_WORDS: list = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    [0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
]


def test_hamming1393_check():
    for valid in HAMMING_13_9_3_VALID_WORDS:
        assert Hamming1393.check(bitarray(valid)) is True


def test_hamming1393_generate():
    for valid in HAMMING_13_9_3_VALID_WORDS:
        assert numpy.array_equal(Hamming1393.generate(bitarray(valid)[:9]), valid)


def test_hamming1393_repair():
    for valid in HAMMING_13_9_3_VALID_WORDS:
        invalid = bitarray(valid)
        # flip single bit
        invalid.invert(randint(0, len(valid) - 1))
        is_valid, corrected = Hamming1393.check_and_correct(invalid)
        assert not is_valid, "No bits was flipped for test purposes?"
        assert bitarray(valid) == corrected
