from typing import Optional

from bitarray import bitarray
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.fec.trellis import Trellis34
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.embedded_signalling import EmbeddedSignalling
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer2.pdu.pi_header import PIHeader
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34Data
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.hytera.hytera_constants import IPSC_KAITAI_VOICE_SLOTS
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits, byteswap_bytes
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class Burst:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 4.2.2   Burst and frame structure
    """

    def __init__(
        self, full_bits: bitarray, burst_type: BurstTypes = BurstTypes.Undefined
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

        self.is_voice_superframe_start = self.sync_or_embedded_signalling in [
            SyncPatterns.Tdma2Voice,
            SyncPatterns.Tdma1Voice,
            SyncPatterns.MsSourcedVoice,
            SyncPatterns.BsSourcedVoice,
        ]
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
        # variables not standardized in ETSI, used for various DMR protocols processing
        self.sequence_no: int = 0
        self.stream_no: bytes = bytes(4)
        self.transmission_type: TransmissionTypes = TransmissionTypes.Idle
        self.data: Optional[BitsInterface] = (
            self.extract_data() if self.is_data_or_control else None
        )

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

        return None

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
        raise AssertionError("Cannot get colour code, no emb and no slot_type")

    def __repr__(self) -> str:
        status: str = f"[{self.sync_or_embedded_signalling.name}] "
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

    @staticmethod
    def from_bits(bits: bitarray, burst_type: BurstTypes) -> "Burst":
        return Burst(full_bits=bits, burst_type=burst_type)

    @staticmethod
    def from_bytes(data: bytes, burst_type: BurstTypes) -> "Burst":
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
        return b

    @staticmethod
    def from_hytera_ipsc(ipsc: IpSiteConnectProtocol) -> "Burst":
        fullbytes: bytes = byteswap_bytes(ipsc.ipsc_payload)[:-1]
        fullbits: bitarray = bytes_to_bits(fullbytes)

        # special cases for IPSC Sync / Wakeup
        if ipsc.slot_type == IpSiteConnectProtocol.SlotTypes.slot_type_sync:
            # prevent circular dependency
            from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync

            return HyteraIPSCSync(full_bits=fullbits)
        elif ipsc.slot_type == IpSiteConnectProtocol.SlotTypes.slot_type_wakeup_request:
            # prevent circular dependency
            from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup

            return HyteraIPSCWakeup(full_bits=fullbits)

        b = Burst(
            full_bits=fullbits,
            burst_type=(
                BurstTypes.Vocoder
                if ipsc.slot_type in IPSC_KAITAI_VOICE_SLOTS
                else BurstTypes.DataAndControl
            ),
        )
        b.set_sequence_no(ipsc.sequence_number)
        return b

    def interleave(self) -> bitarray:
        if not self.is_data_or_control:
            return self.voice_bits

        if self.data_type == DataTypes.Rate34Data:
            return Trellis34.encode(self.data.as_bits())
        elif self.data_type == DataTypes.Rate1Data:
            return self.data.as_bits()
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
            return bits
        elif data_type == DataTypes.Reserved:
            raise ValueError(f"Unknown data type {data_type}")
        else:
            # here expected are: rate 1/2, PI header, voice headeader/terminator, csbk, data header, idle message,
            # response header/data blocks, mbc header/continuation/last block, udt header/continuation/last block
            # unified single block data and more
            # See section B.0 table B.1, FEC and CRC summary, ETSI TS 102 361-1 V2.5.1 (2017-10)
            return BPTC19696.deinterleave_data_bits(bits=bits)
