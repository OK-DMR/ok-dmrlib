import enum
from datetime import date, time
from typing import Union, Optional, Literal

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


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


class GPSData(BytesInterface):
    def __init__(
        self,
        data_valid: Literal["A", "V"],
        greenwich_time: Union[bytes, time],
        greenwich_date: Union[bytes, date],
        north_south: Literal["N", "S"],
        latitude: Union[bytes, float],
        east_west: Literal["E", "W"],
        longitude: Union[bytes, float],
        speed_knots: Union[bytes, float],
        direction: Union[bytes, int],
    ):
        self.data_valid: Literal["A", "V"] = data_valid
        self.greenwich_time: time = (
            greenwich_time
            if isinstance(greenwich_time, time)
            else time(
                hour=int(greenwich_time[0:2]),
                minute=int(greenwich_time[2:4]),
                second=int(greenwich_time[4:6]),
            )
        )
        self.greenwich_date: date = (
            greenwich_date
            if isinstance(greenwich_date, date)
            else date(
                day=int(greenwich_date[0:2]),
                month=int(greenwich_date[2:4]),
                year=2000 + int(greenwich_date[4:6]),
            )
        )
        self.north_south: Literal["N", "S"] = north_south
        self.east_west: Literal["E", "W"] = east_west
        self.latitude: float = (
            latitude if isinstance(latitude, float) else float(latitude.decode("ascii"))
        )
        self.longitude: float = (
            longitude
            if isinstance(longitude, float)
            else float(longitude.decode("ascii"))
        )
        self.speed_knots: float = (
            speed_knots
            if isinstance(speed_knots, float)
            else float(speed_knots.decode("ascii"))
        )
        self.direction: int = int(direction)

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["GPSData"]:
        assert (
            len(data) == 40
        ), f"GPS Data expects 40 bytes of payload, got {len(data)} value {data.hex()}"
        return GPSData(
            data_valid="A" if data[0:1] == b"A" else "V",
            greenwich_time=data[1:7],
            greenwich_date=data[7:13],
            north_south="N" if data[13:14] == b"N" else "S",
            latitude=data[14:23],
            east_west="E" if data[23:24] == b"E" else "W",
            longitude=data[24:34],
            speed_knots=data[34:37],
            direction=data[37:40],
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return (
            self.data_valid
            + self.greenwich_time.strftime("%H%M%S")
            + self.greenwich_date.strftime("%d%m%y")
            + self.north_south
            + f"{self.latitude:09.4f}"
            + self.east_west
            + f"{self.longitude:010.4f}"
            + f"{self.speed_knots:03}"
            + f"{self.direction:03}"
        ).encode("ascii")

    def __repr__(self) -> str:
        _lat: str = f"{self.latitude:09.4f}"
        _lon: str = f"{self.longitude:010.4f}"

        return (
            ("VALID " if self.data_valid else "INVALID ")
            + self.greenwich_date.strftime("%H:%M:%S ")
            + self.greenwich_time.strftime("%d.%m.%Y ")
            + self.north_south
            + f"{round(float(_lat[:2]) + float(_lat[2:])/60.0, 8)} "
            + self.east_west
            + f"{round(float(_lon[:3]) + float(_lon[3:])/60.0, 8)} "
            + f"speed:{round(self.speed_knots * 1.852, 5)} km/h "
            + f"direction:{self.direction}°"
        )


class LocationProtocol(HDAP):
    """
    Hytera DMR Application Protocol
    """

    def __init__(
        self,
        opcode: Union[bytes, LocationProtocolSpecificService],
        request_id: Union[int, bytes],
        radio_ip: Union[bytes, RadioIP],
        result: Union[int, bytes],
        gpsdata: Union[bytes, GPSData],
        is_reliable: bool = False,
    ):
        super().__init__(is_reliable=is_reliable)
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
        self.radio_ip: RadioIP = (
            radio_ip if isinstance(radio_ip, RadioIP) else RadioIP.from_bytes(radio_ip)
        )
        self.result: LocationProtocolResultCodes = LocationProtocolResultCodes(
            result
            if isinstance(result, int)
            else int.from_bytes(result, byteorder="big")
        )
        self.gpsdata: GPSData = (
            GPSData.from_bytes(gpsdata) if isinstance(gpsdata, bytes) else gpsdata
        )

    def get_service_type(self) -> HyteraServiceType:
        return HyteraServiceType.LP

    def get_opcode(self) -> bytes:
        return self.specific_service.value.to_bytes(length=2, byteorder="big")

    def get_payload(self) -> bytes:
        if self.specific_service == LocationProtocolSpecificService.StandardReport:
            return (
                self.request_id.to_bytes(length=4, byteorder="big")
                + self.radio_ip.as_bytes()
                + self.result.value.to_bytes(length=2, byteorder="big")
                + self.gpsdata.as_bytes()
            )
        raise ValueError(f"LP get_payload not implemented for {self.specific_service}")

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> "LocationProtocol":
        (is_reliable, service_type) = HDAP.get_reliable_and_service(data[0:1])
        assert service_type == HyteraServiceType.LP, f"Expected LP got {service_type}"

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
                is_reliable=is_reliable,
            )

        raise ValueError(f"LP {opcode} not yet implemented")

    def __repr__(self):
        repre: str = f"[LP {self.general_service} {self.specific_service}] "
        if self.specific_service == LocationProtocolSpecificService.StandardReport:
            repre += (
                f"[Request ID {self.request_id}] [Radio IP {self.radio_ip}] "
                f"[Result {self.result}] [GpsData {self.gpsdata}]"
            )
        return repre
