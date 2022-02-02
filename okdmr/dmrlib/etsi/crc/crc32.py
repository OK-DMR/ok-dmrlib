from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc32
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits, byteswap_bytes


class CRC32:
    """
    B.3.9 32-bit CRC calculation - ETSI TS 102 361-1 V2.5.1 (2017-10)
    No CRC-mask is applied before transmission, no need to check it
    """

    CALC: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc32.ETSI_DMR
    )

    @staticmethod
    def check(data: bytes, crc32: int) -> bool:
        """
        Will check that provided crc32 param matches the internal calculation
        :param data:
        :param crc32:
        :return:
        """
        assert (
            0x00000000 <= crc32 <= 0xFFFFFFFF
        ), f"CRC32 is expected in range (exclusive) 0-{0xFFFFFFFF}, got {crc32}"

        return CRC32.calculate(data) == crc32

    @staticmethod
    def calculate(data: bytes) -> int:
        """
        Will perform bytes-swap of payload and returns CRC32 as int
        :param data: bytes object of data to be checksumed
        :return: int crc32
        """
        return ba2int(
            CRC32.CALC.calculate_checksum(bytes_to_bits(byteswap_bytes(data)))
        )
