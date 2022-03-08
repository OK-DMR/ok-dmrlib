from typing import List

from bitarray import bitarray
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK


def test_single_csbk():
    mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(
        bytes.fromhex(
            "444d52440923383b0008fd0006690fe33391012951dd0c4d8bb40ac413a86c5094fdff57d75df5dcadfa1268aaa87b82b9d8291910003c"
        )
    )
    burst: Burst = Burst.from_mmdvm(mmdvm.command_data)
    csbk = CSBK.from_bits(burst.info_bits_deinterleaved)
    assert csbk.last_block
    assert not csbk.protect_flag
    assert csbk.csbko == CsbkOpcodes.PreambleCSBK
    assert csbk.feature_set == FeatureSetIDs.StandardizedFID
    assert csbk.target_address == 2301
    assert csbk.source_address == 2308155
    assert csbk.as_bits() == burst.info_bits_deinterleaved
    zerocrc = burst.info_bits_deinterleaved.copy()
    zerocrc[-16:] = 0
    assert (
        CSBK.from_bits(zerocrc).as_bits()
        == csbk.as_bits()
        == burst.info_bits_deinterleaved
    )
    assert len(repr(csbk))


def test_csbk():
    csbks: List[str] = [
        # preamble
        "101111010000000000000000000000010000000000000001100110100000000000000001100111000101011011001110",
        # channel timing
        "100001110000000000000001010000010000000000000000001010000000000000000000000100010011000001010111",
        # bs outbound activation
        "101110000000000000000000000000000000000000000000011001010000000000000000110010101100010000101111",
        # unit-to-unit voice service request
        "100001000000000000000000000000000000010011100011101001000000010011100011100100011110101000011010",
        # unit-to-unit voice service answer-response
        "100001010000000000000000001000000000010011100011100100010000010011100011101001000001110111110011",
        # negative acknowledgement response
        "101001100000000011000100001000010000011001101001111000000000011001101001110101100011011001110101",
        # following are CsbkOpcodes.UnifiedDataTransportForDGNAOutboundHeader, Tier III, with Manufacturer FID, not yet implemented
        # "101001000001000000000000000000000000000000000001100111000000000000000001100110100100101110010110",
        # "101001000001000000000000100000000000000000000001100111000000000000000001100110101110000001101111"
    ]
    for binstr in csbks:
        _bits = bitarray(binstr)
        csbk = CSBK.from_bits(_bits)
        assert len(repr(csbk))
        assert csbk.feature_set == FeatureSetIDs.StandardizedFID
        assert _bits == csbk.as_bits()
