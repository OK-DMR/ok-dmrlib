import enum

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class UDPPortIdentifier(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-3 V1.3.1 (2017-10) -
        7.2.4.3 - UDP Source Port IDentifier (SPID)
        7.2.4.4 - UDP Destination Port IDentifier (DPID)
    """

    InExtendedHeader = 0b0000000
    UTF16BE_TextMessage = 0b00000001
    LocationInterfaceProtocol = 0b0000010
    Reserved = 0b0000011
    ManufacturerSpecific = 0b1011111

    @classmethod
    def _missing_(cls, value: int) -> "UDPPortIdentifier":
        assert (
            value <= 0b1111111
        ), f"UDP Source/Destination Port Identifier out of range, got {value}"
        if (
            UDPPortIdentifier.Reserved.value
            <= value
            < UDPPortIdentifier.ManufacturerSpecific.value
        ):
            return UDPPortIdentifier.Reserved
        elif UDPPortIdentifier.ManufacturerSpecific.value <= value <= 0b1111111:
            return UDPPortIdentifier.ManufacturerSpecific

    @staticmethod
    def from_bits(bits: bitarray) -> "UDPPortIdentifier":
        assert (
            len(bits) >= 7
        ), f"UDP Port Identifier requires at least 7 bits, got {len(bits)} :: {bits}"
        return UDPPortIdentifier(ba2int(bits[:7]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=7)
