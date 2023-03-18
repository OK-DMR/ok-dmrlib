from typing import Union, Optional, Dict, Literal

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.etsi.crc.crc16 import CRC16
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer3.elements.additional_information_field import (
    AdditionalInformationField,
)
from okdmr.dmrlib.etsi.layer3.elements.announcement_type import AnnouncementType
from okdmr.dmrlib.etsi.layer3.elements.answer_response import AnswerResponse
from okdmr.dmrlib.etsi.layer3.elements.channel_timing_opcode import ChannelTimingOpcode
from okdmr.dmrlib.etsi.layer3.elements.dynamic_identifier import DynamicIdentifier
from okdmr.dmrlib.etsi.layer3.elements.random_access_service_function import (
    RandomAccessServiceFunction,
)
from okdmr.dmrlib.etsi.layer3.elements.reason_code import ReasonCode
from okdmr.dmrlib.etsi.layer3.elements.service_options import ServiceOptions
from okdmr.dmrlib.etsi.layer3.elements.source_type import SourceType
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


class CSBK(BitsInterface, BytesInterface):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.1.2  Control Signalling BlocK (CSBK) PDUs
    """

    TSCC_BACKOFF_MAP: Dict[int, int] = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 8,
        7: 11,
        8: 15,
        9: 20,
        10: 26,
        11: 33,
        12: 41,
        13: 50,
        14: 70,
        15: 100,
    }

    def __init__(
        self,
        csbko: CsbkOpcodes,
        last_block: Union[bool, int] = True,
        protect_flag: Union[bool, int] = False,
        manufacturers_feature_set_id: FeatureSetIDs = FeatureSetIDs.StandardizedFID,
        # default value for crc indicates, it must be recalculated on construct
        crc: int = 0,
        # bs outbound activation fields
        bs_address: int = 0,
        source_address: int = 0,
        # unit to unit voice service request fields
        service_options: Optional[ServiceOptions] = None,
        target_address: int = 0,
        # unit to unit voice service response fields
        answer_response: Optional[AnswerResponse] = None,
        # negative acknowledge response fields
        additional_information_field: Optional[AdditionalInformationField] = None,
        source_type: Optional[SourceType] = None,
        service_type: Optional[CsbkOpcodes] = None,
        reason_code: Optional[ReasonCode] = None,
        # preamble fields
        csbk_content_follows_preambles: Union[int, bool] = False,
        target_address_is_individual: Union[int, bool] = False,
        blocks_to_follow: int = 0,
        # channel timing fields
        sync_age: int = 0,
        generation: int = 0,
        leader_identifier: int = 0,
        new_leader: Union[int, bool] = 0,
        leader_dynamic_identifier: Union[DynamicIdentifier, int] = 0,
        channel_timing_opcode: Union[ChannelTimingOpcode, int] = 0,
        source_identifier: int = 0,
        source_dynamic_identifier: Union[DynamicIdentifier, int] = 0,
        # aloha pdu for RAP
        tsccas_support: bool = False,
        site_timeslot_synchronized: bool = False,
        document_version_control: int = 3,
        tscc_is_offset_timing: bool = False,
        ts_active_connection: bool = False,
        aloha_mask: int = 0,
        service_function: Union[RandomAccessServiceFunction, int] = 0,
        nrand_wait: int = 0,
        tscc_reg_required: bool = False,
        tscc_backoff: int = 1,
        system_identity_code: int = 0,
        # for unknown / manufacturer-specific data
        raw_data: Union[bytes, bitarray] = b"",
        # (C_BCAST)
        announcement_type: AnnouncementType = AnnouncementType.GeneralSiteParams,
        broadcast_params: bitarray = bitarray(),  # it's 14 and 24 bits, total 38 bits, missing 2 bits to bytes
    ):
        """
        Params that are optional, are specific for particular CSBKO

        :param last_block: value 0/1
        :param protect_flag: value 0/1
        :param csbko: CsbkOpcodes enum
        :param manufacturers_feature_set_id: FeatureSetIDs enum
        :param crc: crc-ccit (crc16-ccit) value
        :param bs_address: optional value 0-16777215
        :param source_address: optional value 0-16777215
        :param service_options: optional ServiceOptions element instance
        :param target_address: optional value 0-16777215
        :param answer_response: optional AnswerResponse enum
        :param additional_information_field: optional AdditionalInformationField enum
        :param source_type: optional SourceType enum
        :param service_type: optional CsbkOpcodes enum
        :param reason_code: optional ReasonCode enum
        :param csbk_content_follows_preambles: value 0/1
        :param target_address_is_individual: value 0/1
        :param blocks_to_follow: value 0-255
        :param sync_age: value 0-2047, amount of SAIncr (500ms) since last beacon
        :param generation: value 0-31, number of timing hops from leader
        :param leader_identifier: value 0-1048575, ms derived identifier
        :param new_leader: 0 => ms accepts current leader, 1 => new leader is appointed
        :param leader_dynamic_identifier: DynamicIdentifier or value 0-3
        :param channel_timing_opcode: ChannelTimingOpcode or value 0-3
        :param source_identifier: value 0-1048575, ms derived identifier
        :param source_dynamic_identifier: DynamicIdentifier or value 0-3
        """
        self.last_block: bool = last_block in (True, 1)
        self.protect_flag: bool = protect_flag in (True, 1)
        self.csbko: CsbkOpcodes = csbko
        self.feature_set: FeatureSetIDs = manufacturers_feature_set_id
        self.crc: int = crc

        self.bs_address: int = bs_address
        self.source_address: int = source_address
        self.service_options: Optional[ServiceOptions] = service_options
        self.target_address: int = target_address
        self.answer_response: Optional[AnswerResponse] = answer_response
        self.additional_information_field: Optional[
            AdditionalInformationField
        ] = additional_information_field
        self.source_type: Optional[SourceType] = source_type
        self.service_type: Optional[CsbkOpcodes] = service_type
        self.reason_code: Optional[ReasonCode] = reason_code
        self.csbk_content_follows_preambles: bool = csbk_content_follows_preambles in (
            True,
            1,
        )
        self.target_address_is_individual: bool = target_address_is_individual in (
            True,
            1,
        )
        self.blocks_to_follow: int = blocks_to_follow
        self.sync_age: int = sync_age
        self.generation: int = generation
        self.leader_identifier: int = leader_identifier
        self.new_leader: int = int(new_leader)
        self.leader_dynamic_identifier: DynamicIdentifier = (
            leader_dynamic_identifier
            if isinstance(leader_dynamic_identifier, DynamicIdentifier)
            else DynamicIdentifier(leader_dynamic_identifier)
        )
        self.channel_timing_opcode: ChannelTimingOpcode = (
            channel_timing_opcode
            if isinstance(channel_timing_opcode, ChannelTimingOpcode)
            else ChannelTimingOpcode(channel_timing_opcode)
        )
        self.source_identifier: int = source_identifier
        self.source_dynamic_identifier = (
            source_dynamic_identifier
            if isinstance(source_dynamic_identifier, DynamicIdentifier)
            else DynamicIdentifier(source_dynamic_identifier)
        )
        self.raw_data: bytes = (
            bits_to_bytes(raw_data) if isinstance(raw_data, bitarray) else raw_data
        )
        self.tsccas_support: bool = tsccas_support
        self.site_timeslot_synchronized: bool = site_timeslot_synchronized
        self.document_version_control: int = document_version_control
        self.tscc_is_offset_timing: bool = tscc_is_offset_timing
        self.ts_active_connection: bool = ts_active_connection
        self.aloha_mask: int = aloha_mask
        self.service_function: RandomAccessServiceFunction = (
            service_function
            if isinstance(service_function, RandomAccessServiceFunction)
            else RandomAccessServiceFunction(service_function)
        )
        self.nrand_wait: int = nrand_wait
        self.tscc_reg_required: bool = tscc_reg_required
        self.tscc_backoff: int = tscc_backoff
        self.system_identity_code: int = system_identity_code
        self.broadcast_params: bitarray = broadcast_params
        self.announcement_type: AnnouncementType = announcement_type

        if self.crc <= 0:
            self.calculate_crc_ccit()

    def calculate_crc_ccit(self) -> "CSBK":
        self.crc = CRC16.calculate(self.as_bits()[0:80].tobytes(), CrcMasks.CSBK)
        return self

    def as_bits(self) -> bitarray:
        pdu: bitarray = (
            bitarray([self.last_block, self.protect_flag])
            + self.csbko.as_bits()
            + self.feature_set.as_bits()
        )
        if self.csbko == CsbkOpcodes.BSOutboundActivation:
            pdu += (
                int2ba(0, length=16)
                + int2ba(self.bs_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.UnitToUnitVoiceServiceRequest:
            pdu += (
                self.service_options.as_bits()
                + int2ba(0, length=8)
                + int2ba(self.target_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.UnitToUnitVoiceServiceAnswerResponse:
            pdu += (
                self.service_options.as_bits()
                + self.answer_response.as_bits()
                + int2ba(self.target_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.NegativeAcknowledgementResponse:
            pdu += (
                bitarray([1, self.source_type == SourceType.MSSourced])
                + self.service_type.as_bits()
                + self.reason_code.as_bits()
                + int2ba(self.source_address, length=24)
                + int2ba(self.target_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.PreambleCSBK:
            pdu += (
                bitarray(
                    [
                        not self.csbk_content_follows_preambles,
                        not self.target_address_is_individual,
                    ]
                )
                + int2ba(0, length=6)
                + int2ba(self.blocks_to_follow, length=8)
                + int2ba(self.target_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.ChannelTimingCSBK:
            cto = self.channel_timing_opcode.as_bits()
            pdu += (
                int2ba(self.sync_age, length=11)
                + int2ba(self.generation, length=5)
                + int2ba(self.leader_identifier, length=20)
                + int2ba(self.new_leader, length=1)
                + self.leader_dynamic_identifier.as_bits()
                + bitarray([cto[0]])
                + int2ba(self.source_identifier, length=20)
                + bitarray([0])
                + self.source_dynamic_identifier.as_bits()
                + bitarray([cto[1]])
            )
        elif self.csbko == CsbkOpcodes.HyteraIPSCSync:
            pdu += bytes_to_bits(self.raw_data)
        elif self.csbko == CsbkOpcodes.AlohaPDUsForRandomAccessProtocol:
            pdu += (
                bitarray(
                    [
                        0,  # reserved bit
                        self.tsccas_support,
                        self.site_timeslot_synchronized,
                    ]
                )
                + int2ba(self.document_version_control, length=3)
                + bitarray([self.tscc_is_offset_timing, self.ts_active_connection])
                + int2ba(self.aloha_mask, length=5)
                + int2ba(self.service_function.value, length=2)
                + int2ba(self.nrand_wait, length=4)
                + bitarray([self.tscc_reg_required])
                + int2ba(self.tscc_backoff, length=4)
                + int2ba(self.system_identity_code, length=16)
                + int2ba(self.target_address, length=24)
            )
        elif self.csbko == CsbkOpcodes.AnnouncementPDUsWithoutResponse:
            pdu += (
                int2ba(self.announcement_type.value, length=5)
                + self.broadcast_params[:14]
                + bitarray([self.tscc_reg_required])
                + int2ba(self.tscc_backoff, length=4)
                + int2ba(self.system_identity_code, length=16)
                + self.broadcast_params[14:38]
            )

        return pdu + int2ba(self.crc, length=16)

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["CSBK"]:
        return CSBK.from_bits(bytes_to_bits(data))

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bits_to_bytes(self.as_bits())

    @staticmethod
    def from_bits(bits: bitarray) -> "CSBK":
        assert (
            len(bits) >= 96
        ), f"A single CSBK PDU has a length of 96 bits, got only {len(bits)}"
        lb: int = bits[0]
        pf: int = bits[1]
        csbko: CsbkOpcodes = CsbkOpcodes(ba2int(bits[2:8]))
        fid: FeatureSetIDs = FeatureSetIDs(ba2int(bits[8:16]))
        crc_ccit: int = ba2int(bits[80:96])
        if csbko == CsbkOpcodes.BSOutboundActivation:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                bs_address=ba2int(bits[32:56]),
                source_address=ba2int(bits[56:80]),
            )
        elif csbko == CsbkOpcodes.UnitToUnitVoiceServiceRequest:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                service_options=ServiceOptions.from_bits(bits[16:24]),
                target_address=ba2int(bits[32:56]),
                source_address=ba2int(bits[56:80]),
            )
        elif csbko == CsbkOpcodes.UnitToUnitVoiceServiceAnswerResponse:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                service_options=ServiceOptions.from_bits(bits[16:24]),
                answer_response=AnswerResponse(ba2int(bits[24:32])),
                target_address=ba2int(bits[32:56]),
                source_address=ba2int(bits[56:80]),
            )
        elif csbko == CsbkOpcodes.NegativeAcknowledgementResponse:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                additional_information_field=AdditionalInformationField(bits[16]),
                source_type=SourceType(bits[17]),
                service_type=CsbkOpcodes.from_bits(bits[18:24]),
                reason_code=ReasonCode(ba2int(bits[24:32])),
                source_address=ba2int(bits[32:56]),
                target_address=ba2int(bits[56:80]),
            )
        elif csbko == CsbkOpcodes.PreambleCSBK:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                csbk_content_follows_preambles=not bits[16],
                target_address_is_individual=not bits[17],
                blocks_to_follow=ba2int(bits[24:32]),
                target_address=ba2int(bits[32:56]),
                source_address=ba2int(bits[56:80]),
            )
        elif csbko == CsbkOpcodes.ChannelTimingCSBK:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                sync_age=ba2int(bits[16:27]),
                generation=ba2int(bits[27:32]),
                leader_identifier=ba2int(bits[32:52]),
                new_leader=bits[52],
                leader_dynamic_identifier=DynamicIdentifier.from_bits(bits[53:55]),
                channel_timing_opcode=ba2int(bitarray([bits[55], bits[79]])),
                source_identifier=ba2int(bits[56:76]),
                source_dynamic_identifier=DynamicIdentifier.from_bits(bits[77:79]),
            )
        elif csbko == CsbkOpcodes.HyteraIPSCSync:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                raw_data=bits[16:80],
            )
        elif csbko == CsbkOpcodes.AnnouncementPDUsWithoutResponse:
            return CSBK(
                last_block=lb,
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                announcement_type=AnnouncementType(ba2int(bits[16:21])),
                tscc_reg_required=bits[35] == 1,
                tscc_backoff=ba2int(bits[36:40]),
                system_identity_code=ba2int(bits[40:56]),
                broadcast_params=bits[21:35] + bits[56:80],
            )
        elif csbko == CsbkOpcodes.AlohaPDUsForRandomAccessProtocol:
            return CSBK(
                protect_flag=pf,
                manufacturers_feature_set_id=fid,
                crc=crc_ccit,
                csbko=csbko,
                tsccas_support=bits[17] == 1,
                site_timeslot_synchronized=bits[18] == 1,
                document_version_control=ba2int(bits[19:22]),
                tscc_is_offset_timing=bits[22] == 1,
                ts_active_connection=bits[23] == 1,
                aloha_mask=ba2int(bits[24:29]),
                service_function=ba2int(bits[29:31]),
                nrand_wait=ba2int(bits[31:35]),
                tscc_reg_required=bits[35] == 1,
                tscc_backoff=ba2int(bits[36:40]),
                system_identity_code=ba2int(bits[40:56]),
                target_address=ba2int(bits[56:80]),
            )

        raise NotImplementedError(
            f"Not-implemented CSBKO {csbko} PDU {bits_to_bytes(bits).hex()}"
        )

    def __repr__(self) -> str:
        description = f"[{self.csbko}] [LB: {int(self.last_block)}] [PF: {int(self.protect_flag)}] [{self.feature_set}] "
        if self.csbko == CsbkOpcodes.BSOutboundActivation:
            description += (
                f"[BS ADDR: {self.bs_address}] [SRC ADDR: {self.source_address}]"
            )
        elif self.csbko == CsbkOpcodes.UnitToUnitVoiceServiceRequest:
            description += f"[{self.service_options}] [DST ADDR: {self.target_address}] [SRC ADDR: {self.source_address}]"
        elif self.csbko == CsbkOpcodes.UnitToUnitVoiceServiceAnswerResponse:
            description += f"[{self.service_options}] [{self.answer_response}] [DST ADDR: {self.target_address}] [SRC ADDR: {self.source_address}]"
        elif self.csbko == CsbkOpcodes.NegativeAcknowledgementResponse:
            description += f"[{self.source_type}] [{self.service_type}] [{self.reason_code}] [SRC ADDR: {self.source_address}] [DST ADDR: {self.target_address}]"
        elif self.csbko == CsbkOpcodes.PreambleCSBK:
            description += (
                f"[TARGET IS {'INDIVIDUAL' if self.target_address_is_individual else 'GROUP'}] "
                f"[FOLLOWED BY {'CSBK' if self.csbk_content_follows_preambles else 'DATA'}] "
                f"[BTF: {self.blocks_to_follow}] [DST ADDR: {self.target_address}] [SRC ADDR: {self.source_address}]"
            )
        elif self.csbko == CsbkOpcodes.ChannelTimingCSBK:
            description += (
                f"[AGE: {500 * self.sync_age}ms] [GENERATION: {self.generation}] "
                f"[LEADER IDENTIFIER: {self.leader_identifier}] [NEW LEADER: {self.new_leader}] "
                f"[LEADER DYN IDENTIFIER: {self.leader_dynamic_identifier}] "
                f"[SOURCE IDENTIFIER: {self.source_identifier}] "
                f"[SOURCE DYN IDENTIFIER: {self.source_dynamic_identifier}] "
                f"[CTO: {self.channel_timing_opcode}]"
            )
        elif self.csbko == CsbkOpcodes.HyteraIPSCSync:
            description += f"[MFID DATA HEX({self.raw_data.hex()})]"
        elif self.csbko == CsbkOpcodes.AnnouncementPDUsWithoutResponse:
            description += (
                f"[{self.announcement_type}] "
                f"[PARAMS1: {self.broadcast_params[:14].to01()}] [PARAMS2: {self.broadcast_params[14:].to01()}] "
                f"[REGISTRATION REQUIRED: {self.tscc_reg_required}] "
                f"[BACKOFF: TDMA Frame Length = {CSBK.TSCC_BACKOFF_MAP.get(self.tscc_backoff)}] "
                f"[SYSTEM IDENTITY: {self.system_identity_code}] "
            )
        elif self.csbko == CsbkOpcodes.AlohaPDUsForRandomAccessProtocol:
            description += (
                f"[TSCCAS support: {self.tsccas_support}] "
                f"[Timeslot sync enabled: {self.site_timeslot_synchronized}] "
                f"[DOC: v{self.document_version_control}] "
                f"[TIMING: {'offset' if self.tscc_is_offset_timing else 'aligned'}] "
                f"[TS ACTIVE CONNECTION: {self.ts_active_connection}] "
                f"[MASK: {self.aloha_mask}] "
                f"[SERVICE: {self.service_function}] "
                f"[NRAND_WAIT: {self.nrand_wait}] "
                f"[REGISTRATION REQUIRED: {self.tscc_reg_required}] "
                f"[BACKOFF: TDMA Frame Length = {CSBK.TSCC_BACKOFF_MAP.get(self.tscc_backoff)}] "
                f"[SYSTEM IDENTITY: {self.system_identity_code}] "
                f"[MS ADDRESS: {self.target_address}]"
            )
        return description
