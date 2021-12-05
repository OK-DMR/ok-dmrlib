import numpy

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
    get_syndrome_for_word,
)


class ReedSolomon1294:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.6  Reed-Solomon (12,9)
    """

    GENERATOR_MATRIX: numpy.ndarray = numpy.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0x1C, 0xBC, 0xFD],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0x89, 0x31, 0x08],
            [0, 0, 1, 0, 0, 0, 0, 1, 1, 0xAD, 0x41, 0x36],
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 0x7D, 0x71, 0x16],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 0xF3, 0xA6, 0x3A],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0x08, 0x83, 0x7B],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0x3F, 0x6F, 0x02],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0x6C, 0x0D, 0xA7],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0x0E, 0x38, 0x40],
        ]
    )

    PARITY_CHECK_MATRIX: numpy.ndarray = derive_parity_check_matrix_from_generator(
        GENERATOR_MATRIX
    )

    CORRECT_SYNDROME: numpy.ndarray = numpy.array([0x00, 0x00, 0x00])

    @staticmethod
    def check(data: bytes) -> bool:
        """
        Verifies Reed-Solomon (12,9,4) checksum in last 3 bytes of input
        :param data:
        :return: check result
        """
        assert (
            len(data) == 12
        ), f"Reed-Solomon (12,9,4) expects exactly 12 bytes, got {len(data)}"
        return numpy.array_equal(
            get_syndrome_for_word(
                numpy.array(data), ReedSolomon1294.PARITY_CHECK_MATRIX
            ),
            ReedSolomon1294.CORRECT_SYNDROME,
        )

    @staticmethod
    def generate(data: bytes) -> numpy.ndarray:
        """
        Returns 9 bytes (72 bits) of input data + 3 bytes (24 bits) of RS1294 CRC
        :param data:
        :return: 16 bits (7 data bits + 9 crc bits)
        """
        assert (
            len(data) == 9
        ), f"Reed-Solomon (12,9,4) expects 9 bytes of data to add 3 bytes of parity, got {len(data)}"
        return divmod(
            numpy.dot(ReedSolomon1294.GENERATOR_MATRIX.T, numpy.array(data)),
            2,
        )[1]
