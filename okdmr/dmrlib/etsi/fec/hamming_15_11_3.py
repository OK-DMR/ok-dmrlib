import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class Hamming15113:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.4  Hamming (13,9,3), Hamming (15,11,3), and Hamming (16,11,4)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0, 0, 0, 0])

    @staticmethod
    def check(bits: bitarray) -> bool:
        """
        Verifies Hamming FEC in 4 end bits of input bitarray
        :param bits:
        :return: check result
        """
        assert (
            len(bits) == 15
        ), f"Hamming (15,11,3) expects exactly 15 bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), Hamming15113.PARITY_CHECK_MATRIX
            ),
            Hamming15113.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(bits: bitarray) -> bitarray:
        """
        Returns 11 bits (input) with 4 bits of Hamming FEC
        :param bits:
        :return: 15 bits (11 data bits + 4 FEC bits)
        """
        assert (
            len(bits) == 11
        ), f"Hamming (15,11,3) expects 9 bits of data to add 4 bits of parity, got {len(bits)}"
        return divmod(
            numpy.dot(Hamming15113.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2
        )[1]
