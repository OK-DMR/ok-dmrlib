import numpy


def derive_parity_check_matrix_from_generator(
    generator: numpy.ndarray,
) -> numpy.ndarray:
    k = generator.shape[0]
    n = generator.shape[1]

    return numpy.concatenate(
        (numpy.transpose(generator[:, k:]), numpy.identity(n - k, dtype=int)), axis=1
    )


def get_syndrome_for_word(
    codeword: numpy.ndarray, parity_check_matrix: numpy.ndarray, fieldsize: int = 2
) -> numpy.ndarray:
    # @ is matrix multiplication, PEP 0465, https://www.python.org/dev/peps/pep-0465/
    return (codeword @ parity_check_matrix.T) % fieldsize
