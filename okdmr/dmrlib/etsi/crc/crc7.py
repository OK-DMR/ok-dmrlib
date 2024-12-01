from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc7
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks


class CRC7:
    """
    B.3.13 7-bit CRC calculation - ETSI TS 102 361-1 V2.5.1 (2017-10)
    """

    CALC: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc7.ETSI_DMR
    )

    @staticmethod
    def check(
        data: bitarray, crc7: int, mask: CrcMasks = CrcMasks.ReverseChannel
    ) -> bool:
        """
        Will check that provided crc7 param matches the internal calculation
        :param data: bitarray data
        :param mask: usually only CrcMasks.ReverseChannel
        :param crc7 expected result
        :return: verification result
        """
        assert (
            0x00 <= crc7 <= 0x7F
        ), f"crc7 is expected in range (exclusive) 0-{0x7F}, got {crc7}"

        return CRC7.calculate(data, mask) == crc7

    @staticmethod
    def calculate(data: bitarray, mask: CrcMasks = CrcMasks.ReverseChannel) -> int:
        """
        Will perform bytes-swap of payload and returns crc7 as int
        :param data: bytes object of data to be checked
        :param mask: usually only CrcMasks.ReverseChannel
        :return: int crc7
        """
        return ba2int(CRC7.CALC.calculate_checksum(data)) ^ mask.value
