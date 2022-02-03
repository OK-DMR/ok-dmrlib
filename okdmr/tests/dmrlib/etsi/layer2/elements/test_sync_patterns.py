from unittest import TestCase

from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns


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


class SyncPatternsTestCase(TestCase):
    def test_validates_sync_length(self):
        self.assertRaises(AssertionError, SyncPatterns.resolve_bytes, [b""])
        self.assertRaises(AssertionError, SyncPatterns.resolve_bytes, [b"\x00"])
        self.assertRaises(
            AssertionError,
            SyncPatterns.resolve_bytes,
            [b"\x00\x00\x00\x00\x00\x00\x00"],
        )
