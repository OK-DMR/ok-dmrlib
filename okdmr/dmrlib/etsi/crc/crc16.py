from bitarray.util import ba2int

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc16
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


class CRC16:
    """
    B.3.8 CRC-CCITT calculation - ETSI TS 102 361-1 V2.5.1 (2017-10)
    Also can be called CRC16-CCIT
    """

    CALC: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc16.ETSI_DMR
    )

    @staticmethod
    def check(data: bytes, crc16: int, mask: CrcMasks) -> bool:
        """
        Will check that provided crc16 param matches the internal calculation
        :param data: data bytes
        :param crc16: expected crc-ccit (crc16) result
        :param mask: crc mask
        :return:
        """
        assert (
            0x0000 <= crc16 <= 0xFFFF
        ), f"CRC16 is expected in range (exclusive) 0-{0xFFFF}, got {crc16}"

        return CRC16.calculate(data, mask) == crc16

    @staticmethod
    def calculate(data: bytes, mask: CrcMasks) -> int:
        """
        Will perform bytes-swap of payload and returns CRC16 as int
        :param data: bytes object of data to be checksumed
        :param mask: crc mask to be applied
        :return: int crc16
        """
        return ba2int(~CRC16.CALC.calculate_checksum(bytes_to_bits(data))) ^ mask.value
