from typing import Tuple, List

from okdmr.dmrlib.etsi.crc.crc16 import CRC16
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks


def test_crc16():
    # @formatter:off
    # fmt:off
    # format: data to be verified, appropriate crc16
    data: List[Tuple[str, str, CrcMasks]] = [
        # short data defined header, llc from 2308155 to 2308155
        ("4da323383b23383b0560", "8040", CrcMasks.DataHeader),
        # csbk
        ("bd0080180008fd23383b", "b2ed", CrcMasks.CSBK),
        # hytera pi header contents
        ("211002177afc73000009", "0dda", CrcMasks.PiHeader)
    ]
    # fmt:on
    # @formatter:on

    for (databytes, crc16, crc_mask) in data:
        assert CRC16.check(
            data=bytes.fromhex(databytes),
            crc16=int.from_bytes(bytes.fromhex(crc16), byteorder="big"),
            mask=crc_mask,
        ), f"CRC16 does not match in {(databytes, crc16, crc_mask)}"
