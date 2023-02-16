import enum
from typing import Optional, Literal, Union

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


@enum.unique
class TMPService(enum.Enum):
    """
    Contains both TMP and SDMP services
    """

    SendPrivateMessage = 0xA1
    SendPrivateMessageAck = 0xA2
    SendGroupMessage = 0xB1
    SendGroupMessageAck = 0xB2

    WorkOrderRequest = 0xAC
    WorkOrderReply = 0xAD
    WorkOrderReport = 0xAA
    WorkOrderReportReply = 0xAB
    PrivateShortData = 0xAE
    PrivateShortDataAck = 0xAF
    GroupShortData = 0xBE
    GroupShortDataAck = 0xBF


@enum.unique
class TMPResultCodes(BytesInterface, enum.Enum):
    OK = 0x00
    FAIL = 0x01
    INVALID_PARAMS = 0x03
    CHANNEL_BUSY = 0x04
    RX_ONLY = 0x05
    LOW_BATTERY = 0x06
    PLL_UNLOCK = 0x07
    PRIVATE_CALL_NO_ACK = 0x08
    REPEATER_WAKEUP_FAIL = 0x09
    NOCONTACT = 0x0A
    TX_DENY = 0x0B
    TX_INTERRUPTED = 0x0C

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["TMPResultCodes"]:
        return TMPResultCodes(data[0])

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return int(self.value).to_bytes(length=1, byteorder=endian)


class TextMessageProtocol(HDAP):
    """
    Hytera Text Message Protocol (TMP)
    """

    def __init__(
        self,
        opcode: TMPService,
        source_ip: Optional[RadioIP] = None,
        # target is either RadioIP (for private comms) or Group ID (for group comms)
        destination_ip: Optional[RadioIP] = None,
        is_reliable: bool = False,
        is_confirmed: bool = False,
        has_option: bool = False,
        request_id: int = 0,
        text_data: Union[bytes, str] = b"",
        option_data: Optional[bytes] = None,
        result_code: Optional[TMPResultCodes] = None,
        short_data: bytes = b"",
    ):
        super().__init__(is_reliable=is_reliable)
        self.opcode: TMPService = opcode
        self.has_option: bool = has_option
        self.is_confirmed: bool = is_confirmed
        self.request_id: int = request_id
        self.destination_ip: RadioIP = destination_ip
        self.source_ip: RadioIP = source_ip
        self.text_data: bytes = (
            text_data if isinstance(text_data, bytes) else text_data.encode("utf-16-le")
        )
        self.option_data: Optional[bytes] = option_data
        self.result_code: Optional[TMPResultCodes] = result_code
        self.short_data: bytes = short_data

    def get_service_type(self) -> HyteraServiceType:
        return HyteraServiceType.TMP

    def get_opcode(self) -> bytes:
        return bytes(
            [
                0b0000_0000
                | (0b1000_0000 if self.is_confirmed else 0)
                | (0b0100_0000 if self.has_option else 0),
                self.opcode.value,
            ]
        )

    def is_group(self) -> bool:
        return self.opcode in (
            TMPService.SendGroupMessageAck,
            TMPService.SendGroupMessage,
            TMPService.GroupShortDataAck,
            TMPService.GroupShortData,
        )

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["TextMessageProtocol"]:
        (is_reliable, service_type) = HDAP.get_reliable_and_service(data[0:1])
        assert service_type == HyteraServiceType.TMP, f"Expected TMP got {service_type}"
        opcode: TMPService = TMPService(data[2])
        is_confirmed: bool = bool(data[1] & 0b1000_0000)
        has_option: bool = bool(data[1] & 0b0100_0000)
        payload_idx: int = 7 if has_option else 5
        payload_len = int.from_bytes(data[3:5], byteorder=endian)
        option_data_len: Optional[int] = (
            int.from_bytes(data[5:7], byteorder=endian) if has_option else None
        )
        option_data_start_idx: int = (
            (payload_idx + payload_len - option_data_len - 2)
            if has_option
            else (payload_idx + payload_len)
        )
        option_data: Optional[bytes] = (
            (data[option_data_start_idx : (payload_idx + payload_len - 2)])
            if has_option and option_data_len
            else None
        )

        if opcode in (TMPService.SendPrivateMessage, TMPService.SendGroupMessage):
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8], endian=endian
                ),
                source_ip=RadioIP.from_bytes(
                    data[payload_idx + 8 : payload_idx + 12], endian=endian
                ),
                # utf-16-le text data
                text_data=data[payload_idx + 12 : option_data_start_idx],
            )
        elif opcode == TMPService.SendGroupMessageAck:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8], endian=endian
                ),
                result_code=TMPResultCodes(data[payload_idx + 8]),
            )
        elif opcode == TMPService.SendPrivateMessageAck:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8], endian=endian
                ),
                source_ip=RadioIP.from_bytes(
                    data[payload_idx + 8 : payload_idx + 12], endian=endian
                ),
                result_code=TMPResultCodes(data[payload_idx + 12]),
            )
        elif opcode == TMPService.PrivateShortData:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8], endian=endian
                ),
                source_ip=RadioIP.from_bytes(
                    data[payload_idx + 8 : payload_idx + 12], endian=endian
                ),
                short_data=data[payload_idx + 12 : option_data_start_idx],
            )
        elif opcode == TMPService.PrivateShortDataAck:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8], endian=endian
                ),
                source_ip=RadioIP.from_bytes(
                    data[payload_idx + 8 : payload_idx + 12], endian=endian
                ),
                result_code=TMPResultCodes(data[payload_idx + 12]),
            )
        elif opcode == TMPService.GroupShortData:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8]
                ),
                source_ip=RadioIP.from_bytes(
                    data[payload_idx + 8 : payload_idx + 12], endian=endian
                ),
                short_data=data[payload_idx + 12 : option_data_start_idx],
            )
        elif opcode == TMPService.GroupShortDataAck:
            return TextMessageProtocol(
                opcode=opcode,
                is_reliable=is_reliable,
                is_confirmed=is_confirmed,
                has_option=has_option,
                option_data=option_data,
                request_id=int.from_bytes(
                    data[payload_idx : payload_idx + 4], byteorder=endian
                ),
                destination_ip=RadioIP.from_bytes(
                    data[payload_idx + 4 : payload_idx + 8]
                ),
                result_code=TMPResultCodes(data[payload_idx + 8]),
            )

    def is_tmp(self) -> bool:
        return self.opcode in (
            TMPService.SendPrivateMessage,
            TMPService.SendGroupMessage,
            TMPService.SendGroupMessageAck,
            TMPService.SendPrivateMessageAck,
        )

    def get_payload(self) -> bytes:
        option_data_prefix: bytes = (
            len(self.option_data).to_bytes(length=2, byteorder=self.get_endianness())
            if self.has_option
            else b""
        )
        option_data: bytes = self.option_data if self.has_option else b""
        request_id: bytes = self.request_id.to_bytes(
            length=4, byteorder=self.get_endianness()
        )

        payload: bytes = option_data_prefix + request_id

        if self.is_tmp():
            payload += (
                self.destination_ip.as_bytes(endian=self.get_endianness())
                + (
                    b""
                    if self.opcode == TMPService.SendGroupMessageAck
                    else self.source_ip.as_bytes(endian=self.get_endianness())
                )
                + (
                    self.text_data
                    if self.opcode
                    in (TMPService.SendPrivateMessage, TMPService.SendGroupMessage)
                    else self.result_code.as_bytes(endian=self.get_endianness())
                )
            )
        elif self.opcode == TMPService.PrivateShortData:
            payload += (
                self.destination_ip.as_bytes(endian=self.get_endianness())
                + self.source_ip.as_bytes(endian=self.get_endianness())
                + self.short_data
            )
        elif self.opcode == TMPService.PrivateShortDataAck:
            payload += (
                self.destination_ip.as_bytes(endian=self.get_endianness())
                + self.source_ip.as_bytes(endian=self.get_endianness())
                + self.result_code.as_bytes(endian=self.get_endianness())
            )
        elif self.opcode == TMPService.GroupShortData:
            payload += (
                self.destination_ip.as_bytes(endian=self.get_endianness())
                + self.source_ip.as_bytes(endian=self.get_endianness())
                + self.short_data
            )
        elif self.opcode == TMPService.GroupShortDataAck:
            payload += self.destination_ip.as_bytes(
                endian=self.get_endianness()
            ) + self.result_code.as_bytes(endian=self.get_endianness())

        payload += option_data
        return payload

    def __repr__(self) -> str:
        repre: str = "[TMP "
        if self.is_reliable:
            repre += "RELIABLE "
        if self.is_confirmed:
            repre += "CONFIRMED "
        repre += "GROUP " if self.is_group() else "PRIVATE "
        if self.source_ip:
            repre += f"FROM:{repr(self.source_ip)} "
        if self.destination_ip:
            repre += f"TO:{repr(self.destination_ip)} "
        repre += "] "
        repre += f"[{self.opcode}] "
        if self.request_id:
            repre += f"[REQUEST_ID: {self.request_id}] "
        if self.result_code:
            repre += f"[RESULT: {self.result_code}] "
        if self.has_option and self.option_data:
            repre += f"[OPTION: {self.option_data}] "
        if self.text_data:
            repre += f"[TEXT: {self.text_data.decode('utf-16-le')}] "
        if self.short_data:
            repre += f"[SHORT DATA: {self.short_data.hex()}] "
        return repre
