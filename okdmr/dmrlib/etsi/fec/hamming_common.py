import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import get_syndrome_for_word
from okdmr.dmrlib.utils.bits_bytes import (
    numpy_array_to_bitarray,
    bitarray_to_numpy_array,
)


class HammingCommon:
    GENERATOR_MATRIX: numpy.ndarray
    PARITY_CHECK_MATRIX: numpy.ndarray
    CORRECT_SYNDROME: numpy.ndarray
    CODEWORD_LENGTH: int
    CODE_DIMENSION: int
    MINIMUM_HAMMING_DISTANCE: int

    @classmethod
    def check(cls, bits: bitarray) -> bool:
        """
        Verifies Hamming FEC in full codeword
        :param bits:
        :return: check result
        """
        assert (
            len(bits) == cls.CODEWORD_LENGTH
        ), f"Hamming ({cls.CODEWORD_LENGTH},{cls.CODE_DIMENSION},{cls.MINIMUM_HAMMING_DISTANCE}) expects exactly {cls.CODEWORD_LENGTH} bits, got {len(bits)}"
        return numpy.array_equal(
            get_syndrome_for_word(numpy.array(bits.tolist()), cls.PARITY_CHECK_MATRIX),
            cls.CORRECT_SYNDROME,
        )

    @classmethod
    def correct_numpy_array(cls, bits: numpy.ndarray) -> numpy.ndarray:
        """
        Will repair single bit-flip and return ndarray instead of bitarray
        :param bits:
        :return:
        """
        is_correct, correct_bits = cls.check_and_correct(numpy_array_to_bitarray(bits))
        return bitarray_to_numpy_array(correct_bits) if is_correct else bits

    @classmethod
    def check_and_correct(cls, bits: bitarray) -> (bool, bitarray):
        """
        Will check if parity matches, if not, tries to correct one bit-error
        :param bits:
        :return: (status of returned message where False means it is unrepairable, message)
        """
        check = cls.check(bits)

        if not check:
            # if check does not pass, find index of flipped bit, and correct it
            syndrome = get_syndrome_for_word(
                numpy.array(bits.tolist()), cls.PARITY_CHECK_MATRIX
            ).tolist()
            try:
                bits.invert(cls.PARITY_CHECK_MATRIX.T.tolist().index(syndrome))
                check = True
            except ValueError as e:
                # ValueError is thrown in case syndrome is not found in parity check result, making the message uncorrectable
                return False, bits

        return check, bits

    @classmethod
    def generate(cls, bits: bitarray) -> numpy.ndarray:
        """
        Returns codeword with added parity bits
        :param bits:
        :return: full codeword
        """
        assert (
            len(bits) == cls.CODE_DIMENSION
        ), f"Hamming ({cls.CODEWORD_LENGTH},{cls.CODE_DIMENSION},{cls.MINIMUM_HAMMING_DISTANCE}) expects {cls.CODE_DIMENSION} bits of data to add parity bits, got {len(bits)}"
        return divmod(numpy.dot(cls.GENERATOR_MATRIX.T, numpy.array(bits.tolist())), 2)[
            1
        ]
