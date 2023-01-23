import socket
from typing import Optional, Union, Literal

from okdmr.dmrlib.utils.bytes_interface import BytesInterface


class RadioIP(BytesInterface):
    """
    Simple wrapper around RadioID/RadioIP fields, Hytera uses similar to Motorola Subnet and ID,
    Hytera limits subnet to single byte (first IP octet)
    """

    def __init__(self, radio_id: Union[int, bytes], subnet: int = 0x0A):
        """

        @param radio_id:
        @param subnet: 0x0A is "10" as in IP "10.0.0.1"
        """
        self.subnet: int = subnet
        self.radio_id: int = (
            radio_id
            if isinstance(radio_id, int)
            else int.from_bytes(radio_id, byteorder="big")
        )

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["RadioIP"]:
        assert (
            len(data) == 4
        ), f"4 bytes required to construct RadioIP, got {len(data)} :: {data.hex()}"
        if endian == "little":
            data = data[::-1]
        return RadioIP(subnet=data[0], radio_id=data[1:4])

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        raw: bytes = bytes([self.subnet]) + self.radio_id.to_bytes(
            length=3, byteorder="big"
        )
        return raw if endian == "big" else raw[::-1]

    def as_ip(self) -> str:
        return str(self)

    @staticmethod
    def from_ip(ip: str, endian: Literal["big", "little"] = "big") -> "RadioIP":
        return RadioIP.from_bytes(data=socket.inet_aton(ip), endian=endian)

    def __str__(self):
        return socket.inet_ntoa(
            bytes([self.subnet]) + self.radio_id.to_bytes(length=3, byteorder="big")
        )

    def __repr__(self):
        return f"[RadioIP subnet:{self.subnet} id:{self.radio_id}]"
