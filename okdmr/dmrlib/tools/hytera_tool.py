import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List, Optional

from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.hytera.pdu.hrnp import HRNP
from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP
from okdmr.dmrlib.hytera.pdu.location_protocol import LocationProtocol
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import RadioControlProtocol
from okdmr.dmrlib.hytera.pdu.radio_registration_service import RadioRegistrationService
from okdmr.dmrlib.hytera.pdu.text_message_protocol import TextMessageProtocol
from okdmr.dmrlib.utils.protocol_tool import ProtocolTool


class HyteraTool(ProtocolTool):
    @staticmethod
    def hstrp() -> None:
        HyteraTool._impl(
            protocol="HSTRP - Hytera Simple Transport Reliability Protocol", impl=HSTRP
        )

    @staticmethod
    def hrnp() -> None:
        HyteraTool._impl(protocol="HRNP - Hytera Radio Network Protocol", impl=HRNP)

    @staticmethod
    def hdap() -> None:
        HyteraTool._impl(protocol="HDAP - Hytera DMR Application Protocol", impl=HDAP)

    @staticmethod
    def lp() -> None:
        HyteraTool._impl(impl=LocationProtocol, protocol="LP - Location Protocol")

    @staticmethod
    def rcp() -> None:
        HyteraTool._impl(
            protocol="RCP - Radio Control Protocol", impl=RadioControlProtocol
        )

    @staticmethod
    def rrs() -> None:
        HyteraTool._impl(
            protocol="RRS - Radio Registration Service", impl=RadioRegistrationService
        )

    @staticmethod
    def tmp() -> None:
        HyteraTool._impl(
            protocol="TMP - Text Message Protocol", impl=TextMessageProtocol
        )

    @staticmethod
    def ipsc(arguments: Optional[List[str]] = None) -> None:
        parser: ArgumentParser = ArgumentParser(
            description="IPSC - IP Site Connect",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "hex",
            type=str,
            nargs="+",
            help=f"Hex encoded messages of Hytera IPSC protocol",
        )
        args = (
            parser.parse_args(sys.argv[1:])
            if (not arguments or not len(arguments))
            else arguments
        )
        for hex_msg in args.hex:
            print(hex_msg)
            try:
                pdu = Burst.from_hytera_ipsc(
                    IpSiteConnectProtocol.from_bytes(bytes.fromhex(hex_msg))
                )
                print(repr(pdu))
            except Exception as e:
                print(e, file=sys.stderr)
