from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.utils.bits_interface import BitsInterface


class FragmentSequenceNumber(BitsInterface):
    SINGLE_UNCONFIRMED_FRAGMENT_VALUE: int = 0b0000
    SINGLE_CONFIRMED_FRAGMENT_VALUE: int = 0b1000

    def __init__(self, value: int = 0):
        assert (
            0b0000 <= value <= 0b1111
        ), f"FSN value out of range 0b0000-0b1111 got {bin(value)}"
        self.value: int = value

    def is_last(self) -> bool:
        return (
            # single (last) unconfirmed fragment
            self.value == FragmentSequenceNumber.SINGLE_UNCONFIRMED_FRAGMENT_VALUE
            # 0b1000 is single confirmed, bigger values are last fragment
            or self.value >= FragmentSequenceNumber.SINGLE_CONFIRMED_FRAGMENT_VALUE
        )

    def __repr__(self) -> str:
        desc: str = ""
        if self.value == FragmentSequenceNumber.SINGLE_UNCONFIRMED_FRAGMENT_VALUE:
            desc = "Unconfirmed data single fragment"
        elif self.value == FragmentSequenceNumber.SINGLE_CONFIRMED_FRAGMENT_VALUE:
            desc = "Confirmed data single fragment"
        else:
            num: int = self.value & 0b111
            is_last: str = "Last" if self.is_last() else "Subsequent"
            desc = f"{is_last} confirmed data fragment, number {num}"
        return f"[FSN: {desc}]"

    @staticmethod
    def from_bits(bits: bitarray) -> "FragmentSequenceNumber":
        return FragmentSequenceNumber(value=ba2int(bits[0:4]))

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=4)
