from typing import Tuple, List

from okdmr.dmrlib.etsi.crc.crc32 import CRC32


def test_crc32():
    # @formatter:off
    # fmt:off
    # format: full hex payload, crc32 from last block
    data: List[Tuple[str, str]] = [
        # Rate 1/2 unconfirmed, contains Hytera RRS payload (IP/UDP packet, port 4001)
        ("45000038fb410000401125490c23380b0d0008fd0fa10fa10024276a0d1a22047fffffff694728710f0a522c2d82534e6c0048564770402b", "82616528"),
    ]
    # fmt:on
    # @formatter:on

    for (databytes, expected_crc32) in data:
        assert CRC32.check(
            data=bytes.fromhex(databytes),
            crc32=int.from_bytes(bytes.fromhex(expected_crc32), byteorder="little"),
        ), f"CRC32 does not match in ${(databytes, expected_crc32)}"
