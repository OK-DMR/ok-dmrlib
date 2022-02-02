from typing import List

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc8 import CRC8


def test_crc16():
    # @formatter:off
    # fmt:off
    # format: data to be verified, appropriate crc16
    data: List[bitarray] = [
        bitarray('000100000000000000000000000000010110'),
    ]
    # fmt:on
    # @formatter:on

    for bits in data:
        assert CRC8.check(
            data=bits[:28], crc8=ba2int(bits[28:])
        ), f"CRC16 does not match in {bits}"
