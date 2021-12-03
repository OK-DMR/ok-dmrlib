from typing import Any, Dict

from numpy import array_equal
from okdmr.kaitai.etsi.dmr_csbk import DmrCsbk
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.general_data_burst import GeneralDataBurst
from okdmr.dmrlib.etsi.layer2.sync_patterns import SyncPattern


def test_bptc19696_maps():
    assert len(BPTC19696.INTERLEAVING_INDICES) == 196, "Indices must be 196 bits"
    assert (
        len(BPTC19696.FULL_INTERLEAVING_MAP) == 196
    ), "Full interleave map must be 196 bits"
    assert (
        len(BPTC19696.FULL_DEINTERLEAVING_MAP) == 196
    ), "Full deinterleave map must be 196 bits"
    assert (
        len(BPTC19696.DEINTERLEAVE_INFO_BITS_ONLY_MAP) == 96
    ), "Data bits must be index 0-95 (total 96 bits)"


def test_bptc1969_decode_map_against_dmr_utils3():
    # fmt:off
    # taken from dmr_utils3/bptc.py method decode_full_lc, with added indexes of RS1293 FEC
    indexes: list = [
        136, 121, 106, 91, 76, 61, 46, 31,
        152, 137, 122, 107, 92, 77, 62, 47, 32,
        17, 2, 123, 108, 93, 78, 63, 48, 33, 18, 3, 184,
        169, 94, 79, 64, 49, 34, 19, 4, 185, 170, 155,
        140, 65, 50, 35, 20, 5, 186, 171, 156, 141,
        126, 111, 36, 21, 6, 187, 172, 157, 142, 127, 112,
        97, 82, 7, 188, 173, 158, 143, 128, 113, 98, 83,
        68, 53, 174, 159, 144, 129, 114, 99, 84,
        69, 54, 39, 24, 145, 130, 115, 100, 85, 70, 55, 40,
        25, 10, 191
    ]
    # fmt:on
    only_map_indexes: list = list(BPTC19696.DEINTERLEAVE_INFO_BITS_ONLY_MAP.values())
    assert array_equal(indexes, only_map_indexes)

    # fmt:off
    # index_181 taken from dmr_utils3/bptc.py
    index_181: tuple = (
        0, 181, 166, 151, 136, 121, 106, 91, 76, 61, 46, 31, 16, 1, 182, 167, 152, 137,
        122, 107, 92, 77, 62, 47, 32, 17, 2, 183, 168, 153, 138, 123, 108, 93, 78, 63,
        48, 33, 18, 3, 184, 169, 154, 139, 124, 109, 94, 79, 64, 49, 34, 19, 4, 185, 170,
        155, 140, 125, 110, 95, 80, 65, 50, 35, 20, 5, 186, 171, 156, 141, 126, 111, 96,
        81, 66, 51, 36, 21, 6, 187, 172, 157, 142, 127, 112, 97, 82, 67, 52, 37, 22, 7,
        188, 173, 158, 143, 128, 113, 98, 83, 68, 53, 38, 23, 8, 189, 174, 159, 144, 129,
        114, 99, 84, 69, 54, 39, 24, 9, 190, 175, 160, 145, 130, 115, 100, 85, 70, 55, 40,
        25, 10, 191, 176, 161, 146, 131, 116, 101, 86, 71, 56, 41, 26, 11, 192, 177, 162,
        147, 132, 117, 102, 87, 72, 57, 42, 27, 12, 193, 178, 163, 148, 133, 118, 103, 88,
        73, 58, 43, 28, 13, 194, 179, 164, 149, 134, 119, 104, 89, 74, 59, 44, 29, 14,
        195, 180, 165, 150, 135, 120, 105, 90, 75, 60, 45, 30, 15
    )
    deinterleave_map_indexes = (*list(BPTC19696.FULL_DEINTERLEAVING_MAP.keys()),)
    assert index_181 == deinterleave_map_indexes
    # fmt:on


def test_decode_mmdvm2020_csbks():
    packets: Dict[str, Dict[str, Any]] = {
        "444d52440223383b2338630006690f632e40c70153df0a83b7a8282c2509625014fdff57d75df5dcadde429028c87ae3341e24191c003c": {
            "preamble_csbk_blocks_to_follow": 29,
            "preamble_data_or_csbk": DmrCsbk.CsbkDataOrCsbk.data_content_follows_preambles,
            "preamble_source_address": 2308155,
            "preamble_target_address": 2308195,
            "feature_set_id": 0,
        }
    }
    for packet, testdata in packets.items():
        mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(packet))
        assert isinstance(mmdvm.command_data, Mmdvm2020.TypeDmrData)
        burst: GeneralDataBurst = GeneralDataBurst(mmdvm.command_data.dmr_data)
        assert burst.sync_or_embedded == SyncPattern.BsSourcedData
        assert burst.slot_type.data_type == DataTypes.CSBK.value
        csbk: DmrCsbk = DmrCsbk.from_bytes(burst.info_bits.tobytes())
        for propname, value in testdata.items():
            assert getattr(csbk, propname) == value
