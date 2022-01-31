from okdmr.dmrlib.utils.bits_bytes import byteswap_bytes


def test_byteswap_odd():
    """
    When swapping bytes payload containing odd amount of bytes, the last byte should stay in place
    :return:
    """
    testdata: bytes = b"\x33\xC7\x88"
    swap: bytes = byteswap_bytes(testdata)
    assert testdata[-1] == swap[-1]
