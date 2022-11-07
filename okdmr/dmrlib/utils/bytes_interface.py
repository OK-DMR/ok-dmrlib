from typing import Optional, Literal


class BytesInterface:
    """
    Interface for byte-based protocols, calling from_bytes() and then as_bytes() should yield the original data bytes
    """

    @staticmethod
    def from_bytes(
        data: bytes, endian: Literal["big", "little"] = "big"
    ) -> Optional["BytesInterface"]:
        """
        Deserialize from bytes, if no bytes provided or data cannot be deserialized on that interface, return None
        :param data:
        :param endian:
        :return:
        """
        pass

    def as_bytes(self, endian: Literal["big", "little"] = "big") -> bytes:
        """
        Serialize to bytes
        :param endian:
        :return:
        """
        pass
