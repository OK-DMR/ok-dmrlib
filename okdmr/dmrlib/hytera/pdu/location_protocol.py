import enum
from typing import Union

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType


@enum.unique
class LocationProtocolGeneralService(enum.Enum):
    StandardLocationImmediateService = 0xA0
    EmergencyLocationReportingService = 0xB0
    TriggeredLocationReportingService = 0xC0
    ConditionTriggeredReportingService = 0xD0
    RSSIReportConfiguringService = 0xE0


@enum.unique
class LocationProtocolSpecificService(enum.Enum):
    StandardRequest = 0xA001
    StandardReport = 0xA002
    StandardReportVariableData = 0xA003
    StandardReportWithRSSI = 0xA004

    EmergencyReportStopRequest = 0xB001
    EmergencyReportStopAnswer = 0xB002
    EmergencyReport = 0xB003
    EmergencyReportVariableData = 0xB004

    TriggeredReportRequest = 0xC001
    TriggeredReportAnswer = 0xC002
    TriggeredReport = 0xC003
    TriggeredReportStopRequest = 0xC004
    TriggeredReportStopAnswer = 0xC005

    ConditionReportRequest = 0xD001
    ConditionReportAnswer = 0xD002
    ConditionReport = 0xD003
    ConditionReportWithRSSI = 0xD004
    ConditionReportVariableData = 0xD005
    ConditionQuickGPSRequest = 0xD011
    ConditionQuickGPSAnswer = 0xD012

    RSSIReportConfigRequest = 0xE001
    RSSIReportConfigAnswer = 0xE002


class LocationProtocol(HDAP):
    """
    Hytera DMR Application Protocol
    """

    def __init__(self, opcode: Union[bytes, int]):
        super().__init__(pdu_type=HyteraServiceType.LP)
        self.general_service = LocationProtocolGeneralService(opcode[0])
        self.specific_service = LocationProtocolSpecificService(
            int.from_bytes(opcode, byteorder="big")
        )

    @staticmethod
    def from_bytes(data: bytes) -> "LocationProtocol":
        assert (
            data[0] == 0x08
        ), f"LocationProtocol header does not match, expected 0x08, got {data[0:1].hex()}"
        return LocationProtocol(
            opcode=data[1:3],
        )

    def __repr__(self):
        return f"[LP {self.general_service} {self.specific_service}]"
