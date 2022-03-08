from typing import Union, Optional

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.defined_data_formats import DefinedDataFormats
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.resynchronize_flag import ResynchronizeFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sarq import SARQ
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class DataHeader(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 8.2.1 Header block structure
    """

    def __init__(
        self,
        dpf: DataPacketFormats,
        crc: bitarray,
        # some common fields
        is_group: Union[int, bool] = False,
        is_response_requested: Union[int, bool] = False,
        pad_octet_count: int = 0,
        sap_identifier: Optional[SAPIdentifier] = None,
        llid_destination: int = 0,
        llid_source: int = 0,
        full_message_flag: Optional[FullMessageFlag] = None,
        blocks_to_follow: int = 0,
        resynchronize_flag: Optional[ResynchronizeFlag] = None,
        send_sequence_number: int = 0,
        fragment_sequence_number: int = 0,
        # Confirmed Response packet Header (C_RHEAD) PDU
        response_class: int = 0,
        response_type: int = 0,
        response_status: int = 0,
        # Defined Data short data packet Header (DD_HEAD) PDU
        appended_blocks: int = 0,
        defined_data_format: Optional[DefinedDataFormats] = None,
        sarq: Optional[SARQ] = None,
    ):
        self.data_packet_format: DataPacketFormats = dpf
        # todo implement auto calculation from trimmed as_bits result
        self.crc: bitarray = crc
        self.is_group: bool = is_group in (True, 1)
        self.is_response_requested: bool = is_response_requested in (True, 1)
        self.pad_octet_count: int = pad_octet_count
        self.sap_identifier: Optional[SAPIdentifier] = sap_identifier
        self.llid_destination: int = llid_destination
        self.llid_source: int = llid_source
        self.full_message_flag: Optional[FullMessageFlag] = full_message_flag
        self.blocks_to_follow: int = blocks_to_follow
        self.resynchronize_flag: Optional[ResynchronizeFlag] = resynchronize_flag
        self.send_sequence_number: int = send_sequence_number
        self.fragment_sequence_number: int = fragment_sequence_number
        # Confirmed Response packet Header (C_RHEAD) PDU
        self.response_class: int = response_class
        self.response_type: int = response_type
        self.response_status: int = response_status
        # Defined Data short data packet Header (DD_HEAD) PDU
        self.appended_blocks: int = appended_blocks
        self.defined_data_format: Optional[DefinedDataFormats] = defined_data_format
        self.sarq: Optional[SARQ] = sarq

    def __repr__(self):
        descr: str = f"[{self.data_packet_format}] "

        if self.data_packet_format == DataPacketFormats.DataPacketConfirmed:
            descr += (
                f"[{self.sap_identifier}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[PAD OCTETS: {self.pad_octet_count}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] [{self.resynchronize_flag}] [N(S): {self.send_sequence_number}] "
                + f"[FSN: {self.fragment_sequence_number}]"
            )
        elif self.data_packet_format == DataPacketFormats.DataPacketUnconfirmed:
            descr += (
                f"[{self.sap_identifier}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[PAD OCTETS: {self.pad_octet_count}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] "
                + f"[FSN: {self.fragment_sequence_number}]"
            )
        elif self.data_packet_format == DataPacketFormats.ResponsePacket:
            descr += (
                f"[{self.sap_identifier}] "
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[RESPONSE TYPE: {self.response_type} CLASS: {self.response_class} STATUS: {self.response_status}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] "
            )
        elif self.data_packet_format == DataPacketFormats.ShortDataDefined:
            descr += (
                f"[{self.sap_identifier}] [{self.defined_data_format}] [{self.sarq}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[APPENDED BLOCKS: {self.appended_blocks}] "
            )
        else:
            raise KeyError(f"__repr__ not implemented for {self.data_packet_format}")

        return descr

    @staticmethod
    def from_bits(bits: bitarray) -> "DataHeader":
        dpf: DataPacketFormats = DataPacketFormats.from_bits(bits[4:8])
        print(f"{dpf} {bits.tobytes().hex()}")
        if dpf == DataPacketFormats.DataPacketConfirmed:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_group=bits[0],
                is_response_requested=bits[1],
                pad_octet_count=(bits[3] << 4) + ba2int(bits[12:16]),
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                llid_destination=ba2int(bits[16:40]),
                llid_source=ba2int(bits[40:64]),
                full_message_flag=FullMessageFlag(bits[64]),
                blocks_to_follow=ba2int(bits[65:72]),
                resynchronize_flag=ResynchronizeFlag(bits[72]),
                send_sequence_number=ba2int(bits[73:76]),
                fragment_sequence_number=ba2int(bits[76:80]),
            )
        elif dpf == DataPacketFormats.ResponsePacket:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_response_requested=bits[1],
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                llid_source=ba2int(bits[16:40]),
                llid_destination=ba2int(bits[40:64]),
                full_message_flag=FullMessageFlag(bits[64]),
                blocks_to_follow=ba2int(bits[65:72]),
                response_class=ba2int(bits[72:74]),
                response_type=ba2int(bits[74:76]),
                response_status=ba2int(bits[76:78]),
            )
        elif dpf == DataPacketFormats.ShortDataDefined:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_group=bits[0],
                is_response_requested=bits[1],
                appended_blocks=ba2int(bits[2:4]) << 4 + ba2int(bits[12:16]),
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                llid_source=ba2int(bits[16:40]),
                llid_destination=ba2int(bits[40:64]),
                defined_data_format=DefinedDataFormats.from_bits(bits[64:70]),
                sarq=SARQ(bits[70]),
                full_message_flag=FullMessageFlag(bits[71]),
            )
        elif dpf == DataPacketFormats.DataPacketUnconfirmed:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_group=bits[0],
                is_response_requested=bits[1],
                pad_octet_count=(bits[3] << 4) + ba2int(bits[12:16]),
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                llid_destination=ba2int(bits[16:40]),
                llid_source=ba2int(bits[40:64]),
                full_message_flag=FullMessageFlag(bits[64]),
                blocks_to_follow=ba2int(bits[65:72]),
                fragment_sequence_number=ba2int(bits[76:80]),
            )
        else:
            raise KeyError(f"from_bits not implemented for {dpf}")
