from typing import List, Dict, Any

from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.vbptc_128_72 import VBPTC12873
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_embedded_lc():
    hex_messages: Dict[str, Dict[str, Any]] = {
        "0300030a0f0006060f033a030c393530": {
            "full_link_control_opcode": FLCOs.GroupVoiceChannelUser,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "source_address": 2145007,
            "group_address": 6,
        },
        "03000a03060906060f03030a05000c09": {
            "full_link_control_opcode": FLCOs.GroupVoiceChannelUser,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "source_address": 2145007,
            "group_address": 9,
        },
        "0a00030a170a06050c11220005223f3a": {
            "full_link_control_opcode": FLCOs.GroupVoiceChannelUser,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "source_address": 2145016,
            "group_address": 2149,
        },
        "0a00030a170906060f12110305120f0a": {
            "full_link_control_opcode": FLCOs.GroupVoiceChannelUser,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "source_address": 2145007,
            "group_address": 2149,
        },
    }
    for hexmsg, assertdict in hex_messages.items():
        bits: bitarray = bytes_to_bits(bytes.fromhex(hexmsg))
        vbptc: bitarray = VBPTC12873.deinterleave_data_bits(bits=bits, include_cs5=True)
        lc: FullLinkControl = FullLinkControl.from_bits(vbptc)
        for key, val in assertdict.items():
            assert getattr(lc, key) == val
