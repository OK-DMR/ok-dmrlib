from typing import List
import pytest

from bitarray import bitarray
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


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
        # CsbkOpcodes.Protect
        # "101011110000000000000000000001000001000000010010101111110001000000010010110100001000001001111001",
        # CsbkOpcodes.AnnouncementPDUsWithoutResponse
        "101010000000000000110110100000001001011011010000000001111100000000000000110011101001101100111001",
        # CsbkOpcodes.AlohaPDUsForRandomAccessProtocol
        "100110010000000000001001000000001111011011010000000001110000000000000000000000000010110001101101",
        #
    ]
    for binstr in csbks:
        _bits = bitarray(binstr)
        csbk = CSBK.from_bits(_bits)
        assert len(repr(csbk))
        assert csbk.feature_set == FeatureSetIDs.StandardizedFID
        assert _bits == csbk.as_bits()
        print(repr(csbk))


def test_hytera_ipsc_sync():
    csbks: List[str] = [
        # [CsbkOpcodes.HyteraIPSCSync] [LB: 1] [PF: 0] [FeatureSetIDs.HyteraFID] [HYTERA IPSC SYNC data-hex(0008fd2337fdf020)]
        "88100008fd2337fdf020e68b"
    ]
    for binstr in csbks:
        _bits = bytes_to_bits(bytes.fromhex(binstr))
        csbk = CSBK.from_bits(_bits)
        assert csbk.feature_set == FeatureSetIDs.MotorolaLtd
        assert csbk.as_bits() == _bits
        assert len(repr(csbk))


def test_kairos_csbk():
    csbks: List[str] = [
        "B800 0000 FFFF FF00 00CA 640B",
        "BD00 C006 0000 0100 00CA 3F08",
        "BD00 C005 0000 0100 00CA E78A",
        "BD00 C004 0000 0100 00CA 5FEB",
    ]
    for hexpdu in csbks:
        csbk: CSBK = CSBK.from_bits(
            bytes_to_bits(bytes.fromhex(hexpdu.replace(" ", "")))
        )
        print(repr(csbk))
        assert isinstance(csbk, CSBK), f"Payload is not a valid CSBK data"


class TestCSBKOs:
    def test_unknown_csbkos(self):
        with pytest.raises(NotImplementedError):
            bits = (
                bitarray([1, 0])
                + CsbkOpcodes.AcknowledgementResponseInboundTSCC.as_bits()
                + FeatureSetIDs.StandardizedFID.as_bits()
                + bitarray([0] * 80)
            )
            CSBK.from_bits(bits)
