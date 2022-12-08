import enum
from typing import Optional, Tuple, List, Literal

from bitarray import bitarray

from okdmr.dmrlib.hytera.pdu.hdap import HDAP
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits
from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HSTRPPacketType(BytesInterface):
    """
    Represents single byte that indicate contents of HSTRP PDU
    """

    def __init__(
        self,
        have_options: bool = False,
        is_reject: bool = False,
        is_close: bool = False,
        is_connect: bool = False,
        is_heartbeat: bool = False,
        is_ack: bool = False,
    ):
        self.have_options: bool = have_options
        self.is_reject: bool = is_reject
        self.is_close: bool = is_close
        self.is_connect: bool = is_connect
        self.is_heartbeat: bool = is_heartbeat
        self.is_ack: bool = is_ack

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["HSTRPPacketType"]:
        assert len(data) > 0, f"HSTRP Option Byte needs at least one byte"
        bits = bytes_to_bits(data[0:1])
        return HSTRPPacketType(
            have_options=bits[2] == 1,
            is_reject=bits[3] == 1,
            is_close=bits[4] == 1,
            is_connect=bits[5] == 1,
            is_heartbeat=bits[6] == 1,
            is_ack=bits[7] == 1,
        )

    def __repr__(self) -> str:
        return (
            "HSTRPPacketType "
            + ("HAVE_OPTIONS " if self.have_options else "")
            + ("IS_REJECT " if self.is_reject else "")
            + ("IS_CLOSE " if self.is_close else "")
            + ("IS_CONNECT " if self.is_connect else "")
            + ("IS_HEARTBEAT " if self.is_heartbeat else "")
            + ("IS_ACK " if self.is_ack else "")
        ).strip()

    @property
    def has_options(self):
        return not self.is_heartbeat and self.have_options

    @property
    def has_data(self):
        return self.have_options or self.is_ack

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bitarray(
            [
                False,
                False,
                self.have_options,
                self.is_reject,
                self.is_close,
                self.is_connect,
                self.is_heartbeat,
                self.is_ack,
            ]
        ).tobytes()


@enum.unique
class HSTRPOptionType(enum.Enum):
    RTP = 1
    DeviceID = 3
    ChannelID = 4
    XPTSiteID = 5
    XPTIndex = 6
    XPTChannelType = 7


class HSTRPOptions(BytesInterface):
    """
    | Command | Value | Description | Length (bytes)  | Option's Payload  |
    | ------------------------------------------------------------------- |
    | Realtime | 1 | setup/teardown RTP connection   | 0 | NULL           |
    | Device ID | 3 |  device/radio/repeater id      | 4 | Repeater ID    |
    | Channel ID | 4 | channel path                  | 1 | Slot ID        |
    | XPT site ID | 5 | identifier of XPT site       | 1 | XPT Site ID    |
    | XPT Index | 6 | index number of each repeater  | 1 | repeater index |
    | XPT Channel Type | 7 | 0=voice, 1=data channel | 1 | channel type   |
    | ------------------------------------------------------------------- |
    """

    def __init__(self):
        self.options: List[Tuple[HSTRPOptionType, bytes]] = []

    def add_option(self, command: HSTRPOptionType, data: bytes) -> "HSTRPOptions":
        self.options.append((command, data))
        return self

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        options_count: int = len(self.options)
        current_option: int = 0
        rtn = b""
        for (command, data) in self.options:
            is_last: bool = current_option == (options_count - 1)
            current_option += 1

            rtn += (
                bytes([command.value | (0x80 if not is_last else 0x00), len(data)])
                + data
            )
        return rtn

    def __len__(self) -> int:
        length: int = 0
        for (command, data) in self.options:
            length += 2 + len(data)
        return length

    def __repr__(self) -> str:
        r: str = ""
        for (command, data) in self.options:
            r += f"[{command}: {int.from_bytes(data, byteorder='big') if command != HSTRPOptionType.RTP else ''}] "
        return r

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> "HSTRPOptions":
        options = HSTRPOptions()
        has_next: bool = len(data) > 0
        idx: int = 0

        while has_next:
            # msb bit
            has_next = data[idx] & 0x80 == 0x80
            # following 7 bits
            command = HSTRPOptionType(data[idx] & 0x7F)
            option_len = data[idx + 1]
            # extract single option
            options.add_option(
                command=command, data=data[idx + 2 : idx + 2 + option_len]
            )
            # set next option index
            idx += 2 + option_len

        return options


class HSTRP(LoggingTrait, BytesInterface):
    """
    Big-endian protocol, only to make communication with repeaters reliable

    Assembly:

    | Header (2 bytes) - "2B" or [0x32 0x42]
    | Version (1 byte) - currently 0x00
    | Type (1 byte)
        - configuration in bits in this order
            (reserved, reserved, option, reject, close, connect, heartbeat, ack )
        - if type="option" (bit "option" is set), payload should be RRS, TMS or other payload
        - if type="ack", payload is filled with service messages
        - other bits should not carry payload
    | SN - Sequence number (1 byte)
        - usually from 0x01 to 0xFF incrementing with each message sent
        - for ACK SN should match the SN of message being confirmed
        - for heartbeat, close, reject and connect SN should be 0x00
    | Option (n bytes)
        - can carry multiple options
        - single option structure:
                | 1 bit - another option follows this one |
                | 7 bits - command identifier |
                | 8 bits - length of command payload in "bytes" |
                | n bits - indicated command payload |
    | Application payload (n bytes) - per type indication
    """

    HEADER: bytes = b"2B"

    def __init__(
        self,
        pkt_type: HSTRPPacketType,
        sn: int,
        options: Optional[HSTRPOptions] = None,
        payload: Optional[HDAP] = None,
        version: int = 0x00,
    ):
        self.pkt_type: HSTRPPacketType = pkt_type
        self.sn: int = sn
        self.options: Optional[HSTRPOptions] = options
        self.payload: Optional[HDAP] = payload
        self.version: int = version

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["HSTRP"]:
        if len(data) < 6:
            # minimum of 6 bytes in general is required for HSTRP PDU
            return None
        assert (
            data[0:2] == HSTRP.HEADER
        ), f"HSTRP packet got wrong prefix, expected b'2B' got {data[0:2]}"

        pkt_type: HSTRPPacketType = HSTRPPacketType.from_bytes(data[3:4])
        options = (
            HSTRPOptions.from_bytes(data[6:])
            if pkt_type.has_options
            else HSTRPOptions()
        )
        # payload might be there even if the options is_option=False
        payload = (
            HDAP.from_bytes(data[6 + len(options) :])
            if pkt_type.has_data or len(data) > 6 + len(options)
            else None
        )

        return HSTRP(
            version=data[2],
            pkt_type=pkt_type,
            sn=int.from_bytes(data[4:6], byteorder="big"),
            options=options,
            payload=payload,
        )

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return (
            HSTRP.HEADER
            + self.version.to_bytes(length=1, byteorder="big")
            + self.pkt_type.as_bytes()
            + self.sn.to_bytes(length=2, byteorder="big")
            + (
                self.options.as_bytes()
                if isinstance(self.options, HSTRPOptions)
                else b""
            )
            + (
                self.payload.as_bytes()
                if isinstance(self.payload, BytesInterface)
                else b""
            )
        )

    def __repr__(self) -> str:
        label = f"[{self.pkt_type}] [S/N: {self.sn}]"
        if isinstance(self.options, HSTRPOptions) and len(self.options.options) > 0:
            label += "\n\tOPTIONS: " + repr(self.options)
        if isinstance(self.payload, BytesInterface):
            label += "\n\tPAYLOAD: " + repr(self.payload)
        return label
