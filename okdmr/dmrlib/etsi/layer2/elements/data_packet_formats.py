import enum

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class DataPacketFormats(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.17 Data Packet Format (DPF)
    """

    UnifiedDataTransport = 0b0000
    ResponsePacket = 0b0001
    DataPacketUnconfirmed = 0b0010
    DataPacketConfirmed = 0b0011
    Reserved = 0b1100
    ShortDataDefined = 0b1101
    ShortDataRawOrStatusPrecoded = 0b1110
    ProprietaryDataPacket = 0b1111

    @classmethod
    def _missing_(cls, value: int) -> "DataPacketFormats":
        assert (
            0b0000 <= value <= 0b1111
        ), f"DPF (Data Packet Format) out of range, got {value}"
        # undefined values are reserved per specification
        return DataPacketFormats.Reserved

    @staticmethod
    def from_bits(bits: bitarray) -> "DataPacketFormats":
        return DataPacketFormats(ba2int(bits[0:4]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)
