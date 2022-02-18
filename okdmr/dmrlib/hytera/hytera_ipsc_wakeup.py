from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes


class HyteraIPSCWakeup(Burst):
    def __init__(
        self, full_bits: bitarray, burst_type: BurstTypes = BurstTypes.Undefined
    ):
        """
        Hytera IPSC wakeup does not contain EMB, SLOT or standard ETSI DMR Data

        example payload:    5a5a5a5a0000000042000501020000002222dddd555500004000000000000000000000000000020002000000000000000000000000000000b2dd503250380c00000014000000ff01
                            5a5a5a5a0000000042000501020000002222dddd555500004000000000000000000000000100020002000100000000000000000000000000ffffef082a00000000000000fb372300


        """
        super().__init__(full_bits, burst_type)
        self.has_emb = False
        self.has_slot_type = False

    @staticmethod
    def deinterleave(bits: bitarray, data_type: DataTypes) -> bitarray:
        # IPSC Sync is not interleaved
        return bits

    def as_bits(self) -> bitarray:
        return self.full_bits

    def __repr__(self):
        return f"[IPSC WAKEUP]"

    @staticmethod
    def from_bits(bits: bitarray, burst_type: BurstTypes) -> "HyteraIPSCWakeup":
        return HyteraIPSCWakeup(full_bits=bits, burst_type=burst_type)
