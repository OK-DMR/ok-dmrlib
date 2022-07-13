from typing import List

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType


class TransmissionGenerator:
    """
    Utility class to generate data transmissions with given payload and encoding
    """

    @staticmethod
    def generate_csbk_preambles(
        source_address: int,
        target_address: int,
        target_address_is_individual: bool = True,
        num_of_preambles: int = 1,
        num_of_following_data_blocks: int = 1,
        colour_code: int = 1,
        sync_pattern: SyncPatterns = SyncPatterns.BsSourcedData,
    ) -> List[Burst]:
        bursts: List[Burst] = []
        slot_type: SlotType = SlotType(
            colour_code=colour_code, data_type=DataTypes.CSBK
        )
        final_count: int = num_of_preambles + num_of_following_data_blocks
        for i in reversed(range(num_of_following_data_blocks, final_count)):
            csbk_i = CSBK(
                source_address=source_address,
                target_address=target_address,
                blocks_to_follow=i,
                csbko=CsbkOpcodes.PreambleCSBK,
                target_address_is_individual=target_address_is_individual,
                # last_block True means CSBK or MBC Last Block
                last_block=True,
            )
            b_i = Burst(
                burst_type=BurstTypes.DataAndControl,
            )
            b_i.has_emb = False
            b_i.sync_or_embedded_signalling = sync_pattern
            b_i.slot_type = slot_type
            b_i.data = csbk_i
            bursts.append(b_i)

        return bursts
