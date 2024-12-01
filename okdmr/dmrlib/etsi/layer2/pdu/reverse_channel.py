from typing import Union, Literal, Optional

from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from okdmr.dmrlib.etsi.crc.crc7 import CRC7
from okdmr.dmrlib.etsi.fec.vbptc_32_11 import VBPTC3211
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks

from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface
from okdmr.dmrlib.utils.bytes_interface import BytesInterface
from okdmr.dmrlib.etsi.layer3.elements.reverse_channel_command import (
    ReverseChannelCommand,
)


class ReverseChannel(BitsInterface, BytesInterface):
    def __init__(
        self,
        rc_command: ReverseChannelCommand = ReverseChannelCommand.SetPowerToHighest,
        crc7: Union[int, bytes] = 0,
    ):
        self.rc_command: ReverseChannelCommand = rc_command
        self.crc: int = self.calculate_crc()
        self.crc_ok: bool = self.crc == (
            crc7 if isinstance(crc7, int) else int.from_bytes(crc7, byteorder="big")
        )

    def calculate_crc(self) -> int:
        return CRC7.calculate(
            data=self.rc_command.as_bits(), mask=CrcMasks.ReverseChannel
        )

    def __repr__(self) -> str:
        return f"[ReverseChannel {self.rc_command}]" + (
            "" if self.crc_ok else " [CRC7 INVALID]"
        )

    @staticmethod
    def deinterleave(bits: bitarray) -> bitarray:
        return VBPTC3211.deinterleave_data_bits(bits)

    @staticmethod
    def from_bits(bits: bitarray) -> "ReverseChannel":
        # from_bits => from on-air bits, means from interleaved form
        assert len(bits) in (
            32,
            11,
            4,
        ), f"not 32 (full on-air pdu), 11 (rc command + crc7) or 4 (rc command), got {len(bits)}"
        deinterleaved: bitarray = (
            ReverseChannel.deinterleave(bits)
            if len(bits) == 32
            else (bits if len(bits) == 11 else (bits + bitarray("0000000")))
        )
        return ReverseChannel(
            rc_command=ReverseChannelCommand.from_bits(deinterleaved[0:4]),
            crc7=ba2int(deinterleaved[4:11]),
        )

    def encode(self) -> bitarray:
        """
        Returns: 32 bits of interleaved data+crc7
        """
        return VBPTC3211.encode(
            (self.rc_command.as_bits() + int2ba(self.calculate_crc(), 7)), False
        )

    def as_bits(self) -> bitarray:
        return self.encode()

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["BytesInterface"]:
        return ReverseChannel.from_bits(bytes_to_bits(data))

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        return bits_to_bytes(self.encode())
