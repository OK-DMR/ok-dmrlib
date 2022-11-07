import enum
from typing import Optional, Union, Literal

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


@enum.unique
class RRSTypes(BytesInterface, enum.Enum):
    RadioRegistrationRequest = 0x03
    RadioRegistrationAnswer = 0x80
    RadioGoingOffline = 0x01
    RegistrationStatusCheckRequest = 0x02
    RegistrationStatusCheckAnswer = 0x82

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bytes([self.value])


@enum.unique
class RRSResult(BytesInterface, enum.Enum):
    Success = 0x00
    PasswordError = 0x02
    OtherFailure = 0x01

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bytes([self.value])


@enum.unique
class RRSRadioState(BytesInterface, enum.Enum):
    Online = 0x00
    Offline = 0x01

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bytes([self.value])


class RadioRegistrationService(HDAP):
    """
    RRS - Radio Registration Service
    """

    def __init__(
        self,
        opcode: RRSTypes,
        is_reliable: bool = False,
        radio_ip: Union[bytes, RadioIP] = b"",
        result: Union[int, RRSResult] = RRSResult.Success,
        renew_time_seconds: int = 1,
        radio_state: Union[int, RRSRadioState] = RRSRadioState.Online,
    ):
        super().__init__(is_reliable=is_reliable)
        self.opcode: RRSTypes = opcode
        self.radio_ip: RadioIP = (
            radio_ip if isinstance(radio_ip, RadioIP) else RadioIP.from_bytes(radio_ip)
        )
        self.result: RRSResult = (
            result if isinstance(result, RRSResult) else RRSResult(result)
        )
        assert (
            0x0001 <= renew_time_seconds <= 0xFFFE
        ), f"RRS renewal period exceeds maximum value of {0xFFFE} seconds"
        self.renew_time_seconds: int = renew_time_seconds
        self.radio_state: RRSRadioState = (
            radio_state
            if isinstance(radio_state, RRSRadioState)
            else RRSRadioState(radio_state)
        )

    def get_opcode(self) -> bytes:
        return bytes([0x00, self.opcode.value])

    def get_service_type(self) -> HyteraServiceType:
        return HyteraServiceType.RRS

    def get_payload(self) -> bytes:
        if self.opcode in (
            RRSTypes.RadioRegistrationRequest,
            RRSTypes.RadioGoingOffline,
            RRSTypes.RegistrationStatusCheckRequest,
        ):
            return self.radio_ip.as_bytes()
        elif self.opcode == RRSTypes.RadioRegistrationAnswer:
            return (
                self.radio_ip.as_bytes()
                + self.result.as_bytes()
                + self.renew_time_seconds.to_bytes(length=4, byteorder="big")
            )
        elif self.opcode == RRSTypes.RegistrationStatusCheckAnswer:
            return self.radio_ip.as_bytes() + self.radio_state.as_bytes()
        raise ValueError(f"{self.opcode} not yet implemented")

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["RadioRegistrationService"]:
        (is_reliable, service_type) = HDAP.get_reliable_and_service(data[0:1])
        assert service_type == HyteraServiceType.RRS, f"Expected RRS got {service_type}"
        opcode: RRSTypes = RRSTypes(data[2])
        if opcode in (
            RRSTypes.RadioRegistrationRequest,
            RRSTypes.RadioGoingOffline,
            RRSTypes.RegistrationStatusCheckRequest,
        ):
            return RadioRegistrationService(
                is_reliable=is_reliable, opcode=opcode, radio_ip=data[5:9]
            )
        elif opcode == RRSTypes.RadioRegistrationAnswer:
            return RadioRegistrationService(
                is_reliable=is_reliable,
                opcode=opcode,
                radio_ip=data[5:9],
                result=data[9],
                renew_time_seconds=int.from_bytes(data[10:14], byteorder="big"),
            )
        elif opcode == RRSTypes.RegistrationStatusCheckAnswer:
            return RadioRegistrationService(
                is_reliable=is_reliable,
                opcode=opcode,
                radio_ip=data[5:9],
                radio_state=data[9],
            )

    def __repr__(self) -> str:
        r: str = f"[{self.opcode}]"
        # TODO add more descriptive fields
        return r
