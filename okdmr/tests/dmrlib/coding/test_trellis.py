from array import array
from typing import Dict, Any

from bitarray import bitarray

from okdmr.dmrlib.coding.trellis import (
    trellis34_bits_to_dibits,
    trellis34_dibits_to_bits,
    trellis34_deinterleave,
    trellis34_interleave,
    trellis34_dibits_to_points,
    trellis34_points_to_dibits,
    trellis34_points_to_tribits,
    trellis34_tribits_to_points,
    trellis34_tribits_to_bits,
    trellis34_bits_to_tribits,
    trellis34_decode,
    trellis34_encode,
)

# trellis bits as string => decoded bytes
TRELLIS_TEST_DATA: Dict[str, str] = {
    "0010100000101111111000101011010111010010111111110010001011100010011101100010111100111110110100100111001000101110111110100001001000100010011100101111101100101111001000101001011100100010111101110010": "006200014100480019804a0020005400410000000000000000",
    "0010010011110110110100100011111111100010001101010010001000010010101011101101001001111111110100100110100011100010111100100001001011111010111000101111000001111000001000100100011100101111100001110010": "02f24400590020004d004100520045004b0000000000000000",
    "0010001100100010001000100010001000100010101011000010110111110010001000100010001000100010000100001101011100100010001000100010001000100010101001000000100100100010001000100010001000100010001010100110": "0538000000000000000000000000f486aed800000000000000",
}

# fmt: off
TRELLIS_MESSAGE_PARTS: Dict[str, Any] = {
    "encoded": bitarray(
        "0010100000101111111000101011010111010010111111110010001011100010011101100010111100111110110100100111001000101110111110100001001000100010011100101111101100101111001000101001011100100010111101110010"),
    "dibits_interleaved": array('b',
                                [1, -1, -1, 1, 1, -1, -3, -3, -3, -1, 1, -1, -1, -3, 3, 3, -3, 3, 1, -1, -3, -3, -3, -3,
                                 1, -1, 1, -1, -3, -1, 1, -1, 3, -3, 3, -1, 1, -1, -3, -3, 1, -3, -3, -1, -3, 3, 1, -1,
                                 3, -3, 1, -1, 1, -1, -3, -1, -3, -3, -1, -1, 1, 3, 1, -1, 1, -1, 1, -1, 3, -3, 1, -1,
                                 -3, -3, -1, -3, 1, -1, -3, -3, 1, -1, 1, -1, -1, 3, 3, -3, 1, -1, 1, -1, -3, -3, 3, -3,
                                 1, -1]),
    "dibits_deinterleaved": array('b',
                                  [1, -1, 1, -1, 1, -1, -1, -3, -1, 1, -3, -1, 1, -1, 1, -1, 1, -1, 1, -1, -3, -1, -3,
                                   -3, -3, -3, 3, -3, -3, -3, 1, -1, -3, -1, 3, -1, -1, -1, 1, -1, 1, -1, 1, -1, 1, 3,
                                   -1, 3, -1, -3, -3, -3, 1, -1, 3, -3, 3, 3, 1, -3, 1, -1, 1, -1, -3, 3, -3, -1, 1, -1,
                                   1, -1, 1, -1, -3, 3, 3, -3, -3, -3, -3, -3, 1, -1, 1, -1, 3, -3, -3, -3, 3, -3, -3,
                                   -3, 1, -1, 1, -1]),
    "points": array('B',
                                  [0, 0, 0, 6, 10, 4, 0, 0, 0, 0, 4, 3, 3, 2, 3, 0, 4, 5, 1, 0, 0, 0, 12, 13, 6, 3, 0,
                                   2, 9, 7, 0, 0, 8, 4, 0, 0, 0, 8, 2, 3, 3, 0, 0, 2, 3, 2, 3, 0, 0]),
    "tribits": array('B',
                     [0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 2, 4, 0, 4, 0, 0, 2, 2, 0, 0, 0, 0, 3, 1, 4, 0, 0, 4, 5, 0, 0, 0, 1,
                      0, 0, 0, 0, 1, 2, 4, 0, 0, 0, 4, 0, 4, 0, 0]),
    "decoded": bitarray(
        '0000000001100010000000000000000101000001000000000100100000000000000110011000000001001010000000000010000000000000010101000000000001000001000000000000000000000000000000000000000000000000000000000000')
}


# fmt: on


def test_trellis_decode():
    for bitstring, bytestring in TRELLIS_TEST_DATA.items():
        assert trellis34_decode(bitarray(bitstring), as_bytes=True) == bytes.fromhex(
            bytestring
        )


def test_trellis_encode():
    for bitstring, bytestring in TRELLIS_TEST_DATA.items():
        assert trellis34_encode(bytes.fromhex(bytestring)) == bitarray(bitstring)


def test_bits_dibits():
    assert (
        trellis34_bits_to_dibits(TRELLIS_MESSAGE_PARTS["encoded"])
        == TRELLIS_MESSAGE_PARTS["dibits_interleaved"]
    )
    assert (
        trellis34_dibits_to_bits(TRELLIS_MESSAGE_PARTS["dibits_interleaved"])
        == TRELLIS_MESSAGE_PARTS["encoded"]
    )


def test_interleave_deinterleave():
    assert (
        trellis34_deinterleave(TRELLIS_MESSAGE_PARTS["dibits_interleaved"])
        == TRELLIS_MESSAGE_PARTS["dibits_deinterleaved"]
    )
    assert (
        trellis34_interleave(TRELLIS_MESSAGE_PARTS["dibits_deinterleaved"])
        == TRELLIS_MESSAGE_PARTS["dibits_interleaved"]
    )


def test_deinterleaved_constellations():
    assert (
        trellis34_dibits_to_points(TRELLIS_MESSAGE_PARTS["dibits_deinterleaved"])
        == TRELLIS_MESSAGE_PARTS["points"]
    )
    assert (
        trellis34_points_to_dibits(TRELLIS_MESSAGE_PARTS["points"])
        == TRELLIS_MESSAGE_PARTS["dibits_deinterleaved"]
    )


def test_tribits_constellations():
    assert (
        trellis34_points_to_tribits(TRELLIS_MESSAGE_PARTS["points"])
        == TRELLIS_MESSAGE_PARTS["tribits"]
    )
    assert (
        trellis34_tribits_to_points(TRELLIS_MESSAGE_PARTS["tribits"])
        == TRELLIS_MESSAGE_PARTS["points"]
    )


def test_binary_tribits():
    assert (
        trellis34_tribits_to_bits(TRELLIS_MESSAGE_PARTS["tribits"])
        == TRELLIS_MESSAGE_PARTS["decoded"]
    )
    assert (
        trellis34_bits_to_tribits(TRELLIS_MESSAGE_PARTS["decoded"])
        == TRELLIS_MESSAGE_PARTS["tribits"]
    )
