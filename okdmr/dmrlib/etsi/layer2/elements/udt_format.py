import enum

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class UDTFormat(BitsInterface, enum.Enum):
    Binary = 0b0000
    AddressMSorTG = 0b0001
    BCD4bit = 0b0010
    ISO7bit = 0b0011
    ISO8bit = 0b0100
    LocationNMEA = 0b0101
    AddressIP = 0b0110
    Unicode16bit = 0b0111

    ManufacturerSpecific = 0b1000

    Mixed = 0b1010

    Reserved = 0b1111

    @classmethod
    def _missing_(cls, value: int) -> "UDTFormat":
        if value in (0b1000, 0b1001):
            return UDTFormat.ManufacturerSpecific
        # undefined values are reserved by specification
        return UDTFormat.Reserved

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)

    @staticmethod
    def from_bits(bits: bitarray) -> "UDTFormat":
        return UDTFormat(ba2int(bits[0:4]))
