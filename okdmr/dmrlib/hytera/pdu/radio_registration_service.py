import enum
from typing import Optional

from okdmr.dmrlib.hytera.pdu.hdap import HDAP, HyteraServiceType


@enum.unique
class RRSTypes(enum.Enum):
    Registration = 0x03
    RegistrationAck = 0x80
    DeRegistration = 0x01
    OnLineCheck = 0x02
    OnLineCheckACk = 0x82


class RadioRegistrationService(HDAP):
    """
    RRS - Radio Registration Service
    """

    def __init__(
        self, opcode: RRSTypes, is_reliable: bool = False, radio_ip: bytes = b""
    ):
        super().__init__(is_reliable=is_reliable)
        self.opcode: RRSTypes = opcode
        self.radio_ip: bytes = radio_ip

    def get_opcode(self) -> bytes:
        return bytes([0x00, self.opcode.value])

    def get_service_type(self) -> HyteraServiceType:
        return HyteraServiceType.RRS

    def get_payload(self) -> bytes:
        if self.opcode == RRSTypes.Registration:
            return self.radio_ip
        raise NotImplementedError(f"{self.opcode} not yet implemented")

    @staticmethod
    def from_bytes(data: bytes) -> Optional["RadioRegistrationService"]:
        (is_reliable, service_type) = HDAP.get_reliable_and_service(data[0:1])
        assert service_type == HyteraServiceType.RRS, f"Expected RRS got {service_type}"
        return RadioRegistrationService(
            is_reliable=is_reliable, opcode=RRSTypes(data[2]), radio_ip=data[5:9]
        )
