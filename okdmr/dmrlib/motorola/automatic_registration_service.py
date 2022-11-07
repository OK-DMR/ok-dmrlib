import enum
from typing import Optional, Union, Literal, Tuple

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits, bits_to_bytes
from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


@enum.unique
class ARSPDUType(enum.Enum):
    """
    RESPONSE(USER_REGISTRATION_RESPONSE) for REQUEST(USER
    """

    # these messages originate from RNI (Radio Network Infrastructure) / MSU (Mobile Subscriber Unit)
    DEVICE_REGISTRATION_REQUEST = 0b0000
    DEVICE_DEREGISTATION_NOTICE = 0b0001
    USER_REGISTRATION_REQUEST = 0b0101
    USER_DEREGISTRATION_REQUEST = 0b0110
    # user registration response is same for user registration and deregistration requests
    USER_REGISTRATION_RESPONSE = 0b0111

    # this message originates from ARS Server, checking status of MSU
    STATUS_QUERY_REQUEST = 0b0100

    # this message originates from either party, it provides negative or positive acknowledgement for previous request
    ARS_DEVICE_OR_QUERY_RESPONSE = 0b1111


@enum.unique
class RegistrationEvent(enum.Enum):
    # for user registration request value should be 0b00
    DONT_CARE = 0b00
    # for device registration request value should be in (0b01, 0b10)
    INITIAL = 0b01
    REFRESH = 0b10


@enum.unique
class FailureReason(enum.Enum):
    DEVICE_NOT_AUTHORIZED = 0x00
    USER_ID_NOT_VALID = 0x01
    USER_VALIDATION_TIMEOUT = 0x02
    TRANSMISSION_FAILURE = 0xFF

    @classmethod
    def _missing_(cls, value: object) -> "FailureReason":
        return FailureReason.TRANSMISSION_FAILURE


@enum.unique
class Encoding(enum.Enum):
    UTF8 = 0x00


class FirstHeader(BytesInterface):
    def __init__(
        self,
        has_more_headers: Union[int, bool] = False,
        is_acknowledged: Union[int, bool] = False,
        is_priority: Union[int, bool] = False,
        is_control_message: Union[int, bool] = False,
        pdu_type: Union[int, ARSPDUType] = 0,
    ):
        self.has_more_headers: bool = bool(has_more_headers)
        self.is_acknowledged: bool = bool(is_acknowledged)
        self.is_priority: bool = bool(is_priority)
        self.is_control_message: bool = bool(is_control_message)
        self.pdu_type: ARSPDUType = (
            ARSPDUType(pdu_type) if isinstance(pdu_type, int) else pdu_type
        )

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["FirstHeader"]:
        assert (
            len(data) >= 1
        ), f"ARS::FirstHeader requires 1 byte of data, got {len(data)}"
        bits: bitarray = bytes_to_bits(payload=data[0:1], endian=endian)
        return FirstHeader(
            has_more_headers=bits[0],
            is_acknowledged=bits[1],
            is_priority=bits[2],
            is_control_message=bits[3],
            pdu_type=ba2int(bits[4:8], False),
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bits_to_bytes(
            bitarray(
                [
                    self.has_more_headers,
                    self.is_acknowledged,
                    self.is_priority,
                    self.is_control_message,
                ]
            )
            + int2ba(self.pdu_type.value, length=4, endian=endian, signed=False)
        )

    def __len__(self) -> int:
        # first header is always single byte
        return 1

    def __repr__(self) -> str:
        return (
            f"[{self.pdu_type.name}("
            + (
                ("HAS-EXT " if self.has_more_headers else "")
                + ("IS-ACK " if self.is_acknowledged else "")
                + (f"IS-PRIORITY " if self.is_priority else "")
                + ("IS-CONTROL-MSG " if self.is_control_message else "IS-USER-DATA ")
            ).strip()
            + ")]"
        )


class ResponseSecondHeader(BytesInterface):
    """
    For ARS Device Registration Acknowledgement the header, depending on FirstHeader.is_acknowledged,
    contains the field Refresh Time (success scenario) or Failure Reason (failure scenario)

    For ARS Response USER_REGISTRATION the field is Session Time (success scenario) or Failure Reason (fail scenario)
    """

    def __init__(
        self,
        failure_reason: Optional[Union[int, FailureReason]] = None,
        refresh_time: Optional[int] = None,
    ):
        """

        @param failure_reason: specific per type of request message (PDU)
        @param refresh_time: in 30 minute increments (3 = 90 minutes refresh interval, 0 = refresh not expected)
        """
        assert failure_reason or refresh_time
        self.failure_reason: Optional[FailureReason] = (
            failure_reason
            if failure_reason is None or isinstance(failure_reason, FailureReason)
            else FailureReason(failure_reason)
        )
        self.refresh_time: Optional[int] = refresh_time
        self.first_header: Optional[FirstHeader] = None

    def __len__(self):
        # single byte header
        return 1

    def context(self, first_header: FirstHeader) -> "ResponseSecondHeader":
        self.first_header = first_header
        return self

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        is_failure: bool = not self.first_header or self.first_header.is_acknowledged
        if is_failure and self.failure_reason:
            return bytes([self.failure_reason.value])
        elif not is_failure and self.refresh_time:
            return bytes([self.refresh_time])
        raise ValueError(
            f"ResponseSecondHeader both failure_reason and refresh_time is None"
        )

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["ResponseSecondHeader"]:
        assert len(data) >= 1
        val: int = data[0] & 0x7F
        return ResponseSecondHeader(failure_reason=FailureReason(val), refresh_time=val)

    def __repr__(self) -> str:
        is_failure: bool = not self.first_header or self.first_header.is_acknowledged
        return (
            f"[ResponseSecondHeader"
            + (f" {self.failure_reason}" if is_failure and self.failure_reason else "")
            + (
                f" REFRESH:{self.refresh_time * 30}min"
                if not is_failure and self.refresh_time
                else ""
            )
            + "]"
        )


class RegistrationRequestHeader(BytesInterface):
    """
    Specifies Event and Encoding fields, this header is optional
    """

    def __init__(
        self,
        event: RegistrationEvent = RegistrationEvent.INITIAL,
        encoding: Encoding = Encoding.UTF8,
    ):
        self.event: RegistrationEvent = event
        self.encoding: Encoding = encoding

    def __len__(self):
        # single byte header
        return 1

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["RegistrationRequestHeader"]:
        assert len(data) >= 1
        bits: bitarray = bytes_to_bits(data[0:1], endian=endian)
        return RegistrationRequestHeader(
            event=RegistrationEvent(ba2int(bits[1:3])),
            encoding=Encoding(ba2int(bits[3:8])),
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bytes([(self.event.value << 5) + self.encoding.value])

    def __repr__(self) -> str:
        return f"[RegistrationRequestHeader {self.event} {self.encoding}]"


class AutomaticRegistrationService(BytesInterface, LoggingTrait):
    """
    Automatic Registration Service (ARS)
    """

    CSBK_ARS_MESSAGE_END: bytes = b"\x10\x80"

    def __init__(
        self,
        first_header: Union[bytes, FirstHeader],
        registration_request_header: Optional[RegistrationRequestHeader] = None,
        response_second_header: Optional[ResponseSecondHeader] = None,
        device_identifier: Optional[str] = None,
        user_identifier: Optional[str] = None,
        password: Optional[str] = None,
        is_csbk_ars: bool = False,
    ):
        self.header: FirstHeader = (
            first_header
            if isinstance(first_header, FirstHeader)
            else FirstHeader.from_bytes(first_header)
        )
        self.response_second_header: Optional[
            ResponseSecondHeader
        ] = response_second_header
        self.registration_request_header: Optional[
            RegistrationRequestHeader
        ] = registration_request_header
        self.device_identifier: Optional[str] = device_identifier
        self.user_identifier: Optional[str] = user_identifier
        self.password: Optional[str] = password
        self.is_csbk_ars: bool = is_csbk_ars

    @staticmethod
    def encode_len_val(
        data: Union[bytes, str, None] = None, endian: Literal["big", "little"] = "big"
    ) -> bytes:
        if not data or not hasattr(data, "__len__"):
            # LV is always at least single byte, specifying zero length of (non-existant) following value
            return b"\x00"
        if isinstance(data, str):
            data = data.encode("utf-8")
        return len(data).to_bytes(length=1, byteorder=endian) + data

    @staticmethod
    def read_len_val(data: bytes, idx: int) -> Tuple[int, bytes]:
        val_length: int = data[idx]
        data: bytes = data[idx + 1 : idx + 1 + val_length]
        # new pointer is shifted by 1 (len field) and X (len value)
        return idx + 1 + val_length, data

    def get_payload(self, endian: Literal["big", "little"]) -> bytes:
        payload: bytes = self.header.as_bytes(endian=endian)
        if self.header.pdu_type in (
            ARSPDUType.DEVICE_REGISTRATION_REQUEST,
            ARSPDUType.USER_REGISTRATION_REQUEST,
        ):
            payload += (
                (
                    self.registration_request_header.as_bytes(endian=endian)
                    if self.header.has_more_headers
                    else b""
                )
                + self.encode_len_val(data=self.device_identifier, endian=endian)
                + self.encode_len_val(data=self.user_identifier, endian=endian)
                + self.encode_len_val(data=self.password, endian=endian)
            )
        elif self.header.pdu_type == ARSPDUType.ARS_DEVICE_OR_QUERY_RESPONSE:
            payload += (
                self.response_second_header.as_bytes(endian=endian)
                if self.header.has_more_headers
                else b""
            )
        elif self.header.pdu_type in (
            ARSPDUType.STATUS_QUERY_REQUEST,
            ARSPDUType.DEVICE_DEREGISTATION_NOTICE,
        ):
            # query request does not have own (second) header or payload
            pass
        else:
            raise ValueError(
                f"ARS PDU Type {self.header.pdu_type} not implemented in ARS.get_payload"
            )
        if self.is_csbk_ars:
            payload += AutomaticRegistrationService.CSBK_ARS_MESSAGE_END
        return payload

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["AutomaticRegistrationService"]:
        msg_len: int = int.from_bytes(data[0:2], byteorder=endian, signed=False)
        assert (
            len(data) >= 3 and len(data) >= msg_len
        ), f"ARS message missing, got length {len(data)} expected at least {msg_len}"
        first_header: FirstHeader = FirstHeader.from_bytes(data[2:3])
        idx: int = 3
        is_csbk_ars: bool = (
            data[msg_len : msg_len + 2]
            == AutomaticRegistrationService.CSBK_ARS_MESSAGE_END
        )
        if first_header.pdu_type in (
            ARSPDUType.DEVICE_REGISTRATION_REQUEST,
            ARSPDUType.USER_REGISTRATION_REQUEST,
        ):
            registration_request_header: RegistrationRequestHeader = (
                RegistrationRequestHeader.from_bytes(data[idx : idx + 1])
                if first_header.has_more_headers
                else None
            )
            idx = idx + 1 if first_header.has_more_headers else idx
            (idx, device_identifier) = AutomaticRegistrationService.read_len_val(
                data, idx
            )
            (idx, user_identifier) = AutomaticRegistrationService.read_len_val(
                data, idx
            )
            (idx, password) = AutomaticRegistrationService.read_len_val(data, idx)
            return AutomaticRegistrationService(
                first_header=first_header,
                is_csbk_ars=is_csbk_ars,
                registration_request_header=registration_request_header,
                device_identifier=device_identifier.decode("utf-8"),
                user_identifier=user_identifier.decode("utf-8"),
                password=password.decode("utf-8"),
            )
        elif first_header.pdu_type == ARSPDUType.ARS_DEVICE_OR_QUERY_RESPONSE:
            return AutomaticRegistrationService(
                first_header=first_header,
                is_csbk_ars=is_csbk_ars,
                response_second_header=ResponseSecondHeader.from_bytes(
                    data[idx : idx + 1]
                ).context(first_header)
                if first_header.has_more_headers
                else None,
            )
        elif first_header.pdu_type in (
            ARSPDUType.STATUS_QUERY_REQUEST,
            ARSPDUType.DEVICE_DEREGISTATION_NOTICE,
        ):
            return AutomaticRegistrationService(
                first_header=first_header,
                is_csbk_ars=is_csbk_ars,
            )

        raise ValueError(
            f"ARS PDU Type {first_header.pdu_type} not implemented in ARS.from_bytes"
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        payload: bytes = self.get_payload(endian=endian)
        return len(payload).to_bytes(length=2, byteorder=endian) + payload

    def __len__(self) -> int:
        # payload length (2 bytes) + payload bytes
        return len(self.get_payload(endian="big")) + 2

    def __repr__(self) -> str:
        repre: str = "[ARS] "
        if self.is_csbk_ars:
            repre = "[CSBK ARS] "
        if self.header:
            repre += repr(self.header) + " "
            if self.header.pdu_type in (
                ARSPDUType.DEVICE_REGISTRATION_REQUEST,
                ARSPDUType.USER_REGISTRATION_REQUEST,
            ):
                if self.header.has_more_headers and self.registration_request_header:
                    repre += repr(self.registration_request_header) + " "
                repre += (
                    f"[DEVICE-ID: {self.device_identifier}] "
                    + (
                        f"[USER-ID: {self.user_identifier}] "
                        if self.user_identifier
                        else ""
                    )
                    + (f"[PASSWORD: {self.password}] " if self.password else "")
                )
            elif self.header.pdu_type == ARSPDUType.ARS_DEVICE_OR_QUERY_RESPONSE:
                repre += f"[{'FAILURE' if self.header.is_acknowledged else 'SUCCESS'}] "
                if self.header.has_more_headers and self.response_second_header:
                    repre += (
                        repr(self.response_second_header.context(self.header)) + " "
                    )

        return repre
