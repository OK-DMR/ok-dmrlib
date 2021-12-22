from bitarray import bitarray
from bitarray.util import int2ba
from crccheck.crc import CrcBase

from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


class CRC9(CrcBase):
    _width = 9
    _poly = 0x59
    _reflect_input = False
    _reflect_output = False
    _xor_output = 0x00
    _names = ("CRC-9",)

    @staticmethod
    def check(
        data: bytes,
        serial_number: int,
        crc9: int,
        crc32: bytes = None,
        mask: int = 0x00,
    ) -> bool:
        source_data: bitarray = bytes_to_bits(data, endian="big")
        if crc32 is not None:
            assert len(crc32) == 4, "32-bit CRC must be exactly 4-bytes long"
            source_data += bytes_to_bits(crc32, endian="big")
        else:
            dbsnba = int2ba(serial_number, length=7, endian="little", signed=False)
            source_data += dbsnba

        print(
            "crccheck",
            (
                CRC9.calc(data=source_data),
                CRC9.calc(data=source_data.tobytes()),
                CRC9.calc(data=source_data.tolist()),
            ),
            "expected",
            (crc9, crc9 ^ 0x1FF, crc9 ^ mask),
        )

        return False

    @staticmethod
    def calculate(data: bitarray) -> int:
        return 0
