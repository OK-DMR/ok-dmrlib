import enum
from typing import Optional, Literal

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

    MSG_END: bytes = b"\x03"

    def get_service_type(self) -> HyteraServiceType:
        """
        Message Header / ServiceType
        """

    def get_opcode(self) -> bytes:
        """
        Opcode (2-bytes)
        """

    def get_payload(self) -> bytes:
        """
        Payload (n-bytes)
        """

    @staticmethod
    def get_hdap_checksum(checked_data: bytes) -> bytes:
        """
        Get 1-byte checksum for opcode through payload fields
        """

        csum: int = 0
        for byteval in checked_data:
            csum = (csum + byteval) & 0xFF

        return bytes([((csum ^ 0xFF) + 0x33) & 0xFF])

    def get_endianness(self) -> Literal["big", "little"]:
        return "big"

    def as_bytes(self) -> bytes:
        payload = self.get_payload()
        checked_data = (
            self.get_opcode()
            + len(payload).to_bytes(length=2, byteorder=self.get_endianness())
            + payload
        )

        return (
            self.get_service_type().value.to_bytes(length=1, byteorder="big")
            + checked_data
            + HDAP.get_hdap_checksum(checked_data)
            + HDAP.MSG_END
        )

    def __len__(self):
        return 7 + len(self.get_payload())

    @staticmethod
    def from_bytes(data: bytes) -> Optional["HDAP"]:
        if len(data) < 1:
            return None
        opcode = HyteraServiceType(data[0])

        from okdmr.dmrlib.hytera.pdu.location_protocol import LocationProtocol
        from okdmr.dmrlib.hytera.pdu.radio_control_protocol import RadioControlProtocol

        return {
            HyteraServiceType.LP: LocationProtocol.from_bytes,
            HyteraServiceType.RCP: RadioControlProtocol.from_bytes,
        }[opcode](data)
