from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.bptc_196_96 import BPTC19696
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.coding.trellis import Trellis34
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
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
        self.info_bits_interleaved: bitarray = (
            self.full_bits[:98] + self.full_bits[166:272]
        )
        self.info_bits: bitarray = GeneralDataBurst.deinterleave(
            bits=self.info_bits_interleaved,
            data_type=DataTypes(self.slot_type.data_type),
        )

    @staticmethod
    def deinterleave(bits: bitarray, data_type: DataTypes) -> bitarray:
        if data_type == DataTypes.Rate34Data:
            return Trellis34.decode(bits)
        elif data_type == DataTypes.Rate1Data or data_type == DataTypes.Rate12Data:
            return bits
        elif data_type == DataTypes.Reserved:
            raise ValueError(f"Unknown data type {data_type}")
        else:
            return BPTC19696.decode(bits)
