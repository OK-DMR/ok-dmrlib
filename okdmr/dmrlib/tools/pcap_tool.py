#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from typing import Callable, List, Dict, Optional

from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol
from scapy.data import UDP_SERVICES
from scapy.layers.inet import UDP
from scapy.layers.l2 import Ether
from scapy.utils import PcapReader

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.lcss import LCSS
from okdmr.dmrlib.utils.parsing import try_parse_packet


# noinspection PyDefaultArgument


class PcapTool:
    """
    Various static methods for working with PCAP/PCAPNG files containing DMR protocols
    """

    @staticmethod
    def get_udp_services_names() -> Dict[int, str]:
        udp_services = dict((k, UDP_SERVICES[k]) for k in UDP_SERVICES.keys())
        # typical dmr / homebrew|mmdvm / hytera / motorola
        udp_services[50000] = "Hytera P2P"
        udp_services[50001] = "Hytera DMR Data"
        udp_services[50002] = "Hytera RDAC"
        udp_services[62031] = "MMDVM / Homebrew"

        udp_services[3002] = "Hytera RRS (Radio)"
        udp_services[3003] = "Hytera GPS (Radio)"
        udp_services[3004] = "Hytera TMS (Radio)"
        udp_services[3005] = "Hytera Call Control (Radio)"
        udp_services[3006] = "Hytera Telemetry (Radio)"
        udp_services[3007] = "Hytera Data Transfer (Radio)"
        udp_services[3009] = "Hytera Self-Defined Message Protocol - SDMP - (Radio)"

        udp_services[30001] = "Hytera RRS Slot 1 (Repeater)"
        udp_services[30002] = "Hytera RRS Slot 2 (Repeater)"
        udp_services[30003] = "Hytera GPS Slot 1 (Repeater)"
        udp_services[30004] = "Hytera GPS Slot 2 (Repeater)"
        udp_services[30005] = "Hytera Telemetry Slot 1 (Repeater)"
        udp_services[30006] = "Hytera Telementry Slot 2 (Repeater)"
        udp_services[30007] = "Hytera TMS (Text Message Service) Slot 1 (Repeater)"
        udp_services[30008] = "Hytera TMS (Text Message Service) Slot 2 (Repeater)"
        udp_services[30009] = "Hytera Call Control Slot 1 (Repeater)"
        udp_services[30010] = "Hytera Call Control Slot 2 (Repeater)"
        udp_services[30012] = "Hytera Voice Service Slot 1 (Repeater)"
        udp_services[30014] = "Hytera Voice Service Slot 2 (Repeater)"
        # some from testing unnamed
        udp_services[5355] = "Multicast DNS / LLMNR"
        udp_services[1900] = "SSDP (Simple Service Discovery Protocol)"

        return udp_services

    @staticmethod
    def debug_packet(data: bytes, packet: UDP) -> Optional[Burst]:
        pkt = try_parse_packet(udpdata=data)
        burst: Optional[Burst] = None
        if isinstance(pkt, IpSiteConnectProtocol):
            burst: Burst = Burst.from_hytera_ipsc(pkt)
        elif isinstance(pkt, Mmdvm2020) and isinstance(
            pkt.command_data, Mmdvm2020.TypeDmrData
        ):
            burst: Burst = Burst.from_mmdvm(pkt.command_data)
        else:
            print(
                f"Not handled packet [UDP {packet.sport} => {packet.dport}]"
                f" payload {data.hex()}"
                + (
                    f"type {repr(type(pkt.command_data)).rsplit('.')[-1]}"
                    if isinstance(pkt, Mmdvm2020)
                    else f" type {str(type(pkt)).rsplit('.')[-1]}"
                )
            )

        return burst

    @staticmethod
    def extract_embedded(data: bytes, packet: UDP) -> Optional[Burst]:
        burst: Optional[Burst] = PcapTool.debug_packet(data, packet)

        if (
            burst
            and burst.has_emb
            and burst.emb.link_control_start_stop
            in (
                LCSS.FirstFragmentLC,
                LCSS.ContinuationFragmentLCorCSBK,
                LCSS.LastFragmentLCorCSBK,
            )
        ):
            print(
                f"{packet.sport}->{packet.dport} {burst.emb.link_control_start_stop} data {burst.embedded_signalling_bits.tobytes().hex()}"
            )

        return burst

    # noinspection PyUnusedLocal
    @staticmethod
    def void_packet_callback(data, packet):
        pass

    @staticmethod
    def print_statistics(
        statistics: Dict[int, int],
        ports_whitelist: List[int] = [],
        ports_blacklist: List[int] = [],
    ):
        udp_services = PcapTool.get_udp_services_names()
        print(
            "|------------------------------------------------------------------------------|"
        )
        print(f"| PORT\t\t| PACKETS COUNT\t\t\t| USUAL SERVICE ON THIS PORT")
        print(
            "|------------------------------------------------------------------------------|"
        )
        for portnum in sorted(statistics):
            print(
                f"| {portnum}\t\t| {statistics[portnum]}\t\t\t\t| {udp_services.get(portnum, 'Unknown')}"
                + (f"\t- BLACKLIST" if portnum in ports_blacklist else "")
                + (f"\t- WHITELIST" if portnum in ports_whitelist else "")
            )
        print(
            "|------------------------------------------------------------------------------|"
        )

    @staticmethod
    def print_pcap(
        files: List[str],
        ports_whitelist: List[int] = [],
        ports_blacklist: List[int] = [],
        print_statistics: bool = True,
        callback: Optional[Callable] = None,
    ) -> Dict[int, int]:
        """

        :param callback:
        :param files:
        :param ports_whitelist:
        :param ports_blacklist:
        :param print_statistics: whether statistics should be printed directly to stdout
        :return: port statistics (dict [key=sport/dport number] [value=number of packets encountered])
        """
        stats = PcapTool.iter_pcap(
            files=files,
            ports_whitelist=ports_whitelist,
            ports_blacklist=ports_blacklist,
            callback=PcapTool.debug_packet if callback is None else callback,
        )
        if print_statistics:
            PcapTool.print_statistics(
                statistics=stats,
                ports_blacklist=ports_blacklist,
                ports_whitelist=ports_whitelist,
            )
        return stats

    @staticmethod
    def iter_pcap(
        files: List[str],
        callback: Optional[Callable] = None,
        ports_whitelist: List[int] = [],
        ports_blacklist: List[int] = [],
    ) -> Dict[int, int]:
        """
        Iterate pcap/pcapng file and on each UDP packet found, that matches ports settings, run callback

        :param files:
        :param ports_blacklist:
        :param callback:
        :param ports_whitelist:
        :return: port statistics (dict [key=sport/dport number] [value=number of packets encountered])
        """
        assert isinstance(ports_blacklist, list)
        assert isinstance(ports_whitelist, list)
        assert callback is None or isinstance(callback, Callable)

        statistics: Dict[int, int] = dict()

        if not callback:
            # set default callback if not provided
            callback = PcapTool.void_packet_callback

        for file in files:
            with PcapReader(file) as reader:
                for pkt in reader:
                    if isinstance(pkt, Ether) and pkt.haslayer(UDP):
                        udp_layer = pkt.getlayer(UDP)

                        statistics[udp_layer.sport] = (
                            statistics.get(udp_layer.sport, 0) + 1
                        )
                        statistics[udp_layer.dport] = (
                            statistics.get(udp_layer.dport, 0) + 1
                        )

                        if len(ports_whitelist):
                            # if no ports whitelisted, do not filter
                            if (
                                udp_layer.sport not in ports_whitelist
                                and udp_layer.dport not in ports_whitelist
                            ):
                                # skip packets on non-whitelisted ports
                                continue

                        if len(ports_blacklist):
                            # if no ports blacklisted, do not filter
                            if (
                                udp_layer.sport in ports_blacklist
                                or udp_layer.dport in ports_blacklist
                            ):
                                # skip packets on blacklisted ports
                                continue

                        if not hasattr(udp_layer, "load"):
                            # skip udp packets without any payload
                            continue

                        callback(data=udp_layer.load, packet=udp_layer)

        return statistics

    @staticmethod
    def _arguments() -> ArgumentParser:
        parser = ArgumentParser(
            description="Read and debug UDP packets in PCAP/PCAPNG file"
        )
        parser.add_argument(
            "files", type=str, nargs="+", help="PCAP or PCAPNG file to be read"
        )
        parser.add_argument(
            "--ports",
            "-p",
            dest="whitelist_ports",
            type=int,
            nargs="+",
            default=[],
            help="Whitelist UDP ports to inspect (source or destination or both)",
        )
        parser.add_argument(
            "--filter",
            "-f",
            dest="blacklist_ports",
            type=int,
            nargs="+",
            # default values in order
            # bootp, bootp, dns, snmp, snmp traps, ntp, netbios-ns, netbios-dgm, mdns, llmnr
            default=[67, 68, 53, 161, 162, 123, 137, 138, 5353, 5355],
            help="Blacklist UDP ports to exclude from inspection (source or destination or both)",
        )
        parser.add_argument(
            "--no-statistics",
            "-q",
            dest="no_statistics",
            type=bool,
            default=False,
        )
        return parser

    @staticmethod
    def main(arguments: List[str]):
        args = PcapTool._arguments().parse_args(arguments)
        PcapTool.print_pcap(
            files=args.files,
            ports_whitelist=args.whitelist_ports,
            ports_blacklist=args.blacklist_ports,
            print_statistics=not args.no_statistics,
            # callback=PcapTool.extract_embedded
        )


if __name__ == "__main__":
    PcapTool.main(sys.argv[1:])
