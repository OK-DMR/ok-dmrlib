from typing import Union

from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from okdmr.dmrlib.etsi.crc.crc16 import CRC16
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks

from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class PIHeader(BitsInterface):
    def __init__(self, data: bytes, crc: Union[int, bytes] = 0):
        self.data: bytes = data
        self.crc: int = self.calculate_crc()
        self.crc_ok: bool = self.crc == (
            crc if isinstance(crc, int) else int.from_bytes(crc, byteorder="big")
        )

    def calculate_crc(self) -> int:
        return CRC16.calculate(data=self.data, mask=CrcMasks.PiHeader)

    def __repr__(self):
        return (
            f"[PI Header] [Data({len(self.data)}) {self.data.hex()} {bytes_to_bits(self.data)}]"
            + ("" if self.crc_ok else " [CRC16-CCIT INVALID]")
        )

    @staticmethod
    def from_bits(bits: bitarray) -> "PIHeader":
        return PIHeader(data=bits_to_bytes(bits[:-16]), crc=ba2int(bits[-16:]))

    def as_bits(self) -> bitarray:
        return bytes_to_bits(self.data) + int2ba(self.crc, length=16)
