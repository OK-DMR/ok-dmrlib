from bitarray import bitarray
from bitarray.util import ba2int
from crc import Calculator, Crc16, Crc32

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, BitCrcConfiguration
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_ccit_bitcrc_crc():
    crc_ccit = Calculator(optimized=True, configuration=Crc16.CCITT)
    bit_crc_ccit = BitCrcCalculator(
        table_based=True,
        configuration=BitCrcConfiguration(
            width_bits=16,
            polynomial=0x1021,
            init_value=0x0000,
            final_xor_value=0x0000,
            reverse_input_bytes=False,
            reverse_output_bytes=False,
        ),
    )

    data_bytes: bytes = b"\xFF\xEE\xAA\x88\x44"
    data_bits: bitarray = bytes_to_bits(data_bytes)

    assert crc_ccit.checksum(data_bytes) == ba2int(
        bit_crc_ccit.calculate_checksum(data_bits)
    )


def test_crc32_bitcrc_crc():
    crc32 = Calculator(optimized=True, configuration=Crc32.CRC32)
    bit_crc32 = BitCrcCalculator(
        table_based=True,
        configuration=BitCrcConfiguration(
            width_bits=32,
            polynomial=0x04C11DB7,
            init_value=0xFFFFFFFF,
            final_xor_value=0xFFFFFFFF,
            reverse_input_bytes=True,
            reverse_output_bytes=True,
        ),
    )

    data_bytes: bytes = b"\xAA\x88\x44\x00\x00"
    data_bits: bitarray = bytes_to_bits(data_bytes)

    assert crc32.checksum(data_bytes) == ba2int(bit_crc32.calculate_checksum(data_bits))


def test_feed_width():
    assert 9 == BitCrcConfiguration(polynomial=0x0, width_bits=9).feed_width_bits
    assert 1 == BitCrcConfiguration(polynomial=0x0, width_bits=1).feed_width_bits
    assert 8 == BitCrcConfiguration(polynomial=0x0, width_bits=16).feed_width_bits
