from typing import Union, Optional

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.etsi.crc.crc16 import CRC16
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.defined_data_formats import DefinedDataFormats
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.resynchronize_flag import ResynchronizeFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sarq import SARQ
from okdmr.dmrlib.etsi.layer2.elements.supplementary_flag import SupplementaryFlag
from okdmr.dmrlib.etsi.layer2.elements.udt_format import UDTFormat
from okdmr.dmrlib.etsi.layer3.elements.udt_option_flag import UDTOptionFlag
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class DataHeader(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 8.2.1 Header block structure
    """

    def __init__(
        self,
        dpf: DataPacketFormats,
        crc: Optional[bitarray],
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
        bit_padding: Optional[bitarray] = bitarray(),
        # Unified Data Transport Header (UDT_HEAD) PDU
        is_emergency: Union[int, bool] = False,
        udt_option_flag: Optional[UDTOptionFlag] = None,
        pad_nibbles_count: int = 0,
        udt_format: Optional[UDTFormat] = None,
        udt_opcode: Optional[CsbkOpcodes] = None,
        supplementary_flag: Optional[SupplementaryFlag] = None,
    ):
        self.data_packet_format: DataPacketFormats = dpf
        self.crc: bitarray = crc or bitarray()
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
        self.bit_padding: bitarray = bit_padding
        # Unified Data Transport Header (UDT_HEAD) PDU
        self.is_emergency: bool = is_emergency in (True, 1)
        self.udt_option_flag: Optional[UDTOptionFlag] = udt_option_flag
        self.pad_nibbles_count: int = pad_nibbles_count
        self.udt_format: Optional[UDTFormat] = udt_format
        self.udt_opcode: Optional[CsbkOpcodes] = udt_opcode
        self.supplementary_flag: Optional[SupplementaryFlag] = supplementary_flag

        if len(self.crc) < 16 or ba2int(self.crc) <= 0:
            self.crc_ok: bool = True
            self.crc = int2ba(
                CRC16.calculate(self.as_bits()[:-16].tobytes(), CrcMasks.DataHeader),
                length=16,
            )
        else:
            self.crc_ok: bool = CRC16.check(
                self.as_bits()[:-16].tobytes(), ba2int(self.crc), CrcMasks.DataHeader
            )

    def __repr__(self):
        descr: str = f"[{self.data_packet_format}] "

        if self.data_packet_format == DataPacketFormats.DataPacketConfirmed:
            descr += (
                f"{'[CRC INVALID] ' if not self.crc_ok else ''}"
                + f"[{self.sap_identifier}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[PAD OCTETS: {self.pad_octet_count}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] [{self.resynchronize_flag}] [N(S): {self.send_sequence_number}] "
                + f"[FSN: {self.fragment_sequence_number}]"
            )
        elif self.data_packet_format == DataPacketFormats.DataPacketUnconfirmed:
            descr += (
                f"{'[CRC INVALID] ' if not self.crc_ok else ''}"
                + f"[{self.sap_identifier}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[PAD OCTETS: {self.pad_octet_count}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] "
                + f"[FSN: {self.fragment_sequence_number}]"
            )
        elif self.data_packet_format == DataPacketFormats.ResponsePacket:
            descr += (
                f"{'[CRC INVALID] ' if not self.crc_ok else ''}"
                + f"[{self.sap_identifier}] "
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[RESPONSE TYPE: {self.response_type} CLASS: {self.response_class} STATUS: {self.response_status}] "
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[BTF: {self.blocks_to_follow}] "
            )
        elif self.data_packet_format == DataPacketFormats.ShortDataDefined:
            descr += (
                f"{'[CRC INVALID] ' if not self.crc_ok else ''}"
                + f"[{self.sap_identifier}] [{self.defined_data_format}] [{self.sarq}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.full_message_flag}] "
                + f"[APPENDED BLOCKS: {self.appended_blocks}] "
            )
        elif self.data_packet_format == DataPacketFormats.UnifiedDataTransport:
            descr += (
                f"{'[CRC INVALID] ' if not self.crc_ok else ''}"
                + f"[{self.sap_identifier}] [{self.udt_format}] [UDT Opcode: {self.udt_opcode}] "
                + ("[GROUP] " if self.is_group else "[INDIVIDUAL] ")
                + ("[RESPONSE REQUESTED] " if self.is_response_requested else "")
                + f"[SOURCE: {self.llid_source}] [DESTINATION: {self.llid_destination}] [{self.supplementary_flag}] "
            )
        else:
            raise KeyError(f"__repr__ not implemented for {self.data_packet_format}")

        return descr

    def as_bits(self) -> bitarray:
        if self.data_packet_format == DataPacketFormats.DataPacketConfirmed:
            poc = int2ba(self.pad_octet_count, length=5)
            return (
                bitarray([self.is_group, self.is_response_requested, 0, poc[0]])
                + self.data_packet_format.as_bits()
                + self.sap_identifier.as_bits()
                + poc[1:]
                + int2ba(self.llid_destination, length=24)
                + int2ba(self.llid_source, length=24)
                + bitarray([self.full_message_flag.value])
                + int2ba(self.blocks_to_follow, length=7)
                + bitarray([self.resynchronize_flag.value])
                + int2ba(self.send_sequence_number, length=3)
                + int2ba(self.fragment_sequence_number, length=4)
                + self.crc
            )
        elif self.data_packet_format == DataPacketFormats.DataPacketUnconfirmed:
            poc = int2ba(self.pad_octet_count, length=5)
            return (
                bitarray([self.is_group, self.is_response_requested, 0, poc[0]])
                + self.data_packet_format.as_bits()
                + self.sap_identifier.as_bits()
                + poc[1:]
                + int2ba(self.llid_destination, length=24)
                + int2ba(self.llid_source, length=24)
                + bitarray([self.full_message_flag.value])
                + int2ba(self.blocks_to_follow, length=7)
                + bitarray([0] * 4)
                + int2ba(self.fragment_sequence_number, length=4)
                + self.crc
            )
        elif self.data_packet_format == DataPacketFormats.ResponsePacket:
            return (
                bitarray([0] * 4)
                + self.data_packet_format.as_bits()
                + self.sap_identifier.as_bits()
                + bitarray([0] * 4)
                + int2ba(self.llid_destination, length=24)
                + int2ba(self.llid_source, length=24)
                + bitarray([self.full_message_flag.value])
                + int2ba(self.blocks_to_follow, length=7)
                + int2ba(self.response_class, length=2)
                + int2ba(self.response_type, length=3)
                + int2ba(self.response_status, length=3)
                + self.crc
            )
        elif self.data_packet_format == DataPacketFormats.ShortDataDefined:
            ab = int2ba(self.appended_blocks, length=6)
            return (
                bitarray([self.is_group, self.is_response_requested, ab[0], ab[1]])
                + self.data_packet_format.as_bits()
                + self.sap_identifier.as_bits()
                + ab[2:]
                + int2ba(self.llid_destination, length=24)
                + int2ba(self.llid_source, length=24)
                + self.defined_data_format.as_bits()
                + bitarray([self.sarq.value, self.full_message_flag.value])
                + self.bit_padding
                + self.crc
            )
        elif self.data_packet_format == DataPacketFormats.UnifiedDataTransport:
            return (
                bitarray(
                    [
                        self.is_group,
                        self.is_response_requested,
                        self.is_emergency,
                        self.udt_option_flag.value,
                    ]
                )
                + self.data_packet_format.as_bits()
                + self.sap_identifier.as_bits()
                + self.udt_format.as_bits()
                + int2ba(self.llid_destination, length=24)
                + int2ba(self.llid_source, length=24)
                + int2ba(self.pad_nibbles_count, length=5)
                + bitarray([0])
                + int2ba(self.appended_blocks, length=2)
                + bitarray([self.supplementary_flag.value, 0])
                + self.udt_opcode.as_bits()
                + self.crc
            )
        raise ValueError(f"as_bits not implemented for {self.data_packet_format}")

    @staticmethod
    def from_bits(bits: bitarray) -> "DataHeader":
        dpf: DataPacketFormats = DataPacketFormats.from_bits(bits[4:8])
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
                llid_destination=ba2int(bits[16:40]),
                llid_source=ba2int(bits[40:64]),
                full_message_flag=FullMessageFlag(bits[64]),
                blocks_to_follow=ba2int(bits[65:72]),
                response_class=ba2int(bits[72:74]),
                response_type=ba2int(bits[74:77]),
                response_status=ba2int(bits[77:80]),
            )
        elif dpf == DataPacketFormats.ShortDataDefined:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_group=bits[0],
                is_response_requested=bits[1],
                appended_blocks=ba2int(bits[2:4] + bits[12:16]),
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                llid_destination=ba2int(bits[16:40]),
                llid_source=ba2int(bits[40:64]),
                defined_data_format=DefinedDataFormats.from_bits(bits[64:70]),
                sarq=SARQ(bits[70]),
                full_message_flag=FullMessageFlag(bits[71]),
                bit_padding=bits[72:80],
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
        elif dpf == DataPacketFormats.UnifiedDataTransport:
            return DataHeader(
                dpf=dpf,
                crc=bits[80:96],
                is_group=bits[0],
                is_response_requested=bits[1],
                is_emergency=bits[2],
                udt_option_flag=UDTOptionFlag(bits[3]),
                sap_identifier=SAPIdentifier.from_bits(bits[8:12]),
                udt_format=UDTFormat.from_bits(bits[12:16]),
                llid_destination=ba2int(bits[16:40]),
                llid_source=ba2int(bits[40:64]),
                pad_nibbles_count=ba2int(bits[64:69]),
                appended_blocks=ba2int(bits[70:72]),
                supplementary_flag=SupplementaryFlag(bits[72]),
                udt_opcode=CsbkOpcodes.from_bits(bits[74:80]),
            )
        else:
            raise KeyError(f"from_bits not implemented for {dpf}")
