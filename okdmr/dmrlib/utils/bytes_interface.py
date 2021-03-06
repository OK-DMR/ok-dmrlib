from typing import Optional


class BytesInterface:
    """
    Interface for byte-based protocols, calling from_bytes() and then as_bytes() should yield the original data bytes
    """

    @staticmethod
    def from_bytes(data: bytes) -> Optional["BytesInterface"]:
        """
        Deserialize from bytes, if no bytes provided or data cannot be deserialized on that interface, return None
        :param data:
        :return:
        """
        pass

    def as_bytes(self) -> bytes:
        """
        Serialize to bytes
        :return:
        """
        pass
