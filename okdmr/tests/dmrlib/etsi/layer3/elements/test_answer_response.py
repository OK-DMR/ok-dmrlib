from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.answer_response import AnswerResponse


def test_answer_response_bits():
    ar: AnswerResponse = AnswerResponse.Proceed
    assert AnswerResponse.from_bits(bitarray("00100000")) == ar
    assert ar.as_bits() == bitarray("00100000")
