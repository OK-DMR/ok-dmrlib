from unittest import TestCase

from okdmr.dmrlib.etsi.layer2.sync_patterns import SyncPattern


def test_sync_patterns():
    sync_data_str: str = "755FD7DF75F7"
    sync_data_bytes: bytes = bytes.fromhex(sync_data_str)

    # test that bytes and int enum resolution yields the same result
    assert SyncPattern.resolve_bytes(sync_data_bytes) == SyncPattern(
        int.from_bytes(sync_data_bytes, byteorder="big")
    )

    assert (
        SyncPattern.resolve_bytes(b"\x00\x00\x00\x00\x00\x00")
        == SyncPattern.EmbeddedSignalling
    )


class SyncPatternsTestCase(TestCase):
    def test_validates_sync_length(self):
        self.assertRaises(AssertionError, SyncPattern.resolve_bytes, [b""])
        self.assertRaises(AssertionError, SyncPattern.resolve_bytes, [b"\x00"])
        self.assertRaises(
            AssertionError, SyncPattern.resolve_bytes, [b"\x00\x00\x00\x00\x00\x00\x00"]
        )
