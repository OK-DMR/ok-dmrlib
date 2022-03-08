from typing import List

from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.etsi.crc.crc8 import CRC8
from okdmr.dmrlib.etsi.fec.vbptc_68_28 import VBPTC6828
from okdmr.dmrlib.etsi.layer2.elements.slcos import SLCOs
from okdmr.dmrlib.etsi.layer2.pdu.short_link_control import ShortLinkControl


def test_vbptc_sanity():
    assert len(VBPTC6828.FULL_DEINTERLEAVING_MAP) == 68
    assert len(VBPTC6828.DEINTERLEAVE_INFO_BITS_ONLY_MAP) == 28
    assert len(VBPTC6828.INTERLEAVING_INDICES) == 68
    assert len(VBPTC6828.INTERLEAVE_INFO_BITS_ONLY_MAP) == 28
    assert len(VBPTC6828.FULL_INTERLEAVING_MAP) == 68
    assert len(VBPTC6828.DEINTERLEAVE_8BIT_CHECKSUM) == 8


def test_encode_decode_vbptc():
    bursts: List[(str, SLCOs)] = [
        (
            "00000000000010010000000000000011000000110011000010011001101000000000",
            SLCOs.ActivityUpdate,
        ),
        (
            "00110000001110010011000000110000010101011010111111110101011010101001",
            SLCOs.ActivityUpdate,
        ),
        (
            "00000000000010010000000000000011000000110011000010011001101000000000",
            SLCOs.ActivityUpdate,
        ),
        # null message, slco = 0b0000, no data inside, crc for zeroes is also zero
        (
            "00000000000000000000000000000000000000000000000000000000000000000000",
            SLCOs.NullMessage,
        ),
    ]

    for (burst, expected_slco) in bursts:
        on_air_bits = bitarray(burst)

        deinterleaved_all_bits = VBPTC6828.deinterleave_all_bits(on_air_bits)
        assert len(deinterleaved_all_bits) == 68

        deinterleaved_info_bits = VBPTC6828.deinterleave_data_bits(
            on_air_bits, include_crc8=True
        )
        assert len(deinterleaved_info_bits) == 36

        deinterleaved_data_bits = VBPTC6828.deinterleave_data_bits(
            on_air_bits, include_crc8=False
        )

        crc8_calculated: int = CRC8.calculate(deinterleaved_data_bits[:28])
        crc8_extracted: bitarray = VBPTC6828.deinterleave_crc8_bits(on_air_bits)
        assert crc8_extracted == int2ba(crc8_calculated, length=8, endian="little")
        slc: ShortLinkControl = ShortLinkControl.from_bits(deinterleaved_info_bits)
        assert slc.slco == expected_slco
        assert slc.crc_8bit == int2ba(crc8_calculated, length=8, endian="little")
        assert slc.as_bits() == deinterleaved_info_bits
        assert len(repr(slc))

        crc_nulled: bitarray = deinterleaved_info_bits.copy()
        crc_nulled[28:] = 0
        slc_crc: ShortLinkControl = ShortLinkControl.from_bits(crc_nulled)
        assert slc_crc.crc_8bit == slc.crc_8bit

        encoded_all_bits = VBPTC6828.encode(deinterleaved_all_bits)
        encoded_data_bits = VBPTC6828.encode(deinterleaved_data_bits)
        encoded_info_bits = VBPTC6828.encode(deinterleaved_info_bits)
        encoded_lc = VBPTC6828.encode(slc.as_bits())

        assert encoded_all_bits == encoded_data_bits
        assert encoded_data_bits == encoded_info_bits
        assert encoded_info_bits == on_air_bits
        assert encoded_lc == on_air_bits
