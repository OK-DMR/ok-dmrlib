import pytest

from okdmr.dmrlib.etsi.layer2.elements.access_types import AccessTypes


class TestAccessTypes:
    def test_raises(self):
        with pytest.raises(ValueError):
            AccessTypes(-1)
        with pytest.raises(ValueError):
            AccessTypes(0b10)
