from bitarray import bitarray
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

        example full frame:
        5a5a5a5a0000000042000501010000001111eeee555511114000000000000000000000006f0023003700fa00000000000000000000000000834f00c3e20801006f000000fa372300

        dissected:
        [5a 5a 5a 5a] - fixed header
        [00] - sequence number
        [00 00 00] - unknown data (3 bytes)
        [42] - packet type
        [00 05 01 01 00 00 00] - unknown data (7 bytes)
        [11 11] - timeslot "1" in this case, [22 22] means TS2
        [EE EE] - slot type - "SYNC" in this case
        [55 55] - color code "5"
        [11 11] - frame type - "voice sync" in this case
        [40 00] - unknown data (2 bytes)

        --- IPSC DMR Data payload begin ---

        [00 00 00 00 00] - unknown data (5 bytes)

        [00 00] \
        [00 00]  =>  these 3 identify destination radio/repeater, (16)[00006F] == (10)[111]
        [00 6F] /

        [00 23] \
        [00 37]  =>  these 3 identify source radio/repeater, (16)[2337FA] == (10)[2308090]
        [00 FA] /

        [ 13 times 00 ] - unknown data (13 bytes)
        [83 4F 00 C3] - unknown data (4 bytes), possible signature, checksum or similar

        --- IPSC DMR Data payload end ---

        [E2 08] - unknown data (2 bytes)
        [01] - call type - "group call" in this case, 00 means "private call"

        [00 6F 00 00] -> U4LE destination radio/repeater, (16)[00006F] == (10)[111]
        [00 FA 37 23] -> U4LE source radio/repeater, (16)[2337FA] == (10)[2308090]

        [00] - unknown data (1 byte)

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
        return repr(self.hytera_ipsc)

    @staticmethod
    def from_bits(bits: bitarray, burst_type: BurstTypes) -> "HyteraIPSCSync":
        return HyteraIPSCSync(full_bits=bits, burst_type=burst_type)
