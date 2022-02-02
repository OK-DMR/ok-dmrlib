import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class Hamming16114:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.4  Hamming (13,9,3), Hamming (15,11,3), and Hamming (16,11,4)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0, 0, 0, 0, 0])

    @staticmethod
    def check(bits: bitarray) -> bool:
        """
        Verifies Hamming FEC in 5 end bits of input bitarray
        :param bits:
        :return: check result
        """
        assert (
            len(bits) == 16
        ), f"Hamming (15,11,3) expects exactly 16 bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(bits.tolist()), Hamming16114.PARITY_CHECK_MATRIX
            ),
            Hamming16114.CORRECT_SYNDROME,
        )

    @staticmethod
    def check_and_correct(bits: bitarray) -> (bool, bitarray):
        """
        Will check if parity matches, if not, tries to correct one bit-error
        :param bits:
        :return: (parity matches, corrected message)
        """
        check = Hamming16114.check(bits)

        if not check:
            # if check does not pass, find index of flipped bit, and correct it
            syndrome = get_syndrome_for_word(
                numpy.array(bits.tolist()), Hamming16114.PARITY_CHECK_MATRIX
            ).tolist()
            bits.invert(Hamming16114.PARITY_CHECK_MATRIX.T.tolist().index(syndrome))

        return check, bits

    @staticmethod
    def generate(bits: bitarray) -> numpy.ndarray:
        """
        Returns 11 bits (input) with 5 bits of Hamming FEC
        :param bits:
        :return: 16 bits (11 data bits + 5 FEC bits)
        """
        assert (
            len(bits) == 11
        ), f"Hamming (15,11,3) expects 9 bits of data to add 5 bits of parity, got {len(bits)}"
        return divmod(
            numpy.dot(Hamming16114.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2
        )[1]
