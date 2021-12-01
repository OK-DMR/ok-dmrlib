from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType


class GeneralDataBurst(Burst):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 6.2 Data and control, Figure 6.5: General data burst
    """

    def __init__(self, full_burst: bytes):
        super().__init__(full_burst=full_burst)
        # 98 info + 10 slot type + 48 sync or embedded + 10 slot type + 98 info
        self.slot_type: SlotType = SlotType.from_bits(
            self.full_bits[98:108] + self.full_bits[156:166]
        )
        self.info_bits: bitarray = self.full_bits[:98] + self.full_bits[164:]
