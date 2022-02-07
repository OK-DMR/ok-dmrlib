from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes


def test_data_types_mising():
    assert DataTypes(0b1111) == DataTypes.Reserved
