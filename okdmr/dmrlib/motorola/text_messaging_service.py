import enum
from typing import Optional, Literal, Union, Tuple

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits, bits_to_bytes
from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


@enum.unique
class TMSEncoding(enum.Enum):
    """
    encoding field of TMS protocol
    """

    UNDEFINED = 0x00
    UCS2_LE = 0x04

    @classmethod
    def _missing_(cls, value: object) -> "TMSEncoding":
        return TMSEncoding.UNDEFINED


@enum.unique
class TMSPDUType(enum.Enum):
    """
    Tuple id (is_control_message, bits)
    """

    # system / control messages - no payload
    SERVICE_AVAILABILITY = (True, 0b0000)
    # Acknowledge service availability or text message - no payload
    TMS_ACKNOWLEDGEMENT = (True, 0b1111)
    # user text message -
    SIMPLE_TEXT_MESSAGE = (False, 0b0000)


@enum.unique
class TMSDeviceCapability(enum.Enum):
    LIMITED = 0b00
    INTERNAL = 0b01
    EXTERNAL = 0b10
    FULL = 0b11


class FirstHeader(BytesInterface):
    def __init__(
        self,
        has_more_headers: Union[int, bool] = False,
        is_acknowledged: Union[int, bool] = False,
        is_reserved: Union[int, bool] = False,
        is_control_message: Union[int, bool] = False,
        pdu_type: Union[int, TMSPDUType] = 0,
    ):
        self.has_more_headers: bool = bool(has_more_headers)
        self.is_acknowledged: bool = bool(is_acknowledged)
        self.is_reserved: bool = bool(is_reserved)
        self.pdu_type: TMSPDUType = (
            TMSPDUType((is_control_message, pdu_type))
            if isinstance(pdu_type, int)
            else pdu_type
        )
        self.is_control_message: bool = bool(self.pdu_type.value[0])

    def set_has_more_headers(self, has: bool) -> "FirstHeader":
        self.has_more_headers = has
        return self

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["FirstHeader"]:
        assert (
            len(data) >= 1
        ), f"TMS::FirstHeader requires 1 byte of data, got {len(data)}"
        bits: bitarray = bytes_to_bits(payload=data[0:1], endian=endian)
        return FirstHeader(
            has_more_headers=bits[0],
            is_acknowledged=bits[1],
            is_reserved=bits[2],
            is_control_message=bits[3],
            pdu_type=ba2int(bits[4:8], False),
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bits_to_bytes(
            bitarray(
                [
                    self.has_more_headers,
                    self.is_acknowledged,
                    # reserved for future use
                    self.is_reserved or self.pdu_type == TMSPDUType.SIMPLE_TEXT_MESSAGE,
                    self.is_control_message,
                ]
            )
            + int2ba(self.pdu_type.value[1], length=4, endian=endian, signed=False)
        )

    def __repr__(self) -> str:
        return (
            f"[{self.pdu_type.name}("
            + (
                ("HAS-EXT " if self.has_more_headers else "")
                + ("IS-ACK " if self.is_acknowledged else "")
                + ("IS-CONTROL-MSG " if self.is_control_message else "IS-USER-DATA ")
                + ("IS-RESERVED " if self.is_reserved else "")
            ).strip()
            + ")]"
        )


class AvailabilitySecondHeader(BytesInterface):
    def __init__(self, capability: TMSDeviceCapability):
        self.capability: TMSDeviceCapability = capability

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["AvailabilitySecondHeader"]:
        return AvailabilitySecondHeader(capability=TMSDeviceCapability(data[0] & 0b11))

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return int(self.capability.value).to_bytes(length=1, byteorder=endian)

    def __repr__(self) -> str:
        return f"[AvailabilitySecondHeader {self.capability}]"


class TextMessagingService(BytesInterface, LoggingTrait):
    """
    TMS (Text Messaging Service)
    | PDU len (2 bytes) | FirstHeader (1 byte) | Address len (1 byte) | Address (optional) | Optional headers | Payload |
    """

    def __init__(
        self,
        first_header: FirstHeader,
        address: bytes = b"",
        availability_header: Optional[AvailabilitySecondHeader] = None,
        sequence_number: Optional[int] = None,
        encoding: Optional[TMSEncoding] = None,
        message: Optional[bytes] = None,
    ) -> None:
        self.header: FirstHeader = first_header
        self.address: bytes = address
        self.availability_header: Optional[
            AvailabilitySecondHeader
        ] = availability_header
        self.sequence_number: Optional[int] = sequence_number
        self.encoding: Optional[TMSEncoding] = encoding
        self.message: Optional[bytes] = message

    @staticmethod
    def decode_sn_and_encoding(
        data: bytes, start_idx: int
    ) -> Tuple[int, int, Optional[TMSEncoding]]:
        """
        Returns (new_idx, sequence number, encoding)
        @param data:
        @param start_idx: start decoding at index(start_idx) in data bytes
        @return:
        """
        encoding: Optional[TMSEncoding] = None
        idx: int = start_idx

        # first optional header byte
        # has_more_headers | 2 bits reserved | 5 LSB bits of s/n
        sequence_number = data[idx] & 0b0001_1111
        idx += 1
        # check just the "has_more_headers" bit
        if data[idx - 1] & 0b1000_0000:
            # second optional header byte
            # has_more_headers | 2 MSB bits of s/n | 5 bits reserved
            # masks stack on top of each other
            # 0b0001_1111 (last 5 bits)
            # 0b0110_0000 (2nd and 3rd bit)
            # 0b0111_1111 (merged masks)
            sequence_number |= data[idx] & 0b0110_0000
            encoding = TMSEncoding(data[idx] & 0b0001_1111)
            encoding = None if encoding == TMSEncoding.UNDEFINED else encoding
            idx += 1

        return idx, sequence_number, encoding

    def encode_sn_and_encoding(self, endian: Literal["big", "little"] = "big") -> bytes:
        has_encoding: bool = bool(
            self.encoding and self.encoding != TMSEncoding.UNDEFINED
        )
        has_two_bytes: bool = (self.sequence_number > 0b11111) or has_encoding
        bits: bitarray = bitarray(endian=endian)
        # [+] 1st byte
        # has_more_headers
        bits += [has_two_bytes]
        # 2 bits reserved
        bits += [0, 0]
        # 5 lsb bits of s/n
        sn_bits: bitarray = int2ba(
            self.sequence_number, length=7, signed=False, endian=endian
        )
        bits += sn_bits[2:]
        # [+] 2nd byte
        if has_two_bytes:
            # has_more_headers
            bits += [0]
            # 2 msb bits of s/n
            bits += sn_bits[0:2]
            # optionally encoding
            bits += (
                int2ba(self.encoding.value, length=5, signed=False, endian=endian)
                if has_encoding
                else [0, 0, 0, 0, 0]
            )
        return bits_to_bytes(bits)

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["TextMessagingService"]:
        msg_len: int = int.from_bytes(data[0:2], byteorder=endian)
        assert (
            len(data) >= msg_len
        ), f"TMS PDU not enough data, expected at least {msg_len} bytes, got {len(data)} bytes"
        first_header: FirstHeader = FirstHeader.from_bytes(data[2:3], endian=endian)
        addr_len: int = int.from_bytes(data[3:4], byteorder=endian)
        idx: int = 4 + addr_len
        address: bytes = data[4:idx]
        if first_header.pdu_type == TMSPDUType.SERVICE_AVAILABILITY:
            # read second header, if present
            availability_header: Optional[AvailabilitySecondHeader] = None
            if first_header.has_more_headers:
                availability_header = AvailabilitySecondHeader.from_bytes(
                    data[idx : idx + 1]
                )
                idx += 1

            return TextMessagingService(
                first_header=first_header,
                address=address,
                availability_header=availability_header,
            )
        elif first_header.pdu_type == TMSPDUType.TMS_ACKNOWLEDGEMENT:
            # s/n is sequence number of text message being confirmed by this PDU
            sequence_number: Optional[int] = None
            if first_header.has_more_headers:
                (idx, sequence_number, _) = TextMessagingService.decode_sn_and_encoding(
                    data, idx
                )

            return TextMessagingService(
                first_header=first_header,
                address=address,
                sequence_number=sequence_number,
            )
        elif first_header.pdu_type == TMSPDUType.SIMPLE_TEXT_MESSAGE:
            sequence_number: Optional[int] = None
            encoding: Optional[TMSEncoding] = None
            if first_header.has_more_headers:
                (
                    idx,
                    sequence_number,
                    encoding,
                ) = TextMessagingService.decode_sn_and_encoding(data, idx)
            return TextMessagingService(
                first_header=first_header,
                address=address,
                sequence_number=sequence_number,
                encoding=encoding,
                message=data[idx : msg_len + 2],
            )

    def encode_address_field(self) -> bytes:
        return bytes([len(self.address)]) + self.address

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        has_more_headers: bool = False
        data: bytes = self.encode_address_field()
        """
        | PDU len (2 bytes) | FirstHeader (1 byte) | Address len (1 byte) | Address (optional) | Optional headers | Payload |
        """
        if self.header.pdu_type == TMSPDUType.SERVICE_AVAILABILITY:
            if self.availability_header:
                has_more_headers = True
                data += self.availability_header.as_bytes(endian=endian)
            # NO PAYLOAD
        elif self.header.pdu_type == TMSPDUType.SIMPLE_TEXT_MESSAGE:
            has_more_headers = True
            data += self.encode_sn_and_encoding(endian=endian)
            data += self.message
        elif self.header.pdu_type == TMSPDUType.TMS_ACKNOWLEDGEMENT:
            if self.sequence_number or self.encoding:
                has_more_headers = True
                data += self.encode_sn_and_encoding(endian=endian)
            # NO PAYLOAD

        return (
            (len(data) + 1).to_bytes(length=2, byteorder=endian)
            + self.header.set_has_more_headers(has_more_headers).as_bytes(endian=endian)
            + data
        )

    def __repr__(self) -> str:
        repre: str = "[TMS] "
        if self.header:
            repre += f"{repr(self.header)} "
            if (
                self.header.pdu_type == TMSPDUType.SERVICE_AVAILABILITY
                and self.availability_header
            ):
                repre += f"{repr(self.availability_header)} "
        if self.sequence_number:
            repre += f"[S/N: {self.sequence_number}] "
        if self.address:
            repre += f"[ADDRESS: {self.address}] "
        if self.encoding and self.encoding != TMSEncoding.UNDEFINED:
            repre += f"[ENCODING: {self.encoding.name}]"
        if self.message and len(self.message) > 0:
            repre += f"[MESSAGE: {self.message}]"

        return repre
