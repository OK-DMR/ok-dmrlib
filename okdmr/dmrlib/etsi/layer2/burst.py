from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.sync_patterns import SyncPattern
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits, bits_to_bytes


class Burst:
    def __init__(self, full_burst: bytes):
        assert len(full_burst) == 33, "DMR Layer2 burst must be 33 bytes (264 bits)"
        self.full_bytes: bytes = full_burst
        self.full_bits: bitarray = bytes_to_bits(self.full_bytes)
        self.sync_or_embedded: SyncPattern = SyncPattern.resolve_bytes(
            bits_to_bytes(self.full_bits[108 : 108 + 48])
        )
