from typing import Union

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.etsi.fec.quadratic_residue_16_7_6 import QuadraticResidue1676
from okdmr.dmrlib.etsi.layer2.elements.lcss import LCSS
from okdmr.dmrlib.etsi.layer2.elements.preemption_power_indicator import (
    PreemptionPowerIndicator,
)
from okdmr.dmrlib.utils.bits_bytes import numpy_array_to_int
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class EmbeddedSignalling(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.1.2 Embedded signalling (EMB) PDU
    """

    def __init__(
        self,
        colour_code: int,
        preemption_and_power_control_indicator: int,
        link_control_start_stop: Union[LCSS, int],
        emb_parity: Union[int, bool] = 0,
    ):
        """

        :param colour_code: value 0-15
        :param preemption_and_power_control_indicator: value 0/1
        :param link_control_start_stop:
        :param emb_parity: value 0-511
        """
        assert (
            0b0 <= colour_code <= 0b1111
        ), f"CC (Colour Code) value must be in range 0-15, got {colour_code}"
        assert (
            0b00 <= link_control_start_stop <= 0b11
        ), f"LCSS value must be in range 0-3, got {link_control_start_stop}"
        assert (
            0b0 <= preemption_and_power_control_indicator <= 0b1
        ), f"PI must be in range 0-1, got {preemption_and_power_control_indicator}"

        self.colour_code: int = colour_code
        self.preemption_and_power_control_indicator: PreemptionPowerIndicator = (
            PreemptionPowerIndicator(preemption_and_power_control_indicator)
        )
        self.link_control_start_stop: LCSS = (
            LCSS(link_control_start_stop)
            if isinstance(link_control_start_stop, int)
            else link_control_start_stop
        )
        self.emb_parity: int = emb_parity if isinstance(emb_parity, int) else -1

        if self.emb_parity <= 0:
            # generate parity if not provided
            self.emb_parity = numpy_array_to_int(
                QuadraticResidue1676.generate(self.as_bits()[:7])[7:16]
            )

        # check parity
        self.emb_parity_ok: bool = QuadraticResidue1676.check(self.as_bits())

    def __repr__(self) -> str:
        return (
            f"[{self.link_control_start_stop}] [{self.preemption_and_power_control_indicator}] "
            f"[CC: {self.colour_code}]{'' if self.emb_parity_ok else ' [EMB FEC: INVALID]'}"
        )

    def as_bits(self) -> bitarray:
        return (
            int2ba(self.colour_code, length=4)
            + int2ba(self.preemption_and_power_control_indicator.value, length=1)
            + int2ba(self.link_control_start_stop.value, length=2)
            + int2ba(self.emb_parity, length=9)
        )

    @staticmethod
    def from_bits(bits: bitarray) -> "EmbeddedSignalling":
        assert (
            len(bits) == 16
        ), "EMB (Embedded Signalling) should be exactly 16 bits long"
        return EmbeddedSignalling(
            colour_code=ba2int(bits[0:4]),
            preemption_and_power_control_indicator=bits[4],
            link_control_start_stop=ba2int(bits[5:7]),
            emb_parity=ba2int(bits[7:16]),
        )
