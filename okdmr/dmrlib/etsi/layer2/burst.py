from typing import Optional, Literal, Union

import okdmr.dmrlib.hytera.ipsc_elements.slot_type
from bitarray import bitarray
from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.fec.trellis import Trellis34
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.embedded_signalling import EmbeddedSignalling
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer2.pdu.pi_header import PIHeader
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data
from okdmr.dmrlib.etsi.layer2.pdu.rate1_data import Rate1Data
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34Data
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.hytera.hytera_ipsc import HyteraIPSC
from okdmr.dmrlib.hytera.ipsc_elements.timeslot import Timeslot
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface
from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol


class Burst(BytesInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 4.2.2   Burst and frame structure
    """

    def __init__(
        self,
        full_bits: bitarray = bitarray([0] * 264),
        burst_type: BurstTypes = BurstTypes.Undefined,
    ):
        assert (
            len(full_bits) == 264
        ), f"DMR Layer 2 burst must be 264 bits, got {len(full_bits)}"
        self.full_bits: bitarray = full_bits
        self.embedded_signalling_bits: bitarray = self.full_bits[116:148]
        self.sync_or_embedded_signalling: SyncPatterns = SyncPatterns.resolve_bytes(
            bits_to_bytes(self.full_bits[108:156])
        )
        self.voice_bits: bitarray = full_bits[:108] + full_bits[156:]
        self.info_bits_original: bitarray = full_bits[:98] + full_bits[166:]

        self.is_voice_superframe_start: bool = self.sync_or_embedded_signalling in [
            SyncPatterns.Tdma2Voice,
            SyncPatterns.Tdma1Voice,
            SyncPatterns.MsSourcedVoice,
            SyncPatterns.BsSourcedVoice,
        ]
        # automatically set correct burst type for vocoder burst-center patterns
        if self.is_voice_superframe_start:
            burst_type = BurstTypes.Vocoder

        # set initial value, subsequent bursts must be detected and marked manually
        self.is_vocoder: bool = (
            self.is_voice_superframe_start or burst_type == BurstTypes.Vocoder
        ) and not (
            self.sync_or_embedded_signalling
            in [
                SyncPatterns.Tdma1Data,
                SyncPatterns.Tdma2Data,
                SyncPatterns.BsSourcedData,
                SyncPatterns.MsSourcedData,
            ]
        )
        self.voice_burst: VoiceBursts = (
            VoiceBursts.VoiceBurstA
            if self.is_voice_superframe_start
            else VoiceBursts.Unknown
        )
        self.is_data_or_control = (
            burst_type == BurstTypes.DataAndControl
            or self.sync_or_embedded_signalling
            in [
                SyncPatterns.Tdma1Data,
                SyncPatterns.Tdma2Data,
                SyncPatterns.BsSourcedData,
                SyncPatterns.MsSourcedData,
            ]
        )

        # automatically set correct burst type for data burst-center patterns
        if self.is_data_or_control:
            burst_type = BurstTypes.DataAndControl

        self.has_emb: bool = (
            self.sync_or_embedded_signalling == SyncPatterns.EmbeddedSignalling
            and not self.is_voice_superframe_start
        )
        self.emb: Optional[EmbeddedSignalling] = (
            None
            if not self.has_emb
            else EmbeddedSignalling.from_bits(
                self.full_bits[108:116] + self.full_bits[148:156]
            )
        )

        self.has_slot_type: bool = self.is_data_or_control
        self.slot_type: Optional[SlotType] = (
            None
            if not self.has_slot_type
            else SlotType.from_bits(self.full_bits[98:108] + self.full_bits[156:166])
        )

        self.info_bits_deinterleaved: Optional[bitarray] = (
            None
            if not self.is_data_or_control
            else self.__class__.deinterleave(
                bits=self.info_bits_original, data_type=self.data_type
            )
        )
        # variables not standardized in ETSI Layer II Burst, used for various DMR protocols processing
        self.timeslot: int = 1
        self.hytera_ipsc: Optional[HyteraIPSC] = None
        self.source_radio_id: int = 0
        self._target_radio_id: int = 0
        self._target_radio_id_resolve_attempt: bool = False
        self.sequence_no: int = 0
        self.stream_no: bytes = bytes(4)
        self.transmission_type: TransmissionTypes = TransmissionTypes.Idle
        self.data: Optional[BitsInterface] = (
            self.extract_data() if self.is_data_or_control else None
        )

    @property
    def target_radio_id(self) -> int:
        if self._target_radio_id == 0 and not self._target_radio_id_resolve_attempt:
            self._target_radio_id = self.guess_target_radio_id()
            self._target_radio_id_resolve_attempt = True
        return self._target_radio_id

    @target_radio_id.setter
    def target_radio_id(self, target_radio_id: int) -> None:
        self._target_radio_id = target_radio_id

    def guess_target_radio_id(self) -> int:
        """
        Will return 0 if target cannot be guessed from contents of burst
        """
        if isinstance(self.data, CSBK):
            return int(self.data.target_address or 0)
        elif isinstance(self.data, DataHeader):
            return int(self.data.llid_destination or 0)

        return 0

    def extract_data(self) -> Optional[BitsInterface]:
        if self.data_type == DataTypes.CSBK:
            return CSBK.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.VoiceLCHeader:
            return FullLinkControl.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.PIHeader:
            return PIHeader.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.TerminatorWithLC:
            return FullLinkControl.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.DataHeader:
            return DataHeader.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.Rate34Data:
            return Rate34Data.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.Rate12Data:
            return Rate12Data.from_bits(self.info_bits_deinterleaved)
        elif self.data_type == DataTypes.Rate1Data:
            return Rate1Data.from_bits(self.info_bits_deinterleaved)

        return None

    def set_is_voice(self, burst_id: VoiceBursts = VoiceBursts.Unknown) -> "Burst":
        self.is_vocoder = burst_id != VoiceBursts.Unknown
        self.voice_burst = burst_id
        return self

    def set_sequence_no(self, sequence_no: int) -> "Burst":
        self.sequence_no = sequence_no
        return self

    def set_stream_no(self, stream_no: bytes) -> "Burst":
        self.stream_no = stream_no
        return self

    def debug(self, printout: bool = True) -> str:
        self_repr = repr(self)
        if printout:
            print(self_repr)
        return self_repr

    @property
    def data_type(self) -> DataTypes:
        if self.has_slot_type:
            return self.slot_type.data_type
        return DataTypes.Reserved

    @property
    def colour_code(self) -> int:
        if self.has_emb:
            return self.emb.colour_code
        elif self.has_slot_type:
            return self.slot_type.colour_code
        raise ValueError("Cannot get colour code, no emb and no slot_type")

    def __repr__(self) -> str:
        status: str = (
            f"BURST[{self.as_bytes().hex()}] [{self.sync_or_embedded_signalling.name}] "
        )

        if self.is_vocoder:
            status += f" [{self.voice_burst}]"
            status += f" [VOCODER BYTES: {self.voice_bits.tobytes().hex()}]"

        if self.has_emb:
            status += repr(self.emb)
        elif self.has_slot_type:
            status += repr(self.slot_type)

        if self.data:
            status += "\n\t" + repr(self.data)

        return status

    def as_bits(self) -> bitarray:
        if self.is_data_or_control:
            data_bits_interleaved = self.interleave()
            slot_bits = self.slot_type.as_bits()
            return (
                data_bits_interleaved[:98]
                + slot_bits[:10]
                + (
                    self.emb.as_bits()
                    if self.has_emb
                    else self.sync_or_embedded_signalling.as_bits()
                )
                + slot_bits[10:]
                + data_bits_interleaved[98:]
            )
        emb_bits = self.emb.as_bits() if self.has_emb else None
        center_bits = (
            (emb_bits[:8] + self.embedded_signalling_bits + emb_bits[8:])
            if self.has_emb
            else self.sync_or_embedded_signalling.as_bits()
        )
        return self.voice_bits[:108] + center_bits + self.voice_bits[108:]

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bits_to_bytes(self.as_bits())

    @staticmethod
    def from_bits(bits: bitarray, burst_type: BurstTypes) -> "Burst":
        return Burst(full_bits=bits, burst_type=burst_type)

    @staticmethod
    def from_bytes(
        data: bytes, burst_type: BurstTypes = BurstTypes.DataAndControl
    ) -> "Burst":
        return Burst(full_bits=bytes_to_bits(data), burst_type=burst_type)

    @staticmethod
    def from_mmdvm(mmdvm: Mmdvm2020.TypeDmrData) -> "Burst":
        b = Burst(
            full_bits=bytes_to_bits(mmdvm.dmr_data),
            burst_type=(
                BurstTypes.DataAndControl
                if mmdvm.frame_type == 2
                else BurstTypes.Vocoder
            ),
        )
        b.set_stream_no(mmdvm.stream_id)
        b.set_sequence_no(mmdvm.sequence_no)
        b.source_radio_id = mmdvm.source_id
        b.target_radio_id = mmdvm.target_id
        b.timeslot = 1 if mmdvm.slot_no == Mmdvm2020.Timeslots.timeslot_1 else 2
        return b

    @staticmethod
    def from_hytera_ipsc(ipsc: Union[bytes, IpSiteConnectProtocol]) -> "Burst":
        ipsc: HyteraIPSC = (
            HyteraIPSC.from_ipsc_bytes(ipsc)
            if isinstance(ipsc, bytes)
            else HyteraIPSC.from_kaitai(ipsc)
        )

        full_bytes: bytes = ipsc.payload
        full_bits: bitarray = bytes_to_bits(full_bytes)

        b: Optional[Burst] = None
        # special cases for IPSC Sync / Wakeup
        if (
            ipsc.slot_type
            == okdmr.dmrlib.hytera.ipsc_elements.slot_type.SlotType.VoiceOrDataSync
        ):
            # prevent circular dependency
            from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync

            b = HyteraIPSCSync.from_bits(
                bits=full_bits, burst_type=BurstTypes.Undefined
            )
        elif ipsc.is_wakeup():
            # prevent circular dependency
            from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup

            b = HyteraIPSCWakeup.from_bits(
                bits=full_bits, burst_type=BurstTypes.Undefined
            )
        else:
            b = Burst(
                full_bits=full_bits,
                burst_type=(
                    BurstTypes.Vocoder
                    if okdmr.dmrlib.hytera.ipsc_elements.slot_type.SlotType.is_vocoder(
                        ipsc.slot_type
                    )
                    else BurstTypes.DataAndControl
                ),
            )

        b.hytera_ipsc = ipsc
        b.set_sequence_no(ipsc.sequence_number)
        b.source_radio_id = ipsc.source_radio_id
        b.target_radio_id = ipsc.destination_radio_id
        b.timeslot = 1 if ipsc.timeslot == Timeslot.Timeslot_1 else 2
        return b

    def interleave(self) -> bitarray:
        if not self.is_data_or_control:
            return self.voice_bits

        if self.data_type == DataTypes.Rate34Data:
            return Trellis34.encode(self.data.as_bits())
        elif self.data_type == DataTypes.Rate1Data:
            bits = self.data.as_bits()
            # Rate 1 uncoded data bits (192) + 4 padding bits in the middle makes full 196 bits on-air payload
            return bits[:96] + bitarray([0, 0, 0, 0]) + bits[96:]
        elif self.data_type == DataTypes.Reserved:
            raise ValueError(
                f"Unknown data type {self.data_type} with data {self.data}"
            )
        else:
            return BPTC19696.encode(self.data.as_bits())

    @staticmethod
    def deinterleave(bits: bitarray, data_type: DataTypes) -> bitarray:
        if data_type == DataTypes.Rate34Data:
            return Trellis34.decode(bits)
        elif data_type == DataTypes.Rate1Data:
            # Table B.10B: Transmit bit ordering for rate 1 coded data
            return bits[:96] + bits[100:]
        elif data_type == DataTypes.Reserved:
            raise ValueError(f"Unknown data type {data_type}")
        else:
            # here expected are: rate 1/2, PI header, voice headeader/terminator, csbk, data header, idle message,
            # response header/data blocks, mbc header/continuation/last block, udt header/continuation/last block
            # unified single block data and more
            # See section B.0 table B.1, FEC and CRC summary, ETSI TS 102 361-1 V2.5.1 (2017-10)
            return BPTC19696.deinterleave_data_bits(bits=bits)
