import secrets
from typing import List, Optional, Union

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data, Rate12DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate1_data import Rate1Data, Rate1DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34Data, Rate34DataTypes
from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
    WithObservers,
)
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class Transmission(WithObservers, LoggingTrait):
    def __init__(self, observer: Optional[TransmissionObserverInterface] = None):
        super().__init__(
            observers=[observer]
            if isinstance(observer, TransmissionObserverInterface)
            else []
        )
        self.type = TransmissionTypes.Idle
        self.blocks_expected: int = 0
        self.blocks_received: int = 0
        self.last_voice_burst: VoiceBursts = VoiceBursts.Unknown
        self.last_burst_data_type: DataTypes = DataTypes.Reserved
        self.confirmed: bool = False
        self.finished: bool = False
        self.blocks: List[BitsInterface] = list()
        self.header: Optional[DataHeader] = None
        self.stream_no: bytes = secrets.token_bytes(4)

    def new_transmission(self, newtype: TransmissionTypes):
        if (
            newtype != TransmissionTypes.Idle
            and self.type == TransmissionTypes.DataTransmission
        ):
            self.log_error("New Transmission when old was not yet finished")
            self.end_data_transmission()
        self.type = newtype
        self.blocks_expected = 0
        self.blocks_received = 0
        self.confirmed = False
        self.finished = False
        self.blocks = list()
        self.header = None
        self.stream_no = secrets.token_bytes(4)

        if newtype != TransmissionTypes.Idle:
            self.transmission_started(transmission_type=newtype)

    def ensure_transmission(self, transmission_type: TransmissionTypes):
        if not self.type == transmission_type:
            self.new_transmission(transmission_type)

    def process_voice_header(self, voice_header: FullLinkControl):
        self.ensure_transmission(TransmissionTypes.VoiceTransmission)
        self.header = voice_header

        # header + terminator
        self.blocks_expected += 2
        self.blocks_received += 1

    def process_data_header(self, data_header: DataHeader):
        self.ensure_transmission(TransmissionTypes.DataTransmission)

        if data_header.get_blocks_to_follow():
            if self.blocks_expected == 0:
                self.blocks_expected = data_header.get_blocks_to_follow() + 1
            elif self.blocks_expected != (
                self.blocks_received + data_header.get_blocks_to_follow() + 1
            ):
                pass
                # self.log_warning(
                #    f"[Blocks To Follow / Appended Blocks] DMR Data Header block count mismatch [{self.blocks_expected} - {self.blocks_received} != {data_header.blocks_to_follow}]"
                # )

        self.header = data_header
        self.blocks_received += 1
        self.blocks.append(data_header)
        self.confirmed = data_header.is_response_requested
        # self.log_info(
        #    f"[DATA HDR] received {self.blocks_received} / {self.blocks_expected} expected, {data_header.__class__.__name__}"
        # )
        # self.log_info(repr(data_header))

    def process_csbk(self, csbk: CSBK):
        self.ensure_transmission(TransmissionTypes.DataTransmission)

        if csbk.csbko == CsbkOpcodes.PreambleCSBK:
            if self.blocks_expected == 0:
                self.blocks_expected = csbk.blocks_to_follow + 1
            elif self.blocks_expected - self.blocks_received != (
                csbk.blocks_to_follow + 1
            ):
                pass
                # self.log_warning(
                #    f"CSBK not setting expected to {self.blocks_expected} - {self.blocks_received} != {csbk.blocks_to_follow + 1}"
                # )

        self.blocks_received += 1
        self.blocks.append(csbk)
        # self.log_info(
        #    f"[CSBK] received {self.blocks_received} / {self.blocks_expected} expected"
        # )

    def process_data(self, data: Union[Rate12Data, Rate34Data, Rate1Data]):
        self.blocks_received += 1
        self.blocks.append(data)
        if data.is_last_block():
            self.end_data_transmission()

    def is_last_block(self, called_before_processing: bool = False):
        return self.blocks_expected != 0 and (
            self.blocks_expected
            == self.blocks_received + (1 if called_before_processing else 0)
        )

    def end_voice_transmission(self):
        if self.finished or self.type == TransmissionTypes.Idle:
            return
        self.log_info(f"[VOICE CALL END]")
        if isinstance(self.header, FullLinkControl):
            self.voice_transmission_ended(self.header, self.blocks)

            if self.header.full_link_control_opcode == FLCOs.GroupVoiceChannelUser:
                self.log_info(
                    f"[GROUP] [{self.header.source_address} -> "
                    f"{self.header.group_address}]"
                )
            elif (
                self.header.full_link_control_opcode == FLCOs.UnitToUnitVoiceChannelUser
            ):
                self.log_info(
                    f"[PRIVATE] [{self.header.source_address} ->"
                    f" {self.header.target_address}]"
                )
        else:
            self.log_info(
                f"end voice transmission unknown header type {self.header.__class__.__name__}"
            )
        self.new_transmission(TransmissionTypes.Idle)

    def end_data_transmission(self):
        if self.finished or not self.header or self.type == TransmissionTypes.Idle:
            self.log_info(
                f"end_data_transmission without effect is_finished:{self.finished} header:{type(self.header)} transmission_type:{self.type}"
            )
            return
        # self.log_info(
        #    f"\n[DATA CALL END] [CONFIRMED: {self.confirmed}] "
        #    f"[Packets {self.blocks_received}/{self.blocks_expected} ({len(self.blocks)})] "
        # )

        self.data_transmission_ended(self.header, self.blocks)
        self.log_info(repr(self.header))

        user_data: bytes = b""
        for block in self.blocks:
            if (
                isinstance(block, Rate12Data)
                or isinstance(block, Rate34Data)
                or isinstance(block, Rate1Data)
            ):
                user_data += block.data

        if (
            hasattr(self.header, "sap_identifier")
            and self.header.sap_identifier == SAPIdentifier.UDP_IP_compression
            and len(user_data) >= 5
        ):
            # print(f"udp/ipv4 compressed {user_data.hex()}")
            udp_ip = UDPIPv4CompressedHeader.from_bits(bits=bytes_to_bits(user_data))
            print(repr(udp_ip))

        # print("\n" * 3)

        self.new_transmission(TransmissionTypes.Idle)

    def fix_voice_burst_type(self, burst: Burst) -> Burst:
        if not self.type == TransmissionTypes.VoiceTransmission:
            self.last_burst_data_type = burst.data_type
            return burst

        if burst.is_voice_superframe_start or (
            self.last_voice_burst == VoiceBursts.VoiceBurstF
            and burst.data_type == DataTypes.Reserved
        ):
            burst.set_is_voice(burst_id=VoiceBursts.VoiceBurstA)
        elif burst.data_type == DataTypes.Reserved and self.last_voice_burst in [
            VoiceBursts.VoiceBurstA,
            VoiceBursts.VoiceBurstB,
            VoiceBursts.VoiceBurstC,
            VoiceBursts.VoiceBurstD,
            VoiceBursts.VoiceBurstE,
        ]:
            burst.set_is_voice(VoiceBursts(self.last_voice_burst.value + 1))

        self.last_voice_burst = burst.voice_burst
        self.last_burst_data_type = burst.data_type

        return burst

    def process_packet(self, burst: Burst) -> Burst:
        burst = self.fix_voice_burst_type(burst)

        lc_info_bits = BPTC19696.deinterleave_data_bits(
            burst.full_bits[:98] + burst.full_bits[166:]
        )
        if burst.data_type == DataTypes.VoiceLCHeader:
            self.log_info("voice header %s" % lc_info_bits.tobytes().hex())
            self.process_voice_header(FullLinkControl.from_bits(lc_info_bits))
        elif burst.data_type == DataTypes.DataHeader:
            self.process_data_header(DataHeader.from_bits(lc_info_bits))
        elif burst.data_type == DataTypes.CSBK:
            self.process_csbk(CSBK.from_bits(lc_info_bits))
        elif burst.data_type == DataTypes.TerminatorWithLC:
            self.log_info("voice terminator %s" % lc_info_bits.tobytes().hex())
            self.blocks_received += 1
            self.end_voice_transmission()
        elif burst.data_type in [
            VoiceBursts.VoiceBurstA,
            VoiceBursts.VoiceBurstB,
            VoiceBursts.VoiceBurstC,
            VoiceBursts.VoiceBurstD,
            VoiceBursts.VoiceBurstE,
            VoiceBursts.VoiceBurstF,
        ]:
            if burst.data_type == VoiceBursts.VoiceBurstA:
                self.blocks_expected += 6
            self.blocks_received += 1
        elif burst.data_type == DataTypes.Rate12Data:
            self.process_data(
                data=Rate12Data.from_bits_typed(
                    bits=lc_info_bits,
                    data_type=Rate12DataTypes.resolve(
                        confirmed=self.confirmed, last=self.is_last_block(True)
                    ),
                )
            )
        elif burst.data_type == DataTypes.Rate34Data:
            self.process_data(
                data=Rate34Data.from_bits_typed(
                    bits=burst.info_bits_deinterleaved,
                    data_type=Rate34DataTypes.resolve(
                        confirmed=self.confirmed, last=self.is_last_block(True)
                    ),
                )
            )
        elif burst.data_type == DataTypes.Rate1Data:
            self.process_data(
                data=Rate1Data.from_bits_typed(
                    bits=burst.info_bits_deinterleaved,
                    data_type=Rate1DataTypes.resolve(
                        confirmed=self.confirmed, last=self.is_last_block(True)
                    ),
                )
            )

        if self.is_last_block():
            self.end_transmissions()

        return burst

    def end_transmissions(self):
        if self.type == TransmissionTypes.DataTransmission:
            self.end_data_transmission()
        elif self.type == TransmissionTypes.VoiceTransmission:
            self.end_voice_transmission()
