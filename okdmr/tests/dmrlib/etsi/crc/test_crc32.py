from typing import Tuple, List

from okdmr.dmrlib.etsi.crc.crc32 import CRC32


def test_crc32():
    # @formatter:off
    # fmt:off
    # format: full hex payload, crc32 from last block
    data: List[Tuple[str, str]] = [
        # Rate 1/2
        ("d6790062620003bf000700000000000000000000", "210b9a3d"),
        # Rate 1/2 unconfirmed, contains Hytera RRS payload (IP/UDP packet, port 4001)
        ("45000038fb410000401125490c23380b0d0008fd0fa10fa10024276a0d1a22047fffffff694728710f0a522c2d82534e6c0048564770402b", "82616528"),
        # short data defined payload
        ("0600fb4f3d3f82afc6d80b42ce88668afc7d8b1807e83c308d95bb8be5dd59e95b2837e795af87005ae2a743535ca421601d", "c76ae25c")
    ]
    # fmt:on
    # @formatter:on

    for databytes, expected_crc32 in data:
        assert CRC32.check(
            data=bytes.fromhex(databytes),
            crc32=int.from_bytes(bytes.fromhex(expected_crc32), byteorder="little"),
        ), f"CRC32 does not match in {(databytes, expected_crc32)} {CRC32.calculate(bytes.fromhex(databytes))}"
