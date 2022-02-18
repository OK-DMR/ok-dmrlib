from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes


class HyteraIPSCSync(Burst):
    def __init__(
        self, full_bits: bitarray, burst_type: BurstTypes = BurstTypes.Undefined
    ):
        """
        Hytera IPSC sync packet is different, not dmr data,
        it does not contain EMB or SLOT PDUs, ending might be some RCP / HRNP / HDAP or different hytera-specific protocol

        example payload:    0000 0000 0000 [0000 0000 006f] [0023 0037 00fa] 2a34 102c 2a94 102c 2af4 102c 2e01 4f83

        contains 16-bit fields
        [00 00]
        [00 00]
        [00 00]

        [00 00] \
        [00 00]  =>  these 3 identify source radio/repeater, (16)[00006F] == (10)[111]
        [00 6F] /

        [00 23] \
        [00 37]  =>  these 3 identify destination radio/repeater, (16)[2337FA] == (10)[2308090]
        [00 FA] /

        """
        super().__init__(full_bits, burst_type)
        self.has_emb = False
        self.has_slot_type = False
        self.source: int = ba2int(
            full_bits[56:64] + full_bits[72:80] + full_bits[88:96]
        )
        self.target: int = ba2int(
            full_bits[104:112] + full_bits[120:128] + full_bits[136:144]
        )

    @staticmethod
    def deinterleave(bits: bitarray, data_type: DataTypes) -> bitarray:
        # IPSC Sync is not interleaved
        return bits

    def as_bits(self) -> bitarray:
        return self.full_bits

    def __repr__(self):
        return f"[IPSC SYNC] [SOURCE: {self.source}] [TARGET: {self.target}]"

    @staticmethod
    def from_bits(bits: bitarray, burst_type: BurstTypes) -> "HyteraIPSCSync":
        return HyteraIPSCSync(full_bits=bits, burst_type=burst_type)
