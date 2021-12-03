from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.quadratic_residue_16_7_6 import QuadraticResidue1676

VALID_QR_16_7_6_WORDS = [[0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1]]


def test_qr1676_check():
    for valid_word in VALID_QR_16_7_6_WORDS:
        assert QuadraticResidue1676.check(bitarray(valid_word))


def test_qr1676_generate():
    for valid_word in VALID_QR_16_7_6_WORDS:
        bits: bitarray = bitarray(valid_word)
        assert bits.tolist() == list(QuadraticResidue1676.generate(bits[:7]))
