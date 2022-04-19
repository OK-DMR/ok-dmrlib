from typing import Dict, Optional

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.transmission.terminal import Terminal
from okdmr.dmrlib.utils.logging_trait import LoggingTrait
from scapy.layers.inet import IP


class TransmissionWatcher(LoggingTrait):
    def __init__(self):
        self.terminals: Dict[int, Terminal] = {}

    def ensure_terminal(self, dmrid: int):
        if dmrid not in self.terminals:
            self.terminals[dmrid] = Terminal(dmrid)

    def process_packet(self, data: bytes, packet: IP) -> None:
        from okdmr.dmrlib.tools.pcap_tool import PcapTool

        burst: Optional[Burst] = PcapTool.debug_packet(
            data=data, packet=packet, silent=True
        )
        if burst:
            self.process_burst(burst)

    def process_burst(self, burst: Burst) -> None:
        self.ensure_terminal(burst.target_radio_id)
        self.terminals[burst.target_radio_id].process_incoming_burst(
            burst=burst, timeslot=burst.timeslot
        )

    def end_all_transmissions(self):
        for terminal in self.terminals.values():
            for timeslot in terminal.timeslots.values():
                timeslot.transmission.end_transmissions()
