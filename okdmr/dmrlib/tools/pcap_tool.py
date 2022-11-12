#!/usr/bin/env python3
import logging
import sys
import traceback
from argparse import ArgumentParser
from typing import Callable, List, Dict, Optional, Tuple

from bitarray import bitarray
from kaitaistruct import KaitaiStruct
from okdmr.dmrlib.etsi.fec.vbptc_128_72 import VBPTC12873
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.lcss import LCSS
from okdmr.dmrlib.etsi.layer2.elements.preemption_power_indicator import (
    PreemptionPowerIndicator,
)
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.transmission.transmission_watcher import TransmissionWatcher
from okdmr.dmrlib.utils.parsing import try_parse_packet
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.ip_site_connect_heartbeat import IpSiteConnectHeartbeat
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol
from okdmr.kaitai.tools.prettyprint import prettyprint
from scapy.data import UDP_SERVICES
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether
from scapy.utils import PcapReader


class EmbeddedExtractor:
    """
    Helper class, collects
    """

    def __init__(self):
        self.data: Dict[str, Tuple[LCSS, bitarray]] = {}

    def process_packet(self, data: bytes, packet: IP) -> Optional[FullLinkControl]:
        burst: Optional[Burst] = PcapTool.debug_packet(
            data=data, packet=packet, hide_unknown=True, silent=True
        )

        if (
            not burst
            or not burst.has_emb
            or burst.emb.link_control_start_stop == LCSS.SingleFragmentLCorCSBK
            or burst.emb.preemption_and_power_control_indicator
            == PreemptionPowerIndicator.CarriesReverseChannelInformation
        ):
            return

        full_lc: Optional[FullLinkControl] = None
        key: str = f"{packet.src}:{packet.getlayer(UDP).sport}"

        (_lcss, _bits) = self.data.get(key, (LCSS.SingleFragmentLCorCSBK, bitarray()))
        if burst.emb.link_control_start_stop == LCSS.FirstFragmentLC:
            _bits = bitarray()

        _bits += burst.embedded_signalling_bits
        if (
            len(_bits) == 128
            and burst.emb.link_control_start_stop == LCSS.LastFragmentLCorCSBK
        ):
            _vbptc_bits = VBPTC12873.deinterleave_data_bits(
                bits=_bits, include_cs5=True
            )
            full_lc = FullLinkControl.from_bits(_vbptc_bits)
            print(repr(full_lc))

        self.data[key] = (burst.emb.link_control_start_stop, _bits)
        return full_lc


class IPSCAnalyze:
    def __init__(self):
        self.map: Dict[
            Tuple[IpSiteConnectProtocol.SlotTypes, IpSiteConnectProtocol.FrameTypes],
            Dict[str, int],
        ] = dict()

    def process_packet(self, data: bytes, packet: IP) -> None:
        kaitai_pkt: Optional[KaitaiStruct] = try_parse_packet(udpdata=data)
        burst: Optional[Burst] = PcapTool.debug_packet(
            data=data, packet=packet, hide_unknown=True, silent=True
        )
        if isinstance(kaitai_pkt, IpSiteConnectProtocol) and burst:
            rowkey = (kaitai_pkt.slot_type, kaitai_pkt.frame_type)
            data = burst.extract_data()
            if not burst.is_vocoder and data:
                # prettyprint(kaitai_pkt)
                row = self.map.get(rowkey, dict())
                subrowkey = f"voice" if burst.is_vocoder else data.__class__.__name__
                row[data.__class__.__name__] = row.get(data.__class__.__name__, 0) + 1
                self.map[rowkey] = row

    def print_stats(self):
        for ((slot, frame), dt_stats) in self.map.items():
            print(f"SLOT: {slot} FRAME: {frame}")
            for (dt, dt_count) in dt_stats.items():
                print(f"\tCOUNT: {dt_count}\tDT: {dt}")


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
    def debug_packet(
        data: bytes, packet: IP, hide_unknown: bool = False, silent: bool = False
    ) -> Optional[Burst]:
        pkt = try_parse_packet(udpdata=data)
        burst: Optional[Burst] = None
        ip_str: str = f"{packet.src}:{packet.getlayer(UDP).sport}\t-> {packet.dst}:{packet.getlayer(UDP).dport}\t"
        if isinstance(pkt, IpSiteConnectProtocol):
            burst: Burst = Burst.from_hytera_ipsc(pkt)
            if not silent:
                print(
                    f"{ip_str} IPSC TS:{1 if pkt.timeslot_raw == IpSiteConnectProtocol.Timeslots.timeslot_1 else 2} "
                    f"SEQ: {pkt.sequence_number} {repr(burst)}"
                )
        elif isinstance(pkt, Mmdvm2020):
            if isinstance(pkt.command_data, Mmdvm2020.TypeDmrData):
                burst: Burst = Burst.from_mmdvm(pkt.command_data)
                if not silent:
                    print(
                        f"{ip_str} MMDVM TS:{1 if pkt.command_data.slot_no == Mmdvm2020.Timeslots.timeslot_1 else 2} "
                        f"SEQ: {pkt.command_data.sequence_no} {repr(burst)}"
                    )
        elif isinstance(pkt, IpSiteConnectHeartbeat):
            pass
        elif not hide_unknown and not silent:
            print(
                f"Not handled packet [UDP {packet.sport} => {packet.dport}]"
                f" payload {data.hex()}"
                + (
                    f"type {repr(type(pkt.command_data)).rsplit('.')[-1]}"
                    if isinstance(pkt, Mmdvm2020)
                    else f" type {str(type(pkt)).rsplit('.')[-1]}"
                )
            )
            if isinstance(pkt, KaitaiStruct):
                prettyprint(pkt)

        return burst

    # noinspection PyUnusedLocal
    @staticmethod
    def void_packet_callback(data: bytes, packet: IP):
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
                + (
                    f"\t- BLACKLIST"
                    if portnum in ports_blacklist
                    else (f"\t- WHITELIST" if portnum in ports_whitelist else "")
                )
            )
        print(
            "|------------------------------------------------------------------------------|"
        )

    @staticmethod
    def print_pcap(
        files: List[str],
        ports_whitelist: List[int] = [],
        ports_blacklist: List[int] = [],
        ip_whitelist: List[str] = [],
        print_statistics: bool = True,
        print_raw: bool = False,
        callback: Optional[Callable] = None,
        finish_callback: Optional[Callable] = None,
    ) -> Dict[int, int]:
        """

        :param callback:
        :param finish_callback:
        :param files:
        :param ports_whitelist:
        :param ports_blacklist:
        :param ip_whitelist:
        :param print_raw:
        :param print_statistics: whether statistics should be printed directly to stdout
        :return: port statistics (dict [key=sport/dport number] [value=number of packets encountered])
        """
        stats = PcapTool.iter_pcap(
            files=files,
            ports_whitelist=ports_whitelist,
            ports_blacklist=ports_blacklist,
            ip_whitelist=ip_whitelist,
            print_raw=print_raw,
            callback=PcapTool.debug_packet if callback is None else callback,
        )
        if finish_callback:
            finish_callback()
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
        ip_whitelist: List[str] = [],
        print_raw: bool = False,
    ) -> Dict[int, int]:
        """
        Iterate pcap/pcapng file and on each UDP packet found, that matches ports settings, run callback

        :param print_raw:
        :param files:
        :param ports_blacklist:
        :param callback:
        :param ports_whitelist:
        :param ip_whitelist:
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
                        ip_layer = pkt.getlayer(IP)
                        udp_layer = pkt.getlayer(UDP)

                        statistics[udp_layer.sport] = (
                            statistics.get(udp_layer.sport, 0) + 1
                        )
                        statistics[udp_layer.dport] = (
                            statistics.get(udp_layer.dport, 0) + 1
                        )

                        if len(ip_whitelist):
                            # if no whitelisted ips, do not filter
                            if ip_layer.src not in ip_whitelist:
                                continue

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

                        if not ip_layer or not hasattr(udp_layer, "load"):
                            # skip udp packets without any payload
                            continue

                        try:
                            if print_raw:
                                print(udp_layer.load.hex())

                            callback(data=udp_layer.load, packet=ip_layer)
                        except BaseException as e:
                            if isinstance(e, SystemExit) or isinstance(
                                e, KeyboardInterrupt
                            ):
                                # if keyboard interrupt (user trying to stop the tool) or system exit (forced exit from underlying data handling) is caught
                                # do not ignore and raise up
                                raise e
                            print("=" * 30, file=sys.stderr)
                            print(
                                f'Callback raised exception "{e}" for data {udp_layer.load.hex()}',
                                file=sys.stderr,
                            )
                            traceback.print_exc()
                            print("=" * 30, file=sys.stderr)

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
            # bootp, bootp, dns, snmp, snmp traps, ntp, netbios-ns, netbios-dgm, ssdp, mdns, llmnr, dstar dcs (30052,30061)
            default=[
                67,
                68,
                53,
                161,
                162,
                123,
                137,
                138,
                443,
                80,
                1900,
                5353,
                5355,
                30052,
                30061,
            ],
            help="Blacklist UDP ports to exclude from inspection (source or destination or both)",
        )
        parser.add_argument(
            "--no-statistics",
            "-q",
            dest="no_statistics",
            action="store_true",
            default=False,
            help="Suppress statistics at the end of output",
        )
        parser.add_argument(
            "--print-raw",
            "-r",
            dest="print_raw",
            action="store_true",
            default=False,
            help="Print raw UDP Data before parsing the payload",
        )
        parser.add_argument(
            "--extract-embedded-lc",
            "-e",
            dest="extract_embedded_lc",
            action="store_true",
            default=False,
            help="Extract only Embedded LinkControl data and print these",
        )
        parser.add_argument(
            "--observe-transmissions",
            "-o",
            action="store_true",
            default=False,
            dest="observe_transmissions",
            help="Feed bursts to Transmission and debug the data and how the state of terminals changed",
        )
        parser.add_argument(
            "--debug-vocoder-bytes",
            action="store_true",
            default=False,
            dest="debug_vocoder_bytes",
            help="Effective only with --observe-transmissions, will print voice bytes in format ready for vocoder decode",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            default=False,
            dest="verbose",
            help="Verbose logging",
        )
        parser.add_argument(
            "--ipsc",
            action="store_true",
            default=False,
            dest="analyze_ipsc",
            help="Analyze IPSC traffic (map between slot-type, frame-type and data-type)",
        )
        parser.add_argument(
            "--filter-ip",
            dest="filter_ip",
            type=str,
            nargs="+",
            default=[],
            help='Filter traffic by "ORIGIN" IP address(es)',
        )
        return parser

    @staticmethod
    def main(
        arguments: List[str] = [], return_stats: bool = False
    ) -> Optional[Dict[int, int]]:
        """

        :param return_stats: invoking from console_scripts would print stats dict if default was to return stats
        :param arguments: list of cmdline or mock arguments
        :return: packet statistics for all files processed
        """
        if not len(arguments):
            # fallback for running from "python3 -m" or "console_scripts"
            # routine argument necessary for api usage or unit-testing
            arguments = sys.argv[1:]

        args = PcapTool._arguments().parse_args(arguments)

        logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

        callback: Callable = PcapTool.debug_packet
        finish_callback: Optional[Callable] = None
        ipsc_analyze = IPSCAnalyze()
        watcher = TransmissionWatcher().set_debug_voice_bytes(
            do_debug=args.debug_vocoder_bytes
        )
        if args.extract_embedded_lc:
            callback = EmbeddedExtractor().process_packet
        elif args.observe_transmissions:
            callback = watcher.process_packet
            finish_callback = watcher.end_all_transmissions
        elif args.analyze_ipsc:
            callback = ipsc_analyze.process_packet

        stats = PcapTool.print_pcap(
            files=args.files,
            ports_whitelist=args.whitelist_ports,
            ports_blacklist=args.blacklist_ports,
            ip_whitelist=args.filter_ip,
            print_statistics=not args.no_statistics,
            print_raw=args.print_raw,
            callback=callback,
            finish_callback=finish_callback,
        )

        if args.analyze_ipsc:
            ipsc_analyze.print_stats()

        if return_stats:
            return stats


if __name__ == "__main__":
    PcapTool.main()
