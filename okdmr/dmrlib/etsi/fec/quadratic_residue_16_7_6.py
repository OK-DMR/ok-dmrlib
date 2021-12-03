import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class QuadraticResidue1676:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.2  Quadratic residue (16,7,6)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

    @staticmethod
    def check(bits: bitarray) -> bool:
        """
        Verifies QR (Quadratic Residue) in last 9 bits of input
        :param bits:
        :return: check result
        """
        assert (
            len(bits) == 16
        ), f"Quadratic Residue (16,7,6) expects exactly 16 bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), QuadraticResidue1676.PARITY_CHECK_MATRIX
            ),
            QuadraticResidue1676.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(bits: bitarray) -> numpy.ndarray:
        """
        Returns 7 bits (input) with 9 bits of CRC
        :param bits:
        :return: 16 bits (7 data bits + 9 crc bits)
        """
        assert (
            len(bits) == 7
        ), f"Quadratic Residue (16,7,6) expects 7 bits of data to add 9 bits of parity, got {len(bits)}"
        return divmod(
            numpy.dot(
                QuadraticResidue1676.GENERATOR_MATRIX.T, numpy.array(bits.tolist())
            ),
            2,
        )[1]
