from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc8


class CRC8:
    """
    B.3.7 8-bit CRC calculation - ETSI TS 102 361-1 V2.5.1 (2017-10)
    """

    CALC: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc8.ETSI_DMR
    )

    @staticmethod
    def check(data: bitarray, crc8: int) -> bool:
        """
        Will check that provided crc8 param matches the internal calculation
        :param data: bitarray data
        :param crc8 expected result
        :return:
        """
        assert (
            0x00 <= crc8 <= 0xFF
        ), f"CRC8 is expected in range (exclusive) 0-{0xFF}, got {crc8}"

        return CRC8.calculate(data) == crc8

    @staticmethod
    def calculate(data: bitarray) -> int:
        """
        Will perform bytes-swap of payload and returns CRC8 as int
        :param data: bytes object of data to be checksumed
        :return: int crc8
        """
        return ba2int(CRC8.CALC.calculate_checksum(data))
