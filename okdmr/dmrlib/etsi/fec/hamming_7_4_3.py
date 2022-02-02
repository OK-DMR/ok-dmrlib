import numpy

from okdmr.dmrlib.etsi.fec.fec_utils import (
    derive_parity_check_matrix_from_generator,
)
from okdmr.dmrlib.etsi.fec.hamming_common import HammingCommon


class Hamming743(HammingCommon):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.5  Hamming (7,4,3)
    """

    GENERATOR_MATRIX = numpy.array(
        [
            [1, 0, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 1, 1],
        ]
    )

    PARITY_CHECK_MATRIX = derive_parity_check_matrix_from_generator(GENERATOR_MATRIX)

    CORRECT_SYNDROME = numpy.array([0, 0, 0])

    CODEWORD_LENGTH = 7
    CODE_DIMENSION = 4
    MINIMUM_HAMMING_DISTANCE = 3
