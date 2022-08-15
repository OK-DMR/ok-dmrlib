import pytest

from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_sync_patterns():
    sync_data_str: str = "755FD7DF75F7"
    sync_data_bytes: bytes = bytes.fromhex(sync_data_str)

    # test that bytes and int enum resolution yields the same result
    assert SyncPatterns.resolve_bytes(sync_data_bytes) == SyncPatterns(
        int.from_bytes(sync_data_bytes, byteorder="big")
    )

    # byte sequence other than documented sync patterns should yield "embedded signalling" SyncPattern
    assert (
        SyncPatterns.resolve_bytes(b"\x00\x00\x00\x00\x00\x00")
        == SyncPatterns.EmbeddedSignalling
    )

    assert SyncPatterns.BsSourcedVoice == SyncPatterns.from_bits(
        bytes_to_bits(sync_data_bytes)
    )


class TestSyncPatterns:
    def test_validates_sync_length(self):
        with pytest.raises(AssertionError):
            SyncPatterns.resolve_bytes(b"")
        with pytest.raises(AssertionError):
            SyncPatterns.resolve_bytes(b"\x00")
        with pytest.raises(AssertionError):
            SyncPatterns.resolve_bytes(b"\x00\x00\x00\x00\x00\x00\x00")
