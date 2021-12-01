import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.golay_20_8_7 import Golay2087

GOLAY_20_8_7_VALID_WORDS: list = [
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
]


def test_golay2087_check():
    for valid in GOLAY_20_8_7_VALID_WORDS:
        assert Golay2087.check(bitarray(valid)) is True


def test_golay2087_generate():
    for valid in GOLAY_20_8_7_VALID_WORDS:
        assert numpy.array_equal(Golay2087.generate(bitarray(valid)[:8]), valid)
