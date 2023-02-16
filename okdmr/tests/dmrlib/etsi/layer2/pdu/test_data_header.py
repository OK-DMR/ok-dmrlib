from typing import Dict

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.defined_data_formats import DefinedDataFormats
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.resynchronize_flag import ResynchronizeFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sarq import SARQ
from okdmr.dmrlib.etsi.layer2.elements.supplementary_flag import SupplementaryFlag
from okdmr.dmrlib.etsi.layer2.elements.udt_format import UDTFormat
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_crc():
    orig: bitarray = bitarray(
        "010000110100111000100011001110000110001100100011001110000011101110000100000010000001100011000001"
    )
    dh: DataHeader = DataHeader.from_bits(orig)
    assert dh.crc_ok
    auto_crc: DataHeader = DataHeader.from_bits(orig[:-16] + bitarray(16 * "0"))
    assert dh.crc == auto_crc.crc


def test_data_headers():
    pdus: Dict[str, Dict[str, any]] = {
        "023a2337fc2337fe820081a3": {
            "data_packet_format": DataPacketFormats.DataPacketUnconfirmed,
            "sap_identifier": SAPIdentifier.UDP_IP_compression,
            "is_group": False,
            "llid_source": 2308094,
            "llid_destination": 2308092,
            "blocks_to_follow": 2,
        },
        "01402337fc2337fe000ff83a": {
            "data_packet_format": DataPacketFormats.ResponsePacket,
            "sap_identifier": SAPIdentifier.IP_PacketData,
            "full_message_flag": FullMessageFlag.SubsequentTry,
        },
        "434e2337fe2337fc84781bd1": {
            "data_packet_format": DataPacketFormats.DataPacketConfirmed,
            "is_response_requested": True,
            "resynchronize_flag": ResynchronizeFlag.DoNotSync,
        },
        "4da123386323383b05005757": {
            "data_packet_format": DataPacketFormats.ShortDataDefined,
            "defined_data_format": DefinedDataFormats.BCD,
            "sap_identifier": SAPIdentifier.ShortData,
            "sarq": SARQ.NotRequired,
            "full_message_flag": FullMessageFlag.FirstTryToCompletePacket,
            "appended_blocks": 1,
        },
        "800500010627fce7001bacaf": {
            "udt_format": UDTFormat.LocationNMEA,
            "udt_opcode": CsbkOpcodes.UnifiedDataTransportInboundHeader,
            "sap_identifier": SAPIdentifier.UDT,
            "supplementary_flag": SupplementaryFlag.ShortData,
        },
    }
    for pduhex, validations in pdus.items():
        _bytes = bytes.fromhex(pduhex)
        _bits = bytes_to_bits(_bytes)
        dh: DataHeader = DataHeader.from_bits(_bits)
        for key, val in validations.items():
            assert getattr(dh, key) == val
        # also tests for availability of __repr__ for given DPF
        assert len(repr(dh))

        assert dh.as_bits() == _bits
        nulled_crc = _bits.copy()
        nulled_crc[80:] = 0
        assert DataHeader.from_bits(nulled_crc).as_bits() == _bits
        assert DataHeader.from_bytes(_bytes).as_bytes() == _bytes
        assert (
            (dh.get_blocks_to_follow() is None)
            if dh.data_packet_format == DataPacketFormats.UnifiedDataTransport
            else isinstance(dh.get_blocks_to_follow(), int)
        )


def test_kairos_header():
    header: DataHeader = DataHeader.from_bits(
        bytes_to_bits(bytes.fromhex("8DA300000100000101002B97"))
    )
    # [DataPacketFormats.ShortDataDefined] [SAPIdentifier.ShortData] [DefinedDataFormats.Binary] [SARQ.NotRequired] [TARGET IS GROUP] [SOURCE: 1] [DESTINATION: 1] [FullMessageFlag.FirstTryToCompletePacket] [APPENDED BLOCKS: 3]
    print(repr(header))
    assert isinstance(header, DataHeader)

    dh: DataHeader = DataHeader.from_bits(
        bytes_to_bits(bytes.fromhex("8DA000000100000101002B97"))
    )
    # [DataPacketFormats.ShortDataDefined] [CRC INVALID] [SAPIdentifier.ShortData] [DefinedDataFormats.Binary] [SARQ.NotRequired] [TARGET IS GROUP] [SOURCE: 1] [DESTINATION: 1] [FullMessageFlag.FirstTryToCompletePacket] [APPENDED BLOCKS: 0]
    print(repr(dh))

    dh: DataHeader = DataHeader.from_bits(
        bytes_to_bits(bytes.fromhex("8DA30000010008350100B731"))
    )
    # [DataPacketFormats.ShortDataDefined] [SAPIdentifier.ShortData] [DefinedDataFormats.Binary] [SARQ.NotRequired] [TARGET IS GROUP] [SOURCE: 2101] [DESTINATION: 1] [FullMessageFlag.FirstTryToCompletePacket] [APPENDED BLOCKS: 3]
    print(repr(dh))

    dh: DataHeader = DataHeader.from_bits(
        bytes_to_bits(bytes.fromhex("8DA300000100000101002B97"))
    )
    print(repr(dh))
