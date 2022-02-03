from typing import List

from bitarray import bitarray
from bitarray.util import int2ba
from okdmr.kaitai.etsi.full_link_control import FullLinkControl
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.fec.five_bit_checksum import FiveBitChecksum
from okdmr.dmrlib.etsi.fec.vbptc_128_72 import VBPTC12873
from okdmr.dmrlib.transmission.burst_info import BurstInfo


def test_vbptc_sanity():
    assert len(VBPTC12873.FULL_DEINTERLEAVING_MAP) == 128
    assert len(VBPTC12873.DEINTERLEAVE_INFO_BITS_ONLY_MAP) == 72
    assert len(VBPTC12873.INTERLEAVING_INDICES) == 128
    assert len(VBPTC12873.INTERLEAVE_INFO_BITS_ONLY_MAP) == 72
    assert len(VBPTC12873.FULL_INTERLEAVING_MAP) == 128
    assert len(VBPTC12873.DEINTERLEAVE_5BIT_CHECKSUM) == 5


def test_encode_decode_vbptc():
    embedded_bits = bitarray(
        "00001010000000000000001100001010000101110000101000000110000001010000110000010001001000100000000000000101001000100011111100111010"
    )
    deinterleaved_all_bits = VBPTC12873.deinterleave_all_bits(embedded_bits)
    assert len(deinterleaved_all_bits) == 128
    deinterleaved_data_bits = VBPTC12873.deinterleave_data_bits(
        embedded_bits, include_cs5=True
    )
    assert len(deinterleaved_data_bits) == 77
    cs5_calculated: int = FiveBitChecksum.calculate(
        deinterleaved_data_bits.tobytes()[:9]
    )
    cs5_extractd: bitarray = VBPTC12873.deinterleave_cs5_bits(embedded_bits)
    assert cs5_extractd == int2ba(cs5_calculated, length=5)
    lc: FullLinkControl = FullLinkControl.from_bytes(deinterleaved_data_bits.tobytes())
    assert lc.feature_set_id == FullLinkControl.FeatureSetIds.standardized_ts_102_361_2
    assert not hasattr(lc, "crc_checksum")
    assert hasattr(lc, "cs5_checksum")
    assert lc.cs5_checksum == cs5_calculated

    encoded_data_bits = VBPTC12873.encode(deinterleaved_data_bits[:72])
    encoded_all_bits = VBPTC12873.encode(deinterleaved_all_bits)
    assert encoded_data_bits == embedded_bits


def test_extract_embedded_signalling():
    bursts: List[str] = [
        "444d52446920baf80008650020baef81212a684978f8e0361b6519cdd55ad9c3301130a00030a91b7529dee349fbe3147e040bc9d10000",
        "444d52446a20baf80008650020baef82212a6849c762a2114c736c7a45f562c133617170a06057439c9df11e936ec26335ecf569bf0000",
        "444d52446b20baf80008650020baef83212a6849f30c872376d6102d4791df85442170c112200747b289e11dd5c2877046b1e36bcf0000",
        "444d52446c20baf80008650020baef84212a6849e1e48370246e951422bda7c73511505223f3a07309cda701bdb6e4733318ef91220000",
        "444d52446d20baf80008650020baef85212a6849d5098044132a3761cbc708807701100000000e211a1324cbacb5c675371ddee0130000",
    ]
    for burst in bursts:
        mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(burst))
        assert isinstance(mmdvm.command_data, Mmdvm2020.TypeDmrData)
        burst_info: BurstInfo = BurstInfo(mmdvm.command_data.dmr_data)
        assert burst_info.has_emb
