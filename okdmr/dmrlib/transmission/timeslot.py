from datetime import *
from time import time
from typing import List

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.transmission.transmission import Transmission
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
    WithObservers,
)
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class Timeslot(WithObservers):
    def __init__(
        self, timeslot: int, observers: List[TransmissionObserverInterface] = ()
    ):
        super().__init__(observers=observers)
        self.timeslot = timeslot
        self.last_packet_received: float = 0
        self.rx_sequence: int = 0
        self.reset_rx_sequence: bool = False
        self.transmission: Transmission = Transmission(self)
        self.color_code: int = 0

    def voice_transmission_ended(
        self, voice_header: FullLinkControl, blocks: List[BitsInterface]
    ):
        super().voice_transmission_ended(voice_header=voice_header, blocks=blocks)
        self.reset_rx_sequence = True

    def data_transmission_ended(
        self, transmission_header: DataHeader, blocks: List[BitsInterface]
    ):
        super().data_transmission_ended(
            transmission_header=transmission_header, blocks=blocks
        )
        self.reset_rx_sequence = True

    def get_rx_sequence(self, increment: bool = True) -> int:
        if increment:
            self.rx_sequence = (self.rx_sequence + 1) & 255
        return self.rx_sequence

    def process_burst(self, dmrdata: Burst) -> Burst:
        self.last_packet_received = time()
        if (
            not dmrdata.is_voice_superframe_start
            or dmrdata.sync_or_embedded_signalling == SyncPatterns.Reserved
        ):
            # Voice burst with SYNC (MS/BS Sourced, TDMA TS1/2, Reserved) do not carry CC information
            self.color_code = dmrdata.colour_code

        out: Burst = (
            self.transmission.process_packet(dmrdata)
            .set_sequence_no(self.get_rx_sequence())
            .set_stream_no(self.transmission.stream_no)
        )

        if self.reset_rx_sequence:
            self.reset_rx_sequence = False
            self.rx_sequence = 0

        return out

    def debug(self, printout: bool = True) -> str:
        status: str = (
            f"[TS {self.timeslot}] "
            f"[STATUS {self.transmission.type.name}] "
            f"[LAST PACKET {datetime.fromtimestamp(self.last_packet_received)} {self.transmission.last_burst_data_type.name}] "
            f"[COLOR CODE {self.color_code}]"
        )
        if printout:
            print(status)
        return status
