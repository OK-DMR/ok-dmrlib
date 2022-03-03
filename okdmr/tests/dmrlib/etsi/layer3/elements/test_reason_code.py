from unittest import TestCase

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.reason_code import ReasonCode


class TestReasonCode(TestCase):
    def test_bits(self):
        rc: ReasonCode = ReasonCode.MSDoesNotSupportThisFeatureOrService
        assert rc.as_bits() == bitarray("00100001")
        assert ReasonCode.from_bits(bitarray("00100001")) == rc

    def test_raises(self):
        for i in range(0, 1 << 8):
            if i != ReasonCode.MSDoesNotSupportThisFeatureOrService.value:
                with self.assertRaises(ValueError):
                    ReasonCode(i)
