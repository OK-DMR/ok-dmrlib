from typing import Dict, Optional, List

from scapy.layers.inet import IP

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.hytera.hytera_ipsc_sync import HyteraIPSCSync
from okdmr.dmrlib.hytera.hytera_ipsc_wakeup import HyteraIPSCWakeup
from okdmr.dmrlib.transmission.terminal import Terminal
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
    WithObservers,
)
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class TransmissionWatcher(LoggingTrait, WithObservers):
    def __init__(self, observers: List[TransmissionObserverInterface] = ()) -> None:
        super().__init__(observers=observers)
        self.terminals: Dict[int, Terminal] = {}
        self.last_stream_no: bytes = b""
        self.debug_voice_bytes: bool = False

    def set_debug_voice_bytes(self, do_debug: bool = True) -> "TransmissionWatcher":
        self.debug_voice_bytes = do_debug
        return self

    def ensure_terminal(self, dmrid: int) -> None:
        if dmrid not in self.terminals:
            self.terminals[dmrid] = Terminal(dmrid, self.observers)

    def process_packet(self, data: bytes, packet: IP) -> None:
        # to avoid circular dependency problem import must be local/inline
        from okdmr.dmrlib.tools.pcap_tool import PcapTool

        burst: Optional[Burst] = PcapTool.debug_packet(
            data=data, packet=packet, silent=True
        )
        if burst:
            self.process_burst(burst)
            if self.debug_voice_bytes and burst.is_vocoder:
                import logging

                if self.get_logger().getEffectiveLevel() < logging.DEBUG:
                    self.log_error(f"Cannot print Vocoder with logger not being DEBUG")
                voice_bytes = burst.voice_bits.tobytes()
                if burst.stream_no != self.last_stream_no:
                    self.last_stream_no = burst.stream_no
                    self.log_debug(
                        f"[STREAM {burst.stream_no.hex().upper()}] [FROM {burst.source_radio_id}] [TO {burst.target_radio_id}]"
                    )
                self.log_debug(f"{[x for x in voice_bytes[:9]]},")
                self.log_debug(f"{[x for x in voice_bytes[9:18]]},")
                self.log_debug(f"{[x for x in voice_bytes[18:]]},")

    def process_burst(self, burst: Burst) -> Optional[Burst]:
        if not burst:
            return
        if not burst.target_radio_id:
            if type(burst) not in (HyteraIPSCSync, HyteraIPSCWakeup):
                self.log_warning(
                    f"TransmissionWatcher.process_burst ignoring {burst.__class__.__name__} with target radio id {burst.target_radio_id}"
                )
                self.log_warning(repr(burst))
                return None
        self.ensure_terminal(burst.target_radio_id)
        return self.terminals[burst.target_radio_id].process_incoming_burst(
            burst=burst, timeslot=burst.timeslot
        )

    def end_all_transmissions(self) -> None:
        for terminal in self.terminals.values():
            for timeslot in terminal.timeslots.values():
                timeslot.transmission.end_transmissions()
