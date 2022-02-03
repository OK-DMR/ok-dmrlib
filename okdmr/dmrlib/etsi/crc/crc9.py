from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc9
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


class CRC9:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.10 CRC-9 calculation
    """

    CALC: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc9.ETSI_DMR
    )

    @staticmethod
    def check(data: bytes, serial_number: int, crc9: int, crc32: bytes = None) -> bool:
        assert crc9 <= 511, "CRC-9 check value is invalid, max. for 9-bit number is 511"

        source_data: bitarray = bytes_to_bits(data, endian="big")

        if crc32 is not None:
            assert len(crc32) == 4, "32-bit CRC must be exactly 4-bytes long"
            source_data += bytes_to_bits(crc32, endian="big")

        dbsnba = int2ba(serial_number, length=7, endian="big", signed=False)
        source_data += dbsnba

        return CRC9.calculate(source_data) == crc9

    @staticmethod
    def calculate(data: bitarray) -> int:
        return ba2int(CRC9.CALC.calculate_checksum(data))
