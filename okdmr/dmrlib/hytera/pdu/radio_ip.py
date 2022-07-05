from typing import Optional, Union

from okdmr.dmrlib.utils.bytes_interface import BytesInterface


class RadioIP(BytesInterface):
    """
    Simple wrapper around RadioID/RadioIP fields, Hytera uses similar to Motorola Subnet and ID,
    Hytera limits subnet to single byte (first IP octet)
    """

    def __init__(
        self,
        radio_id: Union[int, bytes],
        subnet: int = 0x0A,
    ):
        self.subnet: int = subnet
        self.radio_id: int = (
            radio_id
            if isinstance(radio_id, int)
            else int.from_bytes(radio_id, byteorder="big")
        )

    @staticmethod
    def from_bytes(data: bytes) -> Optional["RadioIP"]:
        assert len(data) >= 4, f"4 bytes required to construct RadioIP"
        return RadioIP(subnet=data[0], radio_id=data[1:4])

    def as_bytes(self) -> bytes:
        return bytes([self.subnet]) + self.radio_id.to_bytes(length=3, byteorder="big")

    def __str__(self):
        return f"{self.subnet}.{self.radio_id}"

    def __repr__(self):
        return f"[RadioIP subnet:{self.subnet} id:{self.radio_id}]"
