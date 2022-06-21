from typing import Dict, Optional

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.transmission.terminal import Terminal
from okdmr.dmrlib.utils.logging_trait import LoggingTrait
from scapy.layers.inet import IP


class TransmissionWatcher(LoggingTrait):
    def __init__(self):
        self.terminals: Dict[int, Terminal] = {}
        self.last_stream_no: bytes = b""
        self.debug_voice_bytes: bool = False

    def set_debug_voice_bytes(self, do_debug: bool = True) -> "TransmissionWatcher":
        self.debug_voice_bytes = do_debug
        return self

    def ensure_terminal(self, dmrid: int):
        if dmrid not in self.terminals:
            self.terminals[dmrid] = Terminal(dmrid)

    def process_packet(self, data: bytes, packet: IP) -> None:
        # to avoid circular dependency problem import must be local/inline
        from okdmr.dmrlib.tools.pcap_tool import PcapTool

        burst: Optional[Burst] = PcapTool.debug_packet(
            data=data, packet=packet, silent=True
        )
        if burst:
            self.process_burst(burst)
            if self.debug_voice_bytes and burst.is_vocoder:
                voice_bytes = burst.voice_bits.tobytes()
                if burst.stream_no != self.last_stream_no:
                    self.last_stream_no = burst.stream_no
                    print(
                        f"[STREAM {burst.stream_no}] [FROM {burst.source_radio_id}] [TO {burst.target_radio_id}]"
                    )
                print(f"{[x for x in voice_bytes[:9]]},")
                print(f"{[x for x in voice_bytes[9:18]]},")
                print(f"{[x for x in voice_bytes[18:]]},")

    def process_burst(self, burst: Burst) -> None:
        if not burst.target_radio_id:
            print(
                f"TransmissionWatcher.process_burst ignoring {burst.__class__.__name__} with target radio id {burst.target_radio_id}"
            )
            return
        self.ensure_terminal(burst.target_radio_id)
        self.terminals[burst.target_radio_id].process_incoming_burst(
            burst=burst, timeslot=burst.timeslot
        )

    def end_all_transmissions(self):
        for terminal in self.terminals.values():
            for timeslot in terminal.timeslots.values():
                timeslot.transmission.end_transmissions()
