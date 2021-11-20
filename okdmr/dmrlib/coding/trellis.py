#!/usr/bin/env python3
from array import array

from bitarray import bitarray
from bitarray.util import ba2int

# disable black formatting for following scalar arrays, see https://github.com/psf/black/issues/1281
# fmt: off
TRELLIS34_INTERLEAVE_MATRIX: list[int] = [
    0, 1, 8, 9, 16, 17, 24, 25, 32, 33, 40, 41, 48, 49, 56, 57, 64, 65, 72, 73, 80, 81, 88, 89, 96, 97,
    2, 3, 10, 11, 18, 19, 26, 27, 34, 35, 42, 43, 50, 51, 58, 59, 66, 67, 74, 75, 82, 83, 90, 91,
    4, 5, 12, 13, 20, 21, 28, 29, 36, 37, 44, 45, 52, 53, 60, 61, 68, 69, 76, 77, 84, 85, 92, 93,
    6, 7, 14, 15, 22, 23, 30, 31, 38, 39, 46, 47, 54, 55, 62, 63, 70, 71, 78, 79, 86, 87, 94, 95,
]

TRELLIS34_ENCODER_STATE_TRANSITION: list[int] = [
    0, 8, 4, 12, 2, 10, 6, 14,
    4, 12, 2, 10, 6, 14, 0, 8,
    1, 9, 5, 13, 3, 11, 7, 15,
    5, 13, 3, 11, 7, 15, 1, 9,
    3, 11, 7, 15, 1, 9, 5, 13,
    7, 15, 1, 9, 5, 13, 3, 11,
    2, 10, 6, 14, 0, 8, 4, 12,
    6, 14, 0, 8, 4, 12, 2, 10,
]

TRELLIS34_DIBITS: dict[tuple[int, int], int] = {
    (0, 1): 3,
    (0, 0): 1,
    (1, 0): -1,
    (1, 1): -3,
}
TRELLIS34_DIBITS_REVERSE: dict[int, tuple[int, int]] = dict((v, k) for k, v in TRELLIS34_DIBITS.items())

TRELLIS34_CONSTELLATION_POINTS: dict[tuple[int, int], int] = {
    (1, -1): 0,
    (-1, -1): 1,
    (3, -3): 2,
    (-3, -3): 3,
    (-3, -1): 4,
    (3, -1): 5,
    (-1, -3): 6,
    (1, -3): 7,
    (-3, 3): 8,
    (3, 3): 9,
    (-1, 1): 10,
    (1, 1): 11,
    (1, 3): 12,
    (-1, 3): 13,
    (3, 1): 14,
    (-3, 1): 15,
}
TRELLIS34_CONSTELLATION_POINTS_REVERSE: dict[int, tuple[int, int]] = dict(
    (v, k) for k, v in TRELLIS34_CONSTELLATION_POINTS.items())


# fmt: on


def trellis34_make_dibits(stream: bitarray) -> array:
    """
    Converts each 2 bits from input to Trellis3/4 dibit (values 3,1,-1,3)
    :rtype: int[]
    """
    assert len(stream) == 196, "t34_make_dibits expects 196 bits in bitarray"

    # "b" means array stores signed chars, aka -128 through +128
    out: array = array("b", [0] * 98)

    for i in range(0, 196, 2):
        o = int(i / 2)
        out[o] = TRELLIS34_DIBITS[(stream[i], stream[i + 1])]

    return out


def trellis34_reverse_dibits(dibits: array) -> bitarray:
    out: bitarray = bitarray()

    for dibit in dibits:
        for bit in TRELLIS34_DIBITS_REVERSE[dibit]:
            out.append(bit)

    return out


def trellis34_deinterleave(original: array) -> array:
    """
    De-Interleaves dibits

    :rtype: int[]
    """

    # "b" means array stores signed chars, aka -128 through +128
    out: array = array("b", [0] * 98)

    for i in range(0, 98):
        out[TRELLIS34_INTERLEAVE_MATRIX[i]] = original[i]

    return out


def trellis34_interleave(deinterleaved: array) -> array:
    """
    Interleave dibits

    :param deinterleaved:
    :return:
    """
    out: array = array("b", [0] * len(deinterleaved))

    # print("deinterleaved", len(deinterleaved), deinterleaved)
    # print("matrix", len(TRELLIS34_INTERLEAVE_MATRIX))

    for i in range(0, len(deinterleaved)):
        # print(i, TRELLIS34_INTERLEAVE_MATRIX[i]) #, deinterleaved[TRELLIS34_INTERLEAVE_MATRIX[i]])
        out[i] = deinterleaved[TRELLIS34_INTERLEAVE_MATRIX[i]]

    return out


def trellis34_constellation_points(deinterleaved: array) -> array:
    """
    Converts de-interleaved dibits (values 3,1,-1,-3) to constellation values (values 0 through 15)

    :rtype: int[]
    """
    # "B" means array stores unsigned chars, aka 0 through 255
    out: array = array("B", [0] * 49)

    for i in range(0, 98, 2):
        o = int(i / 2)
        out[o] = TRELLIS34_CONSTELLATION_POINTS[
            (deinterleaved[i], deinterleaved[i + 1])
        ]

    return out


def trellis34_reverse_constellation_points(constellations: array) -> array:
    out: array = array("b")

    for constellation in constellations:
        for dibit in TRELLIS34_CONSTELLATION_POINTS_REVERSE[constellation]:
            out.append(dibit)

    return out


def trellis34_extract_tribits(constellation_points: array) -> array:
    """


    :rtype: object
    """
    out: array = array("B", [0] * 48)
    last: int = 0

    for i in range(48):
        start = last * 8
        matches = False

        for j in range(start, start + 8):
            if constellation_points[i] == TRELLIS34_ENCODER_STATE_TRANSITION[j]:
                matches = True
                last = abs((j - start) % 255)
                out[i] = last
                break

        assert (
            matches
        ), f"Trellis data corrupted, point {i} constellation {constellation_points[i]}"

    return out


def trellis34_reverse_extract_tribits(tribits: array) -> array:
    out: array = array("B", [0] * 49)
    state: int = 0

    for i in range(0, len(tribits)):
        out[i] = TRELLIS34_ENCODER_STATE_TRANSITION[state * 8 + tribits[i]]
        state = tribits[i]

    return out


def trellis34_tribits_to_binary(tribits: array) -> bitarray:
    assert len(tribits) == 48, f"Expected 48 tribits got {len(tribits)}"
    out: bitarray = bitarray(196 * "0", endian="big")

    for i in range(0, 144, 3):
        o = int(i / 3)
        out[i] = (tribits[o] & 0x4) > 0
        out[i + 1] = (tribits[o] & 0x2) > 0
        out[i + 2] = (tribits[o] & 0x1) > 0

    return out


def trellis34_binary_to_tribits(original: bitarray) -> array:
    out: array = array("B")

    for i in range(0, len(original), 3):
        out.append(ba2int(original[i : i + 3], signed=False))

    return out[:48]


def trellis_34_decode(encoded: bitarray) -> bitarray:
    assert (
        len(encoded) == 196
    ), f"trellis_34_decode requires 18 bytes (196 bits), got {len(encoded)} bits"
    dibits: array = trellis34_make_dibits(encoded)
    deinterleaved: array = trellis34_deinterleave(dibits)
    points: array = trellis34_constellation_points(deinterleaved)
    tribits: array = trellis34_extract_tribits(points)
    decoded: bitarray = trellis34_tribits_to_binary(tribits)
    return decoded


def trellis_34_encode(decoded: bitarray) -> bitarray:
    assert (
        len(decoded) >= 196
    ), f"trellis_34_encode requires 18 bytes (196 bits), got {len(decoded)} bits"
    decoded = decoded[:196]

    tribits: array = trellis34_binary_to_tribits(decoded)
    points: array = trellis34_reverse_extract_tribits(tribits)
    deinterleaved: array = trellis34_reverse_constellation_points(points)
    dibits: array = trellis34_interleave(deinterleaved)
    encoded: bitarray = trellis34_reverse_dibits(dibits)

    return encoded


def trellis_34_encode_bytes(payload: bytes) -> bitarray:
    bits: bitarray = bitarray(endian="big")
    bits.frombytes(payload)
    return trellis_34_encode(bits)


def trellis_34_decode_as_bytes(encoded: bitarray) -> bytes:
    decoded: bitarray = trellis_34_decode(encoded)
    return decoded.tobytes()
