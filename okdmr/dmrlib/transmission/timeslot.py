from datetime import *
from time import time
from typing import List

from kaitaistruct import KaitaiStruct
from okdmr.kaitai.etsi.dmr_data_header import DmrDataHeader
from okdmr.kaitai.etsi.link_control import LinkControl

from okdmr.dmrlib.transmission.burst_info import BurstInfo
from okdmr.dmrlib.transmission.transmission import Transmission
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
)


class Timeslot(TransmissionObserverInterface):
    def __init__(self, timeslot: int):
        self.timeslot = timeslot
        self.last_packet_received: float = 0
        self.rx_sequence: int = 0
        self.reset_rx_sequence: bool = False
        self.transmission: Transmission = Transmission(self)
        self.color_code: int = 1

    def voice_transmission_ended(
        self, voice_header: LinkControl, blocks: List[KaitaiStruct]
    ):
        self.reset_rx_sequence = True

    def data_transmission_ended(
        self, transmission_header: DmrDataHeader, blocks: List[KaitaiStruct]
    ):
        self.reset_rx_sequence = True

    def get_rx_sequence(self, increment: bool = True) -> int:
        if increment:
            self.rx_sequence = (self.rx_sequence + 1) & 255
        return self.rx_sequence

    def process_burst(self, dmrdata: BurstInfo) -> BurstInfo:
        self.last_packet_received = time()
        if dmrdata.color_code != 0:
            self.color_code = dmrdata.color_code

        out: BurstInfo = (
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
