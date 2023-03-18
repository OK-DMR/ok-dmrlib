import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)
from okdmr.dmrlib.transmission.transmission_watcher import TransmissionWatcher
from okdmr.dmrlib.utils.protocol_tool import ProtocolTool


class DmrlibTool(ProtocolTool):
    @staticmethod
    def burst() -> None:
        ProtocolTool._impl(protocol="DMR Burst (72 bytes)", impl=Burst)

    @staticmethod
    def header() -> None:
        ProtocolTool._impl(protocol="DMR Data Header (12 bytes)", impl=DataHeader)

    @staticmethod
    def ipudp() -> None:
        ProtocolTool._impl(
            protocol="DMR IPv4/UDP Compressed header+data", impl=UDPIPv4CompressedHeader
        )

    @staticmethod
    def csbk() -> None:
        ProtocolTool._impl(protocol="DMR CSBK", impl=CSBK)

    @staticmethod
    def full_lc() -> None:
        ProtocolTool._impl(protocol="DMR Full Link Control", impl=FullLinkControl)

    @staticmethod
    def dsdfme() -> None:
        parser: ArgumentParser = ArgumentParser(
            description="DSD-FME Structured DSP processing",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "file", type=str, help=f'Single DSP output file (use dsd-fme "-Q" option)'
        )
        args = parser.parse_args(sys.argv[1:])

        _mapping = {99: "rc burst", 98: "cach burst", 10: "voice burst"}
        watcher: TransmissionWatcher = TransmissionWatcher()

        with open(args.file, "r") as file:
            i = 0
            while i < 200:
                line = file.readline()
                parts = line.split(" ")
                if len(parts) == 3:
                    timeslot = int(parts[0])
                    burst_type = int(parts[1])
                    burst_data = bytes.fromhex(parts[2])
                    if burst_type not in (99, 98):
                        try:
                            b = Burst.from_bytes(
                                data=burst_data,
                                burst_type=(
                                    BurstTypes.Vocoder
                                    if burst_type == 10
                                    else BurstTypes.DataAndControl
                                ),
                            )
                            b.timeslot = timeslot
                            watcher.process_burst(b)
                        except Exception as e:
                            print(e)
                    i += 1
