from okdmr.dmrlib.etsi.layer2.elements.slcos import SLCOs


def test_slcos():
    assert SLCOs(0b0101) == SLCOs.Reserved
    assert SLCOs(0b1101) == SLCOs.ManufacturerSelectable

    for i in range(0b0000, 0b1111):
        # this tests that all values in SLCO value range are defined, and no error is thrown
        assert isinstance(SLCOs(i), SLCOs)
