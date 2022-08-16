import enum

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class IPAddressIdentifier(BitsInterface, enum.Enum):
    RadioNetwork = 0b0000
    USBEthernetInterfaceNetwork = 0b0001
    Reserved = 0b0010
    ManufacturerSpecific = 0b1100

    @classmethod
    def _missing_(cls, value: int) -> "IPAddressIdentifier":
        assert (
            value <= 0b1111
        ), f"IP Source/Destination Address Identifier out of range, got {value}"
        if (
            IPAddressIdentifier.Reserved.value
            <= value
            < IPAddressIdentifier.ManufacturerSpecific.value
        ):
            return IPAddressIdentifier.Reserved
        elif IPAddressIdentifier.ManufacturerSpecific.value <= value:
            return IPAddressIdentifier.ManufacturerSpecific

    @staticmethod
    def from_bits(bits: bitarray) -> "IPAddressIdentifier":
        assert len(bits) >= 4, f"IP Address Identifier requires at least 4 bits"
        return IPAddressIdentifier(ba2int(bits[0:4]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)
