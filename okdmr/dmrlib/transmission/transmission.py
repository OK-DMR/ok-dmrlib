import secrets
import traceback
from typing import List, Optional, Union

from bitarray.util import int2ba
from kaitaistruct import KaitaiStruct
from okdmr.kaitai.etsi.dmr_csbk import DmrCsbk
from okdmr.kaitai.etsi.dmr_data import DmrData
from okdmr.kaitai.etsi.dmr_data_header import DmrDataHeader
from okdmr.kaitai.etsi.dmr_ip_udp import DmrIpUdp
from okdmr.kaitai.etsi.full_link_control import FullLinkControl

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.fec.trellis import Trellis34
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
)
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class Transmission(LoggingTrait):
    def __init__(self, observer: TransmissionObserverInterface = None):
        self.type = TransmissionTypes.Idle
        self.blocks_expected: int = 0
        self.blocks_received: int = 0
        self.last_voice_burst: VoiceBursts = VoiceBursts.Unknown
        self.last_burst_data_type: DataTypes = DataTypes.Reserved
        self.confirmed: bool = False
        self.finished: bool = False
        self.blocks: List[KaitaiStruct] = list()
        self.header: Optional[KaitaiStruct] = None
        self.stream_no: bytes = secrets.token_bytes(4)
        self.observers: List[TransmissionObserverInterface] = (
            [] if observer is None else [observer]
        )

    def add_transmission_observer(self, observer: TransmissionObserverInterface):
        self.observers.append(observer)

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

    def process_voice_header(self, voice_header: FullLinkControl):
        self.new_transmission(TransmissionTypes.VoiceTransmission)
        self.header = voice_header

        # header + terminator
        self.blocks_expected += 2
        self.blocks_received += 1

    def process_data_header(self, data_header: DmrDataHeader):
        if not self.type == TransmissionTypes.DataTransmission:
            self.new_transmission(TransmissionTypes.DataTransmission)
        if hasattr(data_header.data, "blocks_to_follow"):
            if self.blocks_expected == 0:
                self.blocks_expected = data_header.data.blocks_to_follow + 1
            elif self.blocks_expected != (
                self.blocks_received + data_header.data.blocks_to_follow + 1
            ):
                self.log_warning(
                    f"[Blocks To Follow] Header block count mismatch {self.blocks_expected}-{self.blocks_received} != {data_header.data.blocks_to_follow}"
                )
        elif hasattr(data_header.data, "appended_blocks"):
            if self.blocks_expected == 0:
                self.blocks_expected = data_header.data.appended_blocks + 1
            elif self.blocks_expected != (
                self.blocks_expected + data_header.data.appended_blocks + 1
            ):
                self.log_warning(
                    f"[Appended Blocks] Header block count mismatch {self.blocks_expected}+{self.blocks_received}+1 != {data_header.data.appended_blocks}"
                )

        self.header = data_header
        self.blocks_received += 1
        self.blocks.append(data_header)
        self.confirmed = data_header.data.response_requested
        self.log_info(
            f"[DATA HDR] received {self.blocks_received} / {self.blocks_expected} expected, {data_header.data.__class__.__name__}"
        )

    def process_csbk(self, csbk: DmrCsbk):
        if not self.type == TransmissionTypes.DataTransmission:
            self.new_transmission(TransmissionTypes.DataTransmission)
        if csbk.csbk_opcode == DmrCsbk.CsbkoTypes.preamble:
            if self.blocks_expected == 0:
                self.blocks_expected = csbk.preamble_csbk_blocks_to_follow + 1
            elif (
                self.blocks_expected - self.blocks_received
                != csbk.preamble_csbk_blocks_to_follow + 1
            ):
                self.log_warning(
                    f"CSBK not setting expected to {self.blocks_expected} - {self.blocks_received} != {csbk.preamble_csbk_blocks_to_follow}"
                )

        self.blocks_received += 1
        self.blocks.append(csbk)
        self.log_info(
            f"[CSBK] received {self.blocks_received} / {self.blocks_expected} expected"
        )

    def process_rate_12_confirmed(
        self, data: Union[DmrData.Rate12Confirmed, DmrData.Rate12LastBlockConfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        self.log_info(
            "rate12 crc9 user_data:%s dbsn:%s crc:%s"
            % (
                data.user_data.hex(),
                int2ba(data.data_block_serial_number),
                int2ba(data.crc9),
            )
        )
        if isinstance(data, DmrData.Rate12LastBlockConfirmed):
            self.end_data_transmission()

    def process_rate_12_unconfirmed(
        self, data: Union[DmrData.Rate12Unconfirmed, DmrData.Rate12LastBlockUnconfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        if isinstance(data, DmrData.Rate12LastBlockUnconfirmed):
            self.end_data_transmission()

    def process_rate_34_confirmed(
        self, data: Union[DmrData.Rate34Confirmed, DmrData.Rate34LastBlockConfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        self.log_info(
            "rate34 crc9 class:%s user_data:%s dbsn:%d crc9:%s"
            % (
                data.__class__.__name__,
                data.user_data.hex(),
                data.data_block_serial_number,
                data.crc9,
            )
        )
        if isinstance(data, DmrData.Rate34LastBlockConfirmed):
            self.log_info("crc32 %s" % data.message_crc32.hex())
            self.end_data_transmission()

    def process_rate_34_unconfirmed(
        self, data: Union[DmrData.Rate34Unconfirmed, DmrData.Rate34LastBlockUnconfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        if isinstance(data, DmrData.Rate34LastBlockUnconfirmed):
            self.end_data_transmission()

    def process_rate_1_confirmed(
        self, data: Union[DmrData.Rate1Confirmed, DmrData.Rate1LastBlockConfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        self.log_info(
            "rate1 crc9 user_data:%s dbsn:%s crc9:%s"
            % (
                data.user_data.hex(),
                int2ba(data.data_block_serial_number),
                int2ba(data.crc9),
            )
        )
        if isinstance(data, DmrData.Rate1LastBlockConfirmed):
            self.end_data_transmission()

    def process_rate_1_unconfirmed(
        self, data: Union[DmrData.Rate1Unconfirmed, DmrData.Rate1LastBlockUnconfirmed]
    ):
        self.blocks_received += 1
        self.blocks.append(data)
        if isinstance(data, DmrData.Rate1LastBlockUnconfirmed):
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

            for observer in self.observers:
                # noinspection PyBroadException
                try:
                    observer.voice_transmission_ended(self.header, [])
                except:
                    traceback.print_exc()

            if isinstance(
                self.header.specific_data, FullLinkControl.GroupVoiceChannelUser
            ):
                self.log_info(
                    f"[GROUP] [{self.header.specific_data.source_address} -> "
                    f"{self.header.specific_data.group_address}]"
                )
            elif isinstance(
                self.header.specific_data, FullLinkControl.UnitToUnitVoiceChannelUser
            ):
                self.log_info(
                    f"[PRIVATE] [{self.header.specific_data.source_address} ->"
                    f" {self.header.specific_data.target_address}]"
                )
        else:
            self.log_info(
                f"end voice transmission unknown header type {self.header.__class__.__name__}"
            )
        self.new_transmission(TransmissionTypes.Idle)

    def end_data_transmission(self):
        if self.finished or self.type == TransmissionTypes.Idle:
            return
        if not isinstance(self.header, DmrDataHeader):
            self.log_warning(f"Unexpected header type {self.header.__class__.__name__}")
            return
        self.log_info(
            f"\n[DATA CALL END] [CONFIRMED: {self.confirmed}] "
            f"[Packets {self.blocks_received}/{self.blocks_expected} ({len(self.blocks)})] "
        )

        for observer in self.observers:
            # noinspection PyBroadException
            try:
                observer.data_transmission_ended(self.header, self.blocks)
            except:
                traceback.print_exc()

        user_data: bytes = bytes()
        for packet in self.blocks:
            if isinstance(packet, DmrCsbk):
                self.log_info(
                    f"[CSBK] [{packet.preamble_source_address} -> {packet.preamble_target_address}] [{packet.preamble_group_or_individual}]"
                )
            elif isinstance(packet, DmrDataHeader):
                self.log_info(
                    f"[DATA HDR] [{packet.data_packet_format}] [{packet.data.__class__.__name__}]"
                )
            elif hasattr(packet, "user_data"):
                self.log_info(
                    f"[DATA] [{packet.__class__.__name__}] [{packet.user_data}]"
                )
                user_data += packet.user_data
            else:
                self.log_info(f"[UNUSED] [{packet.__class__.__name__}]")
        if (
            self.header.data.sap_identifier
            == DmrDataHeader.SapIdentifiers.udp_ip_header_compression
        ):
            if len(user_data) == 0:
                self.log_info("No user data to parse as UDP Header with data")
            else:
                udp_header_with_data = DmrIpUdp.UdpIpv4CompressedHeader.from_bytes(
                    user_data
                )
                # prettyprint(udp_header_with_data)
                self.log_info(
                    "UDP DATA: "
                    + bytes(udp_header_with_data.user_data).decode("latin-1")
                )
        elif (
            self.header.data.sap_identifier
            == DmrDataHeader.SapIdentifiers.ip_based_packet_data
        ):
            self.log_info(user_data.hex())
            # ip = IP(user_data)
            # ip.display()
            # print(
            #     "##",
            #     ip.getlayer("UDP").getfieldval("load").hex(),
            #     ip.getlayer("UDP").getfieldval("load").decode("utf-16-le"),
            # )
        elif self.header.data.sap_identifier == DmrDataHeader.SapIdentifiers.short_data:
            if (
                hasattr(self.header.data, "defined_data")
                and self.header.data.defined_data
                == DmrDataHeader.DefinedDataFormats.bcd
            ):
                self.log_info("bcd %s" % user_data.hex())
            else:
                # prettyprint(self.header.data)
                self.log_info("user_data %s (bytes: %s)" % (user_data.hex(), user_data))
        else:
            self.log_warning("unhandled data %s" % user_data.hex())

        self.new_transmission(TransmissionTypes.Idle)

    def fix_voice_burst_type(self, burst: Burst) -> Burst:
        if not self.type == TransmissionTypes.VoiceTransmission:
            self.last_burst_data_type = burst.data_type
            return burst

        if burst.is_voice_superframe_start or (
            self.last_voice_burst == VoiceBursts.VoiceBurstF
            and burst.data_type == DataTypes.Reserved
        ):
            burst.voice_burst = VoiceBursts.VoiceBurstA
        elif burst.data_type == DataTypes.Reserved and self.last_voice_burst in [
            VoiceBursts.VoiceBurstA,
            VoiceBursts.VoiceBurstB,
            VoiceBursts.VoiceBurstC,
            VoiceBursts.VoiceBurstD,
            VoiceBursts.VoiceBurstE,
        ]:
            burst.voice_burst = VoiceBursts(self.last_voice_burst.value + 1)

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
            self.process_voice_header(FullLinkControl.from_bytes(lc_info_bits))
        elif burst.data_type == DataTypes.DataHeader:
            self.process_data_header(DmrDataHeader.from_bytes(lc_info_bits))
        elif burst.data_type == DataTypes.CSBK:
            self.process_csbk(DmrCsbk.from_bytes(lc_info_bits))
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
            if self.confirmed:
                if self.is_last_block(True):
                    self.process_rate_12_confirmed(
                        DmrData.Rate12LastBlockConfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_12_confirmed(
                        DmrData.Rate12Confirmed.from_bytes(lc_info_bits)
                    )
            else:
                if self.is_last_block(True):
                    self.process_rate_12_unconfirmed(
                        DmrData.Rate12LastBlockUnconfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_12_unconfirmed(
                        DmrData.Rate12Unconfirmed.from_bytes(lc_info_bits)
                    )
        elif burst.data_type == DataTypes.Rate34Data:
            lc_info_bits = Trellis34.decode(burst.info_bits, as_bytes=True)
            if self.confirmed:
                if self.is_last_block(True):
                    self.process_rate_34_confirmed(
                        DmrData.Rate34LastBlockConfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_34_confirmed(
                        DmrData.Rate34Confirmed.from_bytes(lc_info_bits)
                    )
            else:
                if self.is_last_block(True):
                    self.process_rate_34_unconfirmed(
                        DmrData.Rate34LastBlockUnconfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_34_unconfirmed(
                        DmrData.Rate34Unconfirmed.from_bytes(lc_info_bits)
                    )
        elif burst.data_type == DataTypes.Rate1Data:
            if self.confirmed:
                if self.is_last_block(True):
                    self.process_rate_1_confirmed(
                        DmrData.Rate1LastBlockConfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_1_confirmed(
                        DmrData.Rate1Confirmed.from_bytes(lc_info_bits)
                    )
            else:
                if self.is_last_block(True):
                    self.process_rate_1_unconfirmed(
                        DmrData.Rate1LastBlockUnconfirmed.from_bytes(lc_info_bits)
                    )
                else:
                    self.process_rate_1_unconfirmed(
                        DmrData.Rate1Unconfirmed.from_bytes(lc_info_bits)
                    )

        if self.is_last_block():
            self.end_transmissions()

        return burst

    def end_transmissions(self):
        if self.type == TransmissionTypes.DataTransmission:
            self.end_data_transmission()
        elif self.type == TransmissionTypes.VoiceTransmission:
            self.end_voice_transmission()
