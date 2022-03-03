from unittest import TestCase

from okdmr.dmrlib.etsi.layer2.elements.access_types import AccessTypes


class TestAccessTypes(TestCase):
    def test_raises(self):
        with self.assertRaises(ValueError):
            AccessTypes(-1)
        with self.assertRaises(ValueError):
            AccessTypes(0b10)
