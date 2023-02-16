from typing import Dict

from okdmr.dmrlib.hytera.pdu.location_protocol import (
    LocationProtocol,
    GPSData,
    LocationProtocolSpecificService,
)
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP


def test_location_protocol():
    msgs: Dict[str, Dict[str, any]] = {
        # standard report
        # [LP LocationProtocolGeneralService.StandardLocationImmediateService LocationProtocolSpecificService.StandardReport] [Request ID 1] [Radio IP 10.33.16.221] [Result LocationProtocolResultCodes.OK] [GpsData VALID 00:00:00 01.01.1900 N47.31341833 E18.90731167 speed:0.1852 km/h direction:121°]
        "08a0020032000000010a2110dd0000413138333634383236313031354e343731382e383035314530313835342e34333837302e313132310b03": {},
        # standard report
        # [LP LocationProtocolGeneralService.StandardLocationImmediateService LocationProtocolSpecificService.StandardReport] [Request ID 3] [Radio IP 0.35.55.251] [Result LocationProtocolResultCodes.OK] [GpsData VALID N50.06461833 E14.44217 speed:0.0 km/h direction:0°]
        "08a002003200000003002337fb0000410000000000000000000000004e353030332e383737314530313432362e353330320000000000007003": {},
    }
    for msg in msgs:
        msg_bytes = bytes.fromhex(msg)
        lp = LocationProtocol.from_bytes(msg_bytes)
        if msg_bytes != lp.as_bytes():
            print(msg.lower())
            print(lp.as_bytes().hex().lower())
        assert lp.as_bytes() == msg_bytes
        assert len(repr(lp)) > 0
        print(repr(lp))


def test_gpsdata():
    assert isinstance(GPSData.zero(), GPSData)


def test_request():
    lp: LocationProtocol = LocationProtocol(
        opcode=LocationProtocolSpecificService.StandardRequest,
        request_id=1,
        radio_ip=RadioIP(radio_id=1001),
    )
    assert lp.as_bytes() == LocationProtocol.from_bytes(lp.as_bytes()).as_bytes()
    assert len(repr(lp))
