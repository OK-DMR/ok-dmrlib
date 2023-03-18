from typing import Dict, Any

from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.vbptc_128_72 import VBPTC12873
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer3.elements.position_error import PositionError
from okdmr.dmrlib.etsi.layer3.elements.talker_alias_data_format import (
    TalkerAliasDataFormat,
)
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
        "09001d17271e81b730060c9a9a8e09b1": {
            "full_link_control_opcode": FLCOs.UnitToUnitVoiceChannelUser,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "source_address": 250997,
            "target_address": 2504105,
        },
        "2100122d8d1b3318305a5c2debb7c92d": {
            "full_link_control_opcode": FLCOs.GPSInfo,
            "feature_set_id": FeatureSetIDs.StandardizedFID,
            "position_error": PositionError.PositionErrorNotKnown,
        },
        "2114001200c350034b4b12ac568b74a0": {
            "full_link_control_opcode": FLCOs.TalkerAliasHeader,
            "talker_alias_data_format": TalkerAliasDataFormat.UnicodeUTF16LE,
            "talker_alias_data_length": 13,
        },
        "0009002100810581211139091d09b48d": {
            "full_link_control_opcode": FLCOs.TalkerAliasBlock1,
            "talker_alias_data": b"\x00" + "BP ".encode("utf-16-le"),
        },
    }
    for hexmsg, assertdict in hex_messages.items():
        bits: bitarray = bytes_to_bits(bytes.fromhex(hexmsg))
        vbptc: bitarray = VBPTC12873.deinterleave_data_bits(bits=bits, include_cs5=True)
        lc: FullLinkControl = FullLinkControl.from_bits(vbptc)
        if not len(assertdict):
            print(repr(lc))

        try:
            assert len(repr(lc))
        except KeyError as e:
            assert False, f"{e}"

        for key, val in assertdict.items():
            assert getattr(lc, key) == val

        assert lc.as_bits() == vbptc


def test_assemble_talker_alias():
    header = FullLinkControl.from_bits(
        bytes_to_bits(bytes.fromhex("0400da00520034005748"))[:-3]
    )
    block1 = FullLinkControl.from_bits(
        bytes_to_bits(bytes.fromhex("050000420050002000e0"))[:-3]
    )
    block2 = FullLinkControl.from_bits(
        bytes_to_bits(bytes.fromhex("060044006d0069007408"))[:-3]
    )
    block3 = FullLinkControl.from_bits(
        bytes_to_bits(bytes.fromhex("070000720069006900a8"))[:-3]
    )

    assert header.talker_alias_data_format == TalkerAliasDataFormat.UnicodeUTF16LE
    # 13 UTF16LE characters
    assert header.talker_alias_data_length == 13
    # MSB must be false for 8-bit or 16-bit coding
    assert not header.talker_alias_data_msb

    text = (
        header.talker_alias_data
        + block1.talker_alias_data
        + block2.talker_alias_data
        + block3.talker_alias_data
    )
    assert text[1:].decode("utf-16-le") == "R4WBP Dmitrii"
