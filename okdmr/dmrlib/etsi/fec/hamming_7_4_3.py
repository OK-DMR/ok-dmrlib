import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class Hamming743:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.5  Hamming (7,4,3)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0, 0, 0])

    @staticmethod
    def check(bits: bitarray) -> bool:
        """
        Verifies Hamming FEC in 3 end bits of input bitarray
        :param bits:
        :return: check result
        """
        assert (
            len(bits) == 7
        ), f"Hamming (7,4,3) expects exactly 7 bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), Hamming743.PARITY_CHECK_MATRIX
            ),
            Hamming743.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(bits: bitarray) -> numpy.ndarray:
        """
        Returns 4 bits (input) with 3 bits of Hamming FEC
        :param bits:
        :return: 7 bits (4 data bits + 3 FEC bits)
        """
        assert (
            len(bits) == 4
        ), f"Hamming (7,4,3) expects 4 bits of data to add 3 bits of parity, got {len(bits)}"
        return divmod(
            numpy.dot(Hamming743.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2
        )[1]
