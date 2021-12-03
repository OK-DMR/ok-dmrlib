import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class Golay2087:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.1 Golay (20,8,7)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    @staticmethod
    def check(bits: bitarray) -> bool:
        """
        Verifies Golay FEC in 12 end bits of input bitarray
        :param bits:
        :return: check result
        """
        assert len(bits) == 20, "Golay (20,8,7) expects exactly 20 bits"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), Golay2087.PARITY_CHECK_MATRIX
            ),
            Golay2087.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(bits: bitarray) -> numpy.ndarray:
        """
        Returns 8 bits (input) with 12 bits of Golay FEC
        :param bits:
        :return: 20 bits (8 data bits + 12 FEC bits)
        """
        assert (
            len(bits) == 8
        ), "Golay (20,8,7) expects 8 bits of data to add 12 bits of parity"
        return divmod(
            numpy.dot(Golay2087.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2
        )[1]
