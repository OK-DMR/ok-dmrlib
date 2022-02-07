from typing import Union

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


class ServiceOptions(BitsInterface):
    """
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.2.1  Service Options
    """

    def __init__(
        self,
        is_emergency: Union[bool, int],
        is_broadcast: Union[bool, int],
        is_open_voice_call_mode: Union[bool, int],
        priority_level: int,
    ):
        assert (
            0b00 <= priority_level <= 0b11
        ), f"Priority level is out of range, got {priority_level}"
        self.is_emergency: bool = is_emergency in (True, 1)
        self.is_broadcast: bool = is_broadcast in (True, 1)
        self.is_open_voice_call_mode: bool = is_open_voice_call_mode in (True, 1)
        self.priority_level: int = priority_level

    @staticmethod
    def from_bits(bits: bitarray) -> "ServiceOptions":
        assert len(bits) == 8, f"ServiceOptions is 8-bit field, got {len(bits)} bits"
        return ServiceOptions(
            is_emergency=bits[0],
            is_broadcast=bits[4],
            is_open_voice_call_mode=bits[5],
            priority_level=ba2int(bits[6:8]),
        )

    def as_bits(self) -> bitarray:
        return bitarray(
            [
                self.is_emergency,
                False,
                False,
                False,
                self.is_broadcast,
                self.is_open_voice_call_mode,
            ]
        ) + int2ba(self.priority_level, length=2)
