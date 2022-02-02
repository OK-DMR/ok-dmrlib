import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.fec_utils import get_syndrome_for_word


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
    def check_and_correct(cls, bits: bitarray) -> (bool, bitarray):
        """
        Will check if parity matches, if not, tries to correct one bit-error
        :param bits:
        :return: (parity matches, corrected message)
        """
        check = cls.check(bits)

        if not check:
            # if check does not pass, find index of flipped bit, and correct it
            syndrome = get_syndrome_for_word(
                numpy.array(bits.tolist()), cls.PARITY_CHECK_MATRIX
            ).tolist()
            bits.invert(cls.PARITY_CHECK_MATRIX.T.tolist().index(syndrome))

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
