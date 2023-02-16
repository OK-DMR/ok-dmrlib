from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)
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
