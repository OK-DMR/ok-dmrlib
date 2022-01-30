from typing import Tuple, List

from okdmr.dmrlib.etsi.crc.crc16 import CRC16
from okdmr.dmrlib.etsi.crc.crc_masks import CrcMasks


def test_crc16():
    # @formatter:off
    # fmt:off
    # format: data to be verified, appropriate crc16
    data: List[Tuple[str, str, CrcMasks]] = [
        # short data defined header, llc from 2308155 to 2308155
        ("4da323383b23383b0560", "8040", CrcMasks.DataHeader),
    ]
    # fmt:on
    # @formatter:on

    for testtuple in data:
        assert CRC16.check(
            data=bytes.fromhex(testtuple[0]),
            crc16=int.from_bytes(bytes.fromhex(testtuple[1]), byteorder="big"),
            mask=testtuple[2],
        ), f"CRC16 does not match in ${testtuple}"
