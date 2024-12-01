from okdmr.dmrlib.etsi.layer2.pdu.reverse_channel import ReverseChannel
from bitarray import bitarray

from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, byteswap_bytes, bytes_to_bits


def test_reverse_channel():
    rcs: List[Tuple[str,]] = [
        ("01011011011000001010111000010101",),
        ("11111000000001100000011001000101",),
        ("10110101101110001110111110000100",),
        ("11101111101110001010111010010100",),
        # ("",),
    ]
    for (rc,) in rcs:
        rc_bits: bitarray = bitarray(rc)
        rc_pdu: ReverseChannel = ReverseChannel.from_bits(rc_bits)
        print(repr(rc_pdu))
        assert rc_pdu.as_bits() == rc_bits
