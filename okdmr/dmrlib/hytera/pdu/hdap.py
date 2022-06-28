import enum
from typing import Union, Optional

from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


@enum.unique
class HyteraServiceType(enum.Enum):
    RRS = 0x11
    LP = 0x08
    TMP = 0x09
    RCP = 0x02
    TP = 0x12
    DTP = 0x13
    DDS = 0x14


class HDAP(BytesInterface, LoggingTrait):
    """
    All HDAP protocols (services) PDUs follow this pattern

    | ServiceType (byte) | Opcode (2 bytes) | Number of bytes in payload (2 bytes) | Payload (n bytes)
    | Checksum (1 byte) | MsgEnd (1 byte) |

    """

    def __init__(
        self,
        pdu_type: HyteraServiceType,
        is_reliable: bool = False,
        payload: Optional[Union["HDAP", bytes]] = None,
        checksum: Union[bytes, int] = 0,
        msg_end: bytes = b"\x03",
    ):
        """

        :param pdu_type:
        :param payload:
        :param checksum:
        :param msg_end:
        """
        self.pdu_type: HyteraServiceType = pdu_type
        self.is_reliable: bool = is_reliable
        self.checksum: bytes = (
            checksum
            if isinstance(checksum, bytes)
            else checksum.to_bytes(length=1, byteorder="big")
        )
        self.payload: Optional[HDAP] = (
            payload
            if (payload is None or isinstance(payload, HDAP))
            else HDAP.from_bytes(payload)
        )
        self.msg_end: bytes = msg_end

    def __len__(self) -> int:
        return 12 + (len(self.payload) if self.payload else 0)

    @staticmethod
    def from_bytes(data: bytes) -> Optional["HDAP"]:
        if len(data) == 0:
            return None
        # prevent circular imports
        from okdmr.dmrlib.hytera.pdu.location_protocol import LocationProtocol
        from okdmr.dmrlib.hytera.pdu.radio_control_protocol import RadioControlProtocol

        assert len(data) >= 1
        service = HyteraServiceType(data[0])
        return {
            HyteraServiceType.LP: lambda x: LocationProtocol.from_bytes(x),
            HyteraServiceType.RCP: lambda x: RadioControlProtocol.from_bytes(x),
        }[service](data)

    def get_checksum(self, provided_checksum: Union[bytes, int]) -> int:
        return 0

    # noinspection PyMethodMayBeStatic
    def get_opcode(self) -> bytes:
        """
        Get 2-byte opcode of inner
        :return:
        """
        return b"\x00\x00"
