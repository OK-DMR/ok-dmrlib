#!/usr/bin/env python3
from array import array
from typing import Union, List, Dict, Tuple

from bitarray import bitarray
from bitarray.util import ba2int


class Trellis34:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.2.4  Rate ¾ Trellis code
    """

    # disable black formatting for following scalar arrays, see https://github.com/psf/black/issues/1281
    # fmt: off
    TRELLIS34_INTERLEAVE_MATRIX: List[int] = [
        0, 1, 8, 9, 16, 17, 24, 25, 32, 33, 40, 41, 48, 49, 56, 57, 64, 65, 72, 73, 80, 81, 88, 89, 96, 97,
        2, 3, 10, 11, 18, 19, 26, 27, 34, 35, 42, 43, 50, 51, 58, 59, 66, 67, 74, 75, 82, 83, 90, 91,
        4, 5, 12, 13, 20, 21, 28, 29, 36, 37, 44, 45, 52, 53, 60, 61, 68, 69, 76, 77, 84, 85, 92, 93,
        6, 7, 14, 15, 22, 23, 30, 31, 38, 39, 46, 47, 54, 55, 62, 63, 70, 71, 78, 79, 86, 87, 94, 95,
    ]

    TRELLIS34_ENCODER_STATE_TRANSITION: List[int] = [
        0, 8, 4, 12, 2, 10, 6, 14,
        4, 12, 2, 10, 6, 14, 0, 8,
        1, 9, 5, 13, 3, 11, 7, 15,
        5, 13, 3, 11, 7, 15, 1, 9,
        3, 11, 7, 15, 1, 9, 5, 13,
        7, 15, 1, 9, 5, 13, 3, 11,
        2, 10, 6, 14, 0, 8, 4, 12,
        6, 14, 0, 8, 4, 12, 2, 10,
    ]

    TRELLIS34_DIBITS: Dict[Tuple[int, int], int] = {
        (0, 1): 3,
        (0, 0): 1,
        (1, 0): -1,
        (1, 1): -3,
    }
    TRELLIS34_DIBITS_REVERSE: Dict[int, Tuple[int, int]] = dict((v, k) for k, v in TRELLIS34_DIBITS.items())

    TRELLIS34_CONSTELLATION_POINTS: Dict[Tuple[int, int], int] = {
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
    TRELLIS34_CONSTELLATION_POINTS_REVERSE: Dict[int, Tuple[int, int]] = dict(
        (v, k) for k, v in TRELLIS34_CONSTELLATION_POINTS.items())

    # fmt: on

    @staticmethod
    def bits_to_dibits(stream: bitarray) -> array:
        """
        Convert each 2-bits from input to Trellis3/4 dibit (values 3,1,-1,3)
        :rtype: int[]
        """
        # "b" means array stores signed chars, aka -128 through +128
        out: array = array("b", [0] * (int(len(stream) / 2)))

        for i in range(0, len(stream), 2):
            o = int(i / 2)
            out[o] = Trellis34.TRELLIS34_DIBITS[(stream[i], stream[i + 1])]

        return out

    @staticmethod
    def dibits_to_bits(dibits: array) -> bitarray:
        """
        Convert each input array value (3,1,-1,-3) to 2-bit representation

        :param dibits:
        :return: bitarray of size 2xlen(input)
        """
        out: bitarray = bitarray()

        for dibit in dibits:
            for bit in Trellis34.TRELLIS34_DIBITS_REVERSE[dibit]:
                out.append(bit)

        return out

    @staticmethod
    def deinterleave(original: array) -> array:
        """
        De-Interleaves input array with Trellis 3/4 interleave matrix

        :rtype: int[]
        """

        # "b" means array stores signed chars, aka -128 through +128
        out: array = array("b", [0] * len(original))

        for i in range(0, len(Trellis34.TRELLIS34_INTERLEAVE_MATRIX)):
            out[Trellis34.TRELLIS34_INTERLEAVE_MATRIX[i]] = original[i]

        return out

    @staticmethod
    def interleave(deinterleaved: array) -> array:
        """
        Interleave input array with Trellis 3/4 interleave matrix

        :param deinterleaved:
        :return:
        """
        out: array = array("b", [0] * 98)

        for i in range(0, len(Trellis34.TRELLIS34_INTERLEAVE_MATRIX)):
            out[i] = deinterleaved[Trellis34.TRELLIS34_INTERLEAVE_MATRIX[i]]

        return out

    @staticmethod
    def dibits_to_points(deinterleaved: array) -> array:
        """
        Converts de-interleaved dibits (values 3,1,-1,-3) to constellation points (values 0 through 15)

        :rtype: int[]
        """
        # "B" means array stores unsigned chars, aka 0 through 255
        out: array = array("B", [0] * int(len(deinterleaved) / 2))

        for i in range(0, len(deinterleaved), 2):
            o = int(i / 2)
            out[o] = Trellis34.TRELLIS34_CONSTELLATION_POINTS[
                (deinterleaved[i], deinterleaved[i + 1])
            ]

        return out

    @staticmethod
    def points_to_dibits(constellations: array) -> array:
        """
        Convert constellation points (values 0 through 15) to dibits (values 3,1,-1,-3)

        :param constellations:
        :return:
        """
        out: array = array("b")

        for constellation in constellations:
            for dibit in Trellis34.TRELLIS34_CONSTELLATION_POINTS_REVERSE[
                constellation
            ]:
                out.append(dibit)

        return out

    @staticmethod
    def points_to_tribits(constellation_points: array) -> array:
        """
        Convert each constellation point into 3-bit value

        :rtype: object
        """
        out: array = array("B", [0] * 49)
        last: int = 0

        for i in range(0, 49):
            start = last * 8
            matches = False

            for j in range(start, start + 8):
                if (
                    constellation_points[i]
                    == Trellis34.TRELLIS34_ENCODER_STATE_TRANSITION[j]
                ):
                    matches = True
                    last = abs((j - start) % 255)
                    out[i] = last

            assert (
                matches
            ), f"Trellis data corrupted, index {i} constellation point {constellation_points[i]}"

        return out

    @staticmethod
    def tribits_to_points(tribits: array) -> array:
        """
        Convert 3-bit values to constellation points

        :param tribits:
        :return:
        """
        out: array = array("B", [0] * len(tribits))
        state: int = 0

        for i in range(0, len(tribits)):
            out[i] = Trellis34.TRELLIS34_ENCODER_STATE_TRANSITION[
                state * 8 + tribits[i]
            ]
            state = tribits[i]

        return out

    @staticmethod
    def tribits_to_bits(tribits: array) -> bitarray:
        """
        Convert 3-bit representations to raw bitstream

        :param tribits:
        :return:
        """
        assert len(tribits) == 49, f"Expected 49 tribits got {len(tribits)}"
        out: bitarray = bitarray(144 * [0], endian="big")

        for i in range(0, 144, 3):
            o = int(i / 3)
            out[i] = (tribits[o] & 0x4) > 0
            out[i + 1] = (tribits[o] & 0x2) > 0
            out[i + 2] = (tribits[o] & 0x1) > 0

        return out

    @staticmethod
    def bits_to_tribits(original: bitarray) -> array:
        """
        Convert raw bitstream to 3-bit representations

        :param original:
        :return:
        """
        out: array = array("B")

        for i in range(0, len(original), 3):
            out.append(ba2int(original[i : i + 3], signed=False))
        out.append(0)

        return out

    @staticmethod
    def decode(encoded: bitarray, as_bytes: bool = False) -> Union[bitarray, bytes]:
        """
        Convert Trellis3/4 encoded bitstream to raw data bits (or bytes)

        :param encoded:
        :param as_bytes: if return should be of type "bytes"
        :return:
        """
        assert (
            len(encoded) == 196
        ), f"trellis_34_decode requires 24.5 bytes (196 bits), got {len(encoded)} bits"

        dibits: array = Trellis34.bits_to_dibits(encoded)
        deinterleaved_dibits: array = Trellis34.deinterleave(dibits)
        points: array = Trellis34.dibits_to_points(deinterleaved_dibits)
        tribits: array = Trellis34.points_to_tribits(points)
        decoded: bitarray = Trellis34.tribits_to_bits(tribits)
        return decoded.tobytes() if as_bytes else decoded

    @staticmethod
    def encode(decoded: Union[bitarray, bytes]) -> bitarray:
        """
        Convert raw data bits (or bytes) to Trellis3/4 encoded bitstream

        :param decoded:
        :return:
        """
        if isinstance(decoded, bytes):
            bits: bitarray = bitarray(endian="big")
            bits.frombytes(decoded)
            decoded = bits

        assert (
            len(decoded) >= 144
        ), f"trellis_34_encode requires 18 bytes (144 bits), got {len(decoded)} bits"
        decoded = decoded[:144]

        tribits: array = Trellis34.bits_to_tribits(decoded)
        points: array = Trellis34.tribits_to_points(tribits)
        dibits: array = Trellis34.points_to_dibits(points)
        interleaved_dibits: array = Trellis34.interleave(dibits)
        encoded: bitarray = Trellis34.dibits_to_bits(interleaved_dibits)
        return encoded
