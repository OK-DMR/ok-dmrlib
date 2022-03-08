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
        is_emergency: Union[bool, int] = False,
        is_broadcast: Union[bool, int] = False,
        is_open_voice_call_mode: Union[bool, int] = False,
        priority_level: int = 0,
        is_privacy: Union[bool, int] = False,
        reserved: bitarray = bitarray("00"),
    ):
        assert (
            0b00 <= priority_level <= 0b11
        ), f"Priority level is out of range, got {priority_level}"
        self.is_emergency: bool = is_emergency in (True, 1)
        self.is_broadcast: bool = is_broadcast in (True, 1)
        self.is_privacy: bool = is_privacy in (True, 1)
        self.is_open_voice_call_mode: bool = is_open_voice_call_mode in (True, 1)
        self.priority_level: int = priority_level
        self.reserved: bitarray = reserved[0:2]

    def __repr__(self) -> str:
        return (
            "[SERVICE_OPTIONS: "
            + ("EMERGENCY " if self.is_emergency else "")
            + ("BROADCAST " if self.is_broadcast else "")
            + ("OVCM " if self.is_open_voice_call_mode else "")
            + ("PRIVACY " if self.is_privacy else "")
            + f"PRIORITY:{self.priority_level}]"
        )

    @staticmethod
    def from_bits(bits: bitarray) -> "ServiceOptions":
        assert len(bits) == 8, f"ServiceOptions is 8-bit field, got {len(bits)} bits"
        return ServiceOptions(
            is_emergency=bits[0],
            is_privacy=bits[1],
            reserved=bits[2:4],
            is_broadcast=bits[4],
            is_open_voice_call_mode=bits[5],
            priority_level=ba2int(bits[6:8]),
        )

    def as_bits(self) -> bitarray:
        return bitarray(
            [
                self.is_emergency,
                self.is_privacy,
                self.reserved[0],
                self.reserved[1],
                self.is_broadcast,
                self.is_open_voice_call_mode,
            ]
        ) + int2ba(self.priority_level, length=2)
