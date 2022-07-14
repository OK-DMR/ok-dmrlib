from unittest import TestCase

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs


def test_missing():
    assert FeatureSetIDs(0b11) == FeatureSetIDs.ReservedForFutureStandardization
    assert FeatureSetIDs(0b1100) == FeatureSetIDs.FlydeMicroLtd
    assert FeatureSetIDs(0b11000000) == FeatureSetIDs.ReservedForFutureMFID
    assert FeatureSetIDs(0b110011) == FeatureSetIDs.from_bits(bitarray("110011"))
    for i in range(0, 1 << 8):
        # in case this statement raises error, test fails
        FeatureSetIDs(i)


class RaisingFID(TestCase):
    def test_fid_raising(self):
        with self.assertRaises(AssertionError):
            FeatureSetIDs(-1)
        with self.assertRaises(AssertionError):
            FeatureSetIDs(1 << 9)
        for val in range(1 << 8, 1 << 9):
            # tests that any values 1<<8 through 1<<9 raise Assert not ValueError
            with self.assertRaises(AssertionError):
                FeatureSetIDs(val)
