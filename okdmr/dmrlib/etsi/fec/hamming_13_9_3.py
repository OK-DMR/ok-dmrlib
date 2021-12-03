import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class Hamming1393:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.4  Hamming (13,9,3), Hamming (15,11,3), and Hamming (16,11,4)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
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
            len(bits) == 13
        ), f"Hamming (13,9,3) expects exactly 13 bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), Hamming1393.PARITY_CHECK_MATRIX
            ),
            Hamming1393.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(bits: bitarray) -> numpy.ndarray:
        """
        Returns 9 bits (input) with 4 bits of Hamming FEC
        :param bits:
        :return: 13 bits (9 data bits + 4 FEC bits)
        """
        assert (
            len(bits) == 9
        ), f"Hamming (13,9,3) expects 9 bits of data to add 4 bits of parity, got {len(bits)}"
        return divmod(
            numpy.dot(Hamming1393.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2
        )[1]
