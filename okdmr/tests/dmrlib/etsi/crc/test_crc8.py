from typing import List

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc8 import CRC8


def test_crc8():
    # @formatter:off
    # fmt:off
    # format: data to be verified (36 bits of CACH Short LC) including the 8-bit CRC on the end of bits
    data: List[bitarray] = [
        bitarray('000100000000000000000000000000010110'),
        bitarray('000100000011000000001101101010100011')
    ]
    # fmt:on
    # @formatter:on

    for bits in data:
        assert CRC8.check(
            data=bits[:28], crc8=ba2int(bits[28:36])
        ), f"CRC8 does not match in {bits}"
