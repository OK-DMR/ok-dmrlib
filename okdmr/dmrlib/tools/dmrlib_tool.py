from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.utils.protocol_tool import ProtocolTool


class DmrlibTool(ProtocolTool):
    @staticmethod
    def burst() -> None:
        ProtocolTool._impl(protocol="DMR Burst (72 bytes)", impl=Burst)
