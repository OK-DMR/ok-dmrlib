import enum
from typing import Union

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType


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


@enum.unique
class LocationProtocolGeneralService(enum.Enum):
    StandardLocationImmediateService = 0xA0
    EmergencyLocationReportingService = 0xB0
    TriggeredLocationReportingService = 0xC0
    ConditionTriggeredReportingService = 0xD0
    RSSIReportConfiguringService = 0xE0

    @staticmethod
    def from_specific(
        specific_service: LocationProtocolSpecificService,
    ) -> "LocationProtocolGeneralService":
        return LocationProtocolGeneralService(
            specific_service.value.to_bytes(length=2, byteorder="big")[0]
        )


@enum.unique
class LocationProtocolResultCodes(enum.Enum):
    OK = 0
    PositionMethodFailure = 6
    FormatError = 105


class LocationProtocol(HDAP):
    """
    Hytera DMR Application Protocol
    """

    def __init__(
        self,
        opcode: Union[bytes, LocationProtocolSpecificService],
        request_id: Union[int, bytes],
        radio_ip: Union[int, bytes],
        result: Union[int, bytes],
        gpsdata: Union[bytes],
    ):
        self.specific_service = (
            opcode
            if isinstance(opcode, LocationProtocolSpecificService)
            else LocationProtocolSpecificService(
                int.from_bytes(opcode, byteorder="big")
            )
        )
        self.general_service: LocationProtocolGeneralService = (
            LocationProtocolGeneralService.from_specific(self.specific_service)
        )
        self.request_id: int = (
            request_id
            if isinstance(request_id, int)
            else int.from_bytes(request_id, byteorder="big")
        )
        self.radio_ip: int = (
            radio_ip
            if isinstance(radio_ip, int)
            else int.from_bytes(radio_ip, byteorder="big")
        )
        self.result: LocationProtocolResultCodes = LocationProtocolResultCodes(
            result
            if isinstance(result, int)
            else int.from_bytes(result, byteorder="big")
        )
        self.gpsdata: bytes = gpsdata

    def get_service_type(self) -> HyteraServiceType:
        return HyteraServiceType.LP

    def get_opcode(self) -> bytes:
        return self.specific_service.value.to_bytes(length=2, byteorder="big")

    def get_payload(self) -> bytes:
        if self.specific_service == LocationProtocolSpecificService.StandardReport:
            return (
                self.request_id.to_bytes(length=4, byteorder="big")
                + self.radio_ip.to_bytes(length=4, byteorder="big")
                + self.result.value.to_bytes(length=2, byteorder="big")
                + self.gpsdata
            )
        raise NotImplementedError(
            f"LP get_payload not implemented for {self.specific_service}"
        )

    @staticmethod
    def from_bytes(data: bytes) -> "LocationProtocol":
        assert (
            data[0] == 0x08
        ), f"LocationProtocol HDAP PDU should start with 0x08, got {hex(data[0])}"
        opcode = LocationProtocolSpecificService(
            int.from_bytes(data[1:3], byteorder="big")
        )
        if opcode == LocationProtocolSpecificService.StandardReport:
            return LocationProtocol(
                opcode=opcode,
                request_id=data[5:9],
                radio_ip=data[9:13],
                result=data[13:15],
                gpsdata=data[15:55],
            )

        raise NotImplementedError(f"LP {opcode} not yet implemented")

    def __repr__(self):
        repre: str = f"[LP {self.general_service} {self.specific_service}] "
        if self.specific_service == LocationProtocolSpecificService.StandardReport:
            repre += (
                f"[Request ID {self.request_id}] [Radio IP {self.radio_ip}] "
                f"[Result {self.result}] [GpsData {self.gpsdata}]"
            )
        return repre
