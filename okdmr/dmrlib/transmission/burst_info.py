import datetime
from typing import Optional

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_types import SyncTypes
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.etsi.layer2.pdu.embedded_signalling import EmbeddedSignalling
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


class BurstInfo:
    def __init__(self, data: bytes):
        self.data_bits: bitarray = bytes_to_bits(data)
        self.payload_bits: bitarray = self.data_bits[:108] + self.data_bits[156:]
        self.info_bits: bitarray = self.data_bits[:98] + self.data_bits[166:]
        self.sync_or_emb: bitarray = self.data_bits[108:156]
        self.embedded_signalling_bits: bitarray = self.data_bits[116:148]
        self.sync_type: SyncTypes = SyncTypes.Reserved

        self.has_emb: bool = False
        self.emb: Optional[EmbeddedSignalling] = None

        self.has_slot_type: bool = False
        self.slot_type: Optional[SlotType] = None

        self.is_voice_superframe_start: bool = False
        self.is_data_or_control: bool = False
        self.is_valid: bool = False
        self.color_code: int = 0
        self.sequence_no: int = 0
        self.stream_no: bytes = bytes(4)
        self.data_type: DataTypes = DataTypes.Reserved
        self.voice_burst: VoiceBursts = VoiceBursts.Unknown

        self.detect_sync_type()
        self.parse_slot_type()
        self.parse_emb()

    def set_sequence_no(self, sequence_no: int) -> "BurstInfo":
        self.sequence_no = sequence_no
        return self

    def set_stream_no(self, stream_no: bytes) -> "BurstInfo":
        self.stream_no = stream_no
        return self

    def detect_sync_type(self):
        self.sync_type = SyncTypes(ba2int(self.sync_or_emb))

        self.is_voice_superframe_start = self.sync_type in [
            SyncTypes.Tdma2Voice,
            SyncTypes.Tdma1Voice,
            SyncTypes.MsSourcedVoice,
            SyncTypes.BsSourcedVoice,
        ]
        self.is_data_or_control = self.sync_type in [
            SyncTypes.Tdma1Data,
            SyncTypes.Tdma2Data,
            SyncTypes.BsSourcedData,
            SyncTypes.MsSourcedData,
        ]

        self.has_slot_type = self.is_data_or_control
        self.has_emb = (
            self.sync_type == SyncTypes.EmbeddedData
            and not self.is_voice_superframe_start
        )

    def parse_slot_type(self):
        if not self.is_data_or_control:
            return
        """Section 6.2 Data and control"""
        slot_type_bits = self.data_bits[98:108] + self.data_bits[156:166]
        self.slot_type = SlotType.from_bits(slot_type_bits)

    def parse_emb(self):
        if not self.has_emb or self.is_voice_superframe_start:
            return
        emb_bits = self.data_bits[108:116] + self.data_bits[148:156]
        self.emb = EmbeddedSignalling.from_bits(emb_bits)

    def debug(self, printout: bool = True) -> str:
        status: str = f"{str(datetime.datetime.now())} [{self.sync_type.name}] [DATA TYPE {self.data_type.name}] "
        if self.has_emb:
            status += repr(self.emb)
        elif self.has_slot_type:
            status += repr(self.slot_type)
        if printout:
            print(status)
        return status
