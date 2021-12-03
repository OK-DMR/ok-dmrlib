from okdmr.dmrlib.etsi.fec.five_bit_checksum import FiveBitChecksum


def test_5bit_verify():
    assert FiveBitChecksum.verify(b"\x10\x20\x00\x0c\x30\x2f\x9b\xe5", 0xC)
