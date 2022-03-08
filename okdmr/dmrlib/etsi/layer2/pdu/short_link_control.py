from typing import Union, Optional

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.etsi.crc.crc8 import CRC8
from okdmr.dmrlib.etsi.layer2.elements.slcos import SLCOs
from okdmr.dmrlib.etsi.layer3.elements.activity_id import ActivityID
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class ShortLinkControl(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.1.7 Short Link Control (SHORT LC) PDU
    """

    def __init__(
        self,
        slco: SLCOs,
        crc_8bit: Union[int, bitarray] = 0,
        # 7.1.3.1 Null Message - does not have any more data
        # 7.1.3.2 Activity Update
        ts1_activity_id: Optional[ActivityID] = None,
        ts2_activity_id: Optional[ActivityID] = None,
        ts1_address: Optional[bitarray] = None,
        ts2_address: Optional[bitarray] = None,
    ):
        self.slco: SLCOs = slco
        self.crc_8bit: bitarray = (
            crc_8bit[:8]
            if isinstance(crc_8bit, bitarray)
            else int2ba(crc_8bit, length=8)
        )
        self.ts1_activity_id: Optional[ActivityID] = ts1_activity_id
        self.ts1_address: Optional[bitarray] = ts1_address
        self.ts2_activity_id: Optional[ActivityID] = ts2_activity_id
        self.ts2_address: Optional[bitarray] = ts2_address

        if not ba2int(self.crc_8bit):
            self.crc_8bit = int2ba(
                CRC8.calculate(self.as_bits()[:28]), length=8, endian="little"
            )
            self.crc_ok: bool = True
        else:
            self.crc_ok: bool = CRC8.check(self.as_bits()[:28], ba2int(self.crc_8bit))

    def __repr__(self) -> str:
        descr: str = f"[{self.slco}]"
        if self.slco == SLCOs.NullMessage:
            pass
        elif self.slco == SLCOs.ActivityUpdate:
            descr += f"[TS1: {self.ts1_activity_id} / {self.ts1_address}] [TS2: {self.ts2_activity_id} / {self.ts2_address}]"
        else:
            raise KeyError(f"__repr__ not implemented for {self.slco}")

        return descr + f"{'' if self.crc_ok else ' [CRC INVALID]'}"

    @staticmethod
    def from_bits(bits: bitarray) -> "ShortLinkControl":
        assert (
            len(bits) >= 36
        ), f"Expected at least 36 bits (including 8-bit CRC), got {len(bits)}"
        slco: SLCOs = SLCOs.from_bits(bits[:4])
        if slco == SLCOs.NullMessage:
            return ShortLinkControl(slco=slco, crc_8bit=bits[28:36])
        elif slco == SLCOs.ActivityUpdate:
            return ShortLinkControl(
                slco=slco,
                crc_8bit=bits[28:36],
                ts1_activity_id=ActivityID.from_bits(bits[4:8]),
                ts2_activity_id=ActivityID.from_bits(bits[8:12]),
                ts1_address=bits[12:20],
                ts2_address=bits[20:28],
            )

        raise KeyError(f"from_bits not implemented for {slco}")

    def as_bits(self) -> bitarray:
        if self.slco == SLCOs.NullMessage:
            return self.slco.as_bits() + bitarray([0] * 24) + self.crc_8bit
        elif self.slco == SLCOs.ActivityUpdate:
            return (
                self.slco.as_bits()
                + self.ts1_activity_id.as_bits()
                + self.ts2_activity_id.as_bits()
                + self.ts1_address
                + self.ts2_address
                + self.crc_8bit
            )

        raise KeyError(f"as_bits not implemented for {self.slco}")
