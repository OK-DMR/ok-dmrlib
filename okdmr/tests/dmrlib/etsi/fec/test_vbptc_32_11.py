from typing import List

from bitarray import bitarray
from okdmr.dmrlib.etsi.fec.vbptc_32_11 import VBPTC3211


def test_vbptc_sanity():
    assert len(VBPTC3211.FULL_DEINTERLEAVING_MAP) == 32
    assert len(VBPTC3211.DEINTERLEAVE_INFO_BITS_ONLY_MAP) == 11
    assert len(VBPTC3211.INTERLEAVING_INDICES) == 32
    assert len(VBPTC3211.INTERLEAVE_INFO_BITS_ONLY_MAP) == 11
    assert len(VBPTC3211.FULL_INTERLEAVING_MAP) == 32


def test_encode_decode_vbptc():
    bursts: List[(str,)] = [
        ("00000100010110000000100010100100",),
        # following are not valid vbptc protected payloads, probably something proprietary / unidentified
        # ("00001100000100010010010001000001",),
        # ("00010111000010100000011001000100",),
    ]

    for (burst,) in bursts:
        on_air_bits = bitarray(burst)

        deinterleaved_all_bits = VBPTC3211.deinterleave_all_bits(on_air_bits)
        assert len(deinterleaved_all_bits) == 32

        deinterleaved_info_bits = VBPTC3211.deinterleave_data_bits(on_air_bits)
        assert len(deinterleaved_info_bits) == 11

        deinterleaved_data_bits = VBPTC3211.deinterleave_data_bits(on_air_bits)

        encoded_all_bits = VBPTC3211.encode(deinterleaved_all_bits)
        encoded_data_bits = VBPTC3211.encode(deinterleaved_data_bits)
        encoded_info_bits = VBPTC3211.encode(deinterleaved_info_bits)

        assert encoded_all_bits == encoded_data_bits
        assert encoded_data_bits == encoded_info_bits
        assert encoded_info_bits == on_air_bits
