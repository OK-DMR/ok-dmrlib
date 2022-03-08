from typing import Dict

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.defined_data_formats import DefinedDataFormats
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.resynchronize_flag import ResynchronizeFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sarq import SARQ
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader


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
        "4da123386323383b05104566": {
            "defined_data_format": DefinedDataFormats.BCD,
            "sap_identifier": SAPIdentifier.ShortData,
            "sarq": SARQ.NotRequired,
            "full_message_flag": FullMessageFlag.FirstTryToCompletePacket,
            "appended_blocks": 0,
        },
    }
    for pduhex, validations in pdus.items():
        _bits = bitarray()
        _bits.frombytes(bytes.fromhex(pduhex))
        dh: DataHeader = DataHeader.from_bits(_bits)
        for key, val in validations.items():
            assert getattr(dh, key) == val
        # also tests for availability of __repr__ for given DPF
        assert len(repr(dh))
