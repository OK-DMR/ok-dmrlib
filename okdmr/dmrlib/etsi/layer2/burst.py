from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits, bits_to_bytes


class Burst:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 4.2.2   Burst and frame structure
    """

    def __init__(self, full_burst: bytes):
        assert len(full_burst) == 33, "DMR Layer2 burst must be 33 bytes (264 bits)"
        self.full_bytes: bytes = full_burst
        self.full_bits: bitarray = bytes_to_bits(self.full_bytes)
        self.sync_or_embedded: SyncPatterns = SyncPatterns.resolve_bytes(
            bits_to_bytes(self.full_bits[108:156])
        )
