from typing import Union

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.etsi.fec.golay_20_8_7 import Golay2087
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.utils.bits_bytes import numpy_array_to_int
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class SlotType(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.1.3 Slot Type (SLOT) PDU
    """

    def __init__(
        self, colour_code: int, data_type: Union[int, DataTypes], parity: int = 0
    ):
        """

        :param colour_code: value 0-15
        :param data_type: DataTypes or value 0-15
        :param parity: value 0-4095
        """
        assert (
            0b0 <= colour_code <= 0b1111
        ), f"Colour Code must be in range 0-15, got {colour_code}"
        assert (
            0
            <= (data_type.value if isinstance(data_type, DataTypes) else data_type)
            <= 0b1111
        ), f"Data Type must be in range 0-15, got {data_type}"
        assert (
            0 <= parity <= 0b111111111111
        ), f"Parity must be in range 0-4095, got {parity}"
        self.colour_code: int = colour_code
        self.data_type: DataTypes = (
            DataTypes(data_type) if isinstance(data_type, int) else data_type
        )

        self.fec_parity: int = parity

        if parity < 1:
            # generate parity if not provided
            self.fec_parity = numpy_array_to_int(
                Golay2087.generate(self.as_bits()[:8])[8:]
            )

        # check parity
        self.fec_parity_ok: bool = Golay2087.check(self.as_bits())

    def as_bits(self) -> bitarray:
        return (
            int2ba(self.colour_code, length=4)
            + int2ba(self.data_type.value, length=4)
            + int2ba(self.fec_parity, length=12)
        )

    def __repr__(self) -> str:
        return f"[{self.data_type}] [CC: {self.colour_code}]{'' if self.fec_parity_ok else ' [SLOT FEC: INVALID]'}"

    @staticmethod
    def from_bits(bits: bitarray) -> "SlotType":
        assert len(bits) == 20, "SlotType must be 20 bits"
        return SlotType(
            colour_code=ba2int(bits[:4]),
            data_type=ba2int(bits[4:8]),
            parity=ba2int(bits[8:]),
        )
