from okdmr.dmrlib.etsi.layer2.elements.sync_types import SyncTypes


def test_sync_types_embedded_or_missing():
    assert SyncTypes(0x1337) == SyncTypes.EmbeddedData
