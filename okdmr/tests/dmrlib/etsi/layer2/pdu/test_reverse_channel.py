from typing import List, Tuple

from okdmr.dmrlib.etsi.fec.hamming_16_11_4 import Hamming16114
from okdmr.dmrlib.etsi.fec.vbptc_32_11 import VBPTC3211
from okdmr.dmrlib.etsi.layer2.pdu.reverse_channel import ReverseChannel
from bitarray import bitarray

from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, byteswap_bytes, bytes_to_bits


def test_reverse_channel():
    merged_bits_odds = bitarray(f"01000000001101011" + f"10111111110010100")

    print(
        "ODD PARITY"
        if (merged_bits_odds.count(0) == merged_bits_odds.count(1))
        else "EVEN PARITY"
    )
    print(
        f"ZEROES {merged_bits_odds.count(0)}\tONES {merged_bits_odds.count(1)}\t\tLEN {len(merged_bits_odds)}"
    )

    merged_bits_even = bitarray(f"01000000010010000" + f"01000000010010000")

    print(
        "ODD PARITY"
        if (merged_bits_even.count(0) == merged_bits_even.count(1))
        else "EVEN PARITY"
    )
    print(
        f"ZEROES {merged_bits_even.count(0)}\tONES {merged_bits_even.count(1)}\t\tLEN {len(merged_bits_even)}"
    )

    rcs: List[Tuple[str,]] = [
        ("00000000000000000111100100100010",),
        ("00010000100000111000101000001010",),
        ("01000000100100000000000000000000",),
        ("01001100011111111110100101011010",),
        ("01010101011101101000010110011111",),
        ("01011011011000001010111000010101",),
        ("01011100111000010100011101111011",),
        ("01101111100100100001010100111000",),
        ("10001111110111110000010101010111",),
        ("10010001101101110100111001010101",),
        ("10011010011111101010111100001100",),
        ("10110100101110001110101110010100",),
        ("10110101101110001110111110000100",),
        ("11001100111111101100001011100101",),
        ("11101111101110001010111010010100",),
        ("11111000000001100000011001000101",),
        ("11111111111011111100111111111011",),
        ("11111111111111111111000101111011",),
        ("11111111111111111111111111111011",),
        ("11111111111111111111111111111110",),
        ("11111111111111111111111111111111",),
    ]
    for (rc,) in rcs:
        print("-!-" * 20)
        rc_bits: bitarray = bitarray(rc)
        rc_bits.reverse()
        rc_pdu: ReverseChannel = ReverseChannel.from_bits(rc_bits)
        print(repr(rc_pdu))
        if False:
            print("interleaved")
            print(rc_bits)
            print("deinterleaved")
            rc_bits_deinterleaved = VBPTC3211.deinterleave_all_bits(rc_bits)
            print(rc_bits_deinterleaved)

        rc_idx = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        h_idx = [22, 24, 26, 28, 30]
        pc_icx = [17, 19, 21, 23, 25, 27, 29, 31, 1, 3, 5, 7, 9, 11, 13, 15]

        rc2_bits = bitarray([rc_bits[x] for x in rc_idx])
        h_bits = bitarray([rc_bits[x] for x in h_idx])
        pc_bits = bitarray([rc_bits[x] for x in pc_icx])

        if False:
            print("manually")

        print("ODD PARITY" if (rc_bits.count(0) == rc_bits.count(1)) else "EVEN PARITY")
        if False:
            h_bits.reverse()
            rc2_bits.reverse()
            pc_bits.reverse()

        print(rc2_bits + h_bits)
        print(pc_bits)

        hamming_data = h_bits + rc2_bits
        # hamming_success, corrected_bits = Hamming16114.check_and_correct(hamming_data)
        # print(f"hamming status: {'OK' if hamming_success else 'FAILED'}")

        # assert rc_pdu.as_bits() == rc_bits
