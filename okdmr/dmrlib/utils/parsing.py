import traceback
from typing import Optional

from kaitaistruct import KaitaiStruct, ValidationNotEqualError
from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020
from okdmr.kaitai.hytera.hytera_dmr_application_protocol import (
    HyteraDmrApplicationProtocol,
)
from okdmr.kaitai.hytera.hytera_radio_network_protocol import HyteraRadioNetworkProtocol
from okdmr.kaitai.hytera.hytera_simple_transport_reliability_protocol import (
    HyteraSimpleTransportReliabilityProtocol,
)
from okdmr.kaitai.hytera.ip_site_connect_heartbeat import IpSiteConnectHeartbeat
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol
from okdmr.kaitai.hytera.real_time_transport_protocol import RealTimeTransportProtocol


def parse_hytera_data(bytedata: bytes) -> KaitaiStruct:
    if len(bytedata) < 2:
        # probably just heartbeat response
        return IpSiteConnectHeartbeat.from_bytes(bytedata)
    elif bytedata[0:2] == bytes([0x32, 0x42]):
        # HSTRP
        return HyteraSimpleTransportReliabilityProtocol.from_bytes(bytedata)
    elif bytedata[0:1] == bytes([0x7E]):
        # HRNP
        return HyteraRadioNetworkProtocol.from_bytes(bytedata)
    elif (int.from_bytes(bytedata[0:1], byteorder="big") & 0x80) == 0x80 and (
        (int.from_bytes(bytedata[0:1], byteorder="big") & 0xC0) >> 6
    ) == 2:
        rtsp = RealTimeTransportProtocol.from_bytes(bytedata)
        return rtsp
    elif (
        int.from_bytes(bytedata[0:8], byteorder="little") == 0
        or bytedata[0:4] == b"ZZZZ"
        or (
            len(bytedata) >= 21 and bytedata[20] == bytedata[21]
        )  # color code shall be same in both bytes
    ):
        if bytedata[5:9] == bytes([0x00, 0x00, 0x00, 0x14]):
            return IpSiteConnectHeartbeat.from_bytes(bytedata)
        else:
            return IpSiteConnectProtocol.from_bytes(bytedata)
    else:
        # HDAP
        return HyteraDmrApplicationProtocol.from_bytes(bytedata)


def try_parse_packet(udpdata: bytes) -> Optional[KaitaiStruct]:

    try:
        if udpdata[:4] == b"USRP":
            return None
    finally:
        pass

    # Try MMDVM/Homebrew packets
    try:
        mmdvm = Mmdvm2020.from_bytes(udpdata)
        if hasattr(mmdvm, "command_data"):
            return mmdvm
    except BaseException as e:
        if (
            not isinstance(e, EOFError)
            and not isinstance(e, ValidationNotEqualError)
            and not isinstance(e, UnicodeDecodeError)
        ):
            traceback.print_exc()

    # Try Hytera proprietary packets
    try:
        return parse_hytera_data(udpdata)
    except BaseException as e:
        if (
            not isinstance(e, EOFError)
            and not isinstance(e, ValidationNotEqualError)
            and not isinstance(e, UnicodeDecodeError)
        ):
            traceback.print_exc()

    return None
