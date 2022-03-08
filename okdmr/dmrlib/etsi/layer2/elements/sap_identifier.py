import enum

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class SAPIdentifier(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.18 SAP identifier (SAP)
    """

    UDT = 0b0000
    TCP_IP_compression = 0b0010
    UDP_IP_compression = 0b0011
    IP_PacketData = 0b0100
    ARP = 0b0101
    Proprietary = 0b1001
    ShortData = 0b1010

    Reserved = 0b1111

    @classmethod
    def _missing_(cls, value: int) -> "SAPIdentifier":
        assert (
            0b0000 <= value <= 0b1111
        ), f"SAP Identifier value {value} is out-of-range"
        return SAPIdentifier.Reserved

    @staticmethod
    def from_bits(bits: bitarray) -> "SAPIdentifier":
        return SAPIdentifier(ba2int(bits[0:4]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)
