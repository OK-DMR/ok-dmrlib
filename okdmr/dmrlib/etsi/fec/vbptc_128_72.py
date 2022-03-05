from typing import Dict, Tuple

import numpy
from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.etsi.fec.five_bit_checksum import FiveBitChecksum
from okdmr.dmrlib.etsi.fec.hamming_16_11_4 import Hamming16114


class VBPTC12873:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.2.1 Variable length BPTC for embedded signalling

    Full size of embedded signalling LC is 128 bits, providing 72 bits of LC information, 5 bits of 5-bit checksum,
    rest (51 bits) are row hammings (7 rows, each 5 hamming bits, total 35 bits) and column parity check bits (16 bits)
    """

    # disable formatter for this whole table, as manual formatting is applied
    # fmt: off
    # @formatter:off
    INTERLEAVING_INDICES: Dict[int, Tuple[int, int, int, bool, bool]] = {
        # (key) index => (value) interleave index, row, column, is row hamming, is 5-bit checksum
        # rows are numbered from 1 to match the documentation/specification

        # Row 1 of table, starts with LC(71)
        0: (0, 1, 0, False, False),
        1: (8, 1, 1, False, False),
        2: (16, 1, 2, False, False),
        3: (24, 1, 3, False, False),
        4: (32, 1, 4, False, False),
        5: (40, 1, 5, False, False),
        6: (48, 1, 6, False, False),
        7: (56, 1, 7, False, False),
        8: (64, 1, 8, False, False),
        9: (72, 1, 9, False, False),
        10: (80, 1, 10, False, False),
        # Row 1 hamming bits, starts with H1(4)
        11: (88, 1, 11, True, False),
        12: (96, 1, 12, True, False),
        13: (104, 1, 13, True, False),
        14: (112, 1, 14, True, False),
        15: (120, 1, 15, True, False),

        # Row 2 of table, starts with LC(60)
        16: (1, 2, 0, False, False),
        17: (9, 2, 1, False, False),
        18: (17, 2, 2, False, False),
        19: (25, 2, 3, False, False),
        20: (33, 2, 4, False, False),
        21: (41, 2, 5, False, False),
        22: (49, 2, 6, False, False),
        23: (57, 2, 7, False, False),
        24: (65, 2, 8, False, False),
        25: (73, 2, 9, False, False),
        26: (81, 2, 10, False, False),
        # Row 2 hamming bits, starts with H2(4)
        27: (89, 2, 11, True, False),
        28: (97, 2, 12, True, False),
        29: (105, 2, 13, True, False),
        30: (113, 2, 14, True, False),
        31: (121, 2, 15, True, False),

        # Row 3 of table, starts with LC(49)
        32: (2, 3, 0, False, False),
        33: (10, 3, 1, False, False),
        34: (18, 3, 2, False, False),
        35: (26, 3, 3, False, False),
        36: (34, 3, 4, False, False),
        37: (42, 3, 5, False, False),
        38: (50, 3, 6, False, False),
        39: (58, 3, 7, False, False),
        40: (66, 3, 8, False, False),
        41: (74, 3, 9, False, False),
        # CS(4)
        42: (82, 3, 10, False, True),
        # Row 2 hamming bits, starts with H3(4)
        43: (90, 3, 11, True, False),
        44: (98, 3, 12, True, False),
        45: (106, 3, 13, True, False),
        46: (114, 3, 14, True, False),
        47: (122, 3, 15, True, False),

        # Row 4 of table, starts with LC(39)
        48: (3, 4, 0, False, False),
        49: (11, 4, 1, False, False),
        50: (19, 4, 2, False, False),
        51: (27, 4, 3, False, False),
        52: (35, 4, 4, False, False),
        53: (43, 4, 5, False, False),
        54: (51, 4, 6, False, False),
        55: (59, 4, 7, False, False),
        56: (67, 4, 8, False, False),
        57: (75, 4, 9, False, False),
        # CS(3)
        58: (83, 4, 10, False, True),
        # Row 2 hamming bits, starts with H4(4)
        59: (91, 4, 11, True, False),
        60: (99, 4, 12, True, False),
        61: (107, 4, 13, True, False),
        62: (115, 4, 14, True, False),
        63: (123, 4, 15, True, False),

        # Row 5 of table, starts with LC(29)
        64: (4, 5, 0, False, False),
        65: (12, 5, 1, False, False),
        66: (20, 5, 2, False, False),
        67: (28, 5, 3, False, False),
        68: (36, 5, 4, False, False),
        69: (44, 5, 5, False, False),
        70: (52, 5, 6, False, False),
        71: (60, 5, 7, False, False),
        72: (68, 5, 8, False, False),
        73: (76, 5, 9, False, False),
        # CS(2)
        74: (84, 5, 10, False, True),
        # Row 2 hamming bits, starts with H5(4)
        75: (92, 5, 11, True, False),
        76: (100, 5, 12, True, False),
        77: (108, 5, 13, True, False),
        78: (116, 5, 14, True, False),
        79: (124, 5, 15, True, False),

        # Row 6 of table, starts with LC(19)
        80: (5, 6, 0, False, False),
        81: (13, 6, 1, False, False),
        82: (21, 6, 2, False, False),
        83: (29, 6, 3, False, False),
        84: (37, 6, 4, False, False),
        85: (45, 6, 5, False, False),
        86: (53, 6, 6, False, False),
        87: (61, 6, 7, False, False),
        88: (69, 6, 8, False, False),
        89: (77, 6, 9, False, False),
        # CS(1)
        90: (85, 6, 10, False, True),
        # Row 2 hamming bits, starts with H6(4)
        91: (93, 6, 11, True, False),
        92: (101, 6, 12, True, False),
        93: (109, 6, 13, True, False),
        94: (117, 6, 14, True, False),
        95: (125, 6, 15, True, False),

        # Row 7 of table, starts with LC(9)
        96: (6, 7, 0, False, False),
        97: (14, 7, 1, False, False),
        98: (22, 7, 2, False, False),
        99: (30, 7, 3, False, False),
        100: (38, 7, 4, False, False),
        101: (46, 7, 5, False, False),
        102: (54, 7, 6, False, False),
        103: (62, 7, 7, False, False),
        104: (70, 7, 8, False, False),
        105: (78, 7, 9, False, False),
        # CS(0)
        106: (86, 7, 10, False, True),
        # Row 2 hamming bits, starts with H7(4)
        107: (94, 7, 11, True, False),
        108: (102, 7, 12, True, False),
        109: (110, 7, 13, True, False),
        110: (118, 7, 14, True, False),
        111: (126, 7, 15, True, False),

        # Row 8 of table, only column parity bits, starts with PC(15)
        112: (7, 8, 0, False, False),
        113: (15, 8, 1, False, False),
        114: (23, 8, 2, False, False),
        115: (31, 8, 3, False, False),
        116: (39, 8, 4, False, False),
        117: (47, 8, 5, False, False),
        118: (55, 8, 6, False, False),
        119: (63, 8, 7, False, False),
        120: (71, 8, 8, False, False),
        121: (79, 8, 9, False, False),
        122: (87, 8, 10, False, False),
        123: (95, 8, 11, False, False),
        124: (103, 8, 12, False, False),
        125: (111, 8, 13, False, False),
        126: (119, 8, 14, False, False),
        127: (127, 8, 15, False, False),
    }
    """Interleave table as key(index) => value(interleave index, row, column, is reserved, is hamming)"""
    # @formatter:on
    # fmt: on

    FULL_INTERLEAVING_MAP: Dict[int, int] = dict(
        (k, v[0]) for k, v in INTERLEAVING_INDICES.items()
    )
    """Extract only (table index -> interleave index)"""
    FULL_DEINTERLEAVING_MAP: Dict[int, int] = dict(
        (v[0], k) for k, v in INTERLEAVING_INDICES.items()
    )
    """Extract only (interleave index -> index)"""
    DEINTERLEAVE_INFO_BITS_ONLY_MAP: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (k, v[0])
                for k, v in INTERLEAVING_INDICES.items()
                if not v[3]
                and not v[4]
                and v[1] != 8  # not reserved or hamming bits or row 8 (parity bits)
            ).values()
        )
    )
    """Extract only (interleave index -> index) where it's not reserved or hamming bit"""
    DEINTERLEAVE_5BIT_CHECKSUM: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (k, v[0])
                for k, v in INTERLEAVING_INDICES.items()
                if not v[3]
                and v[4]
                and v[1] != 8  # not reserved or hamming bits or row 8 (parity bits)
            ).values()
        )
    )
    """Extract only (interleave index -> index) where 5-bit checksum"""
    INTERLEAVE_INFO_BITS_ONLY_MAP: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (v[0], k)
                for k, v in INTERLEAVING_INDICES.items()
                if not v[3]
                and not v[4]
                and v[1] != 8  # not reserved or hamming bits or row 8 (parity bits)
            ).values()
        )
    )
    """Extract only (index -> interleave index) where it's not reserved or hamming bit"""

    @staticmethod
    def deinterleave_all_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 128 bits of deinterleaved bits
        :param bits:
        :return:
        """
        assert (
            len(bits) == 128
        ), f"BPTC 128,72 deinterleave_all_bits requires 128 bits, got {len(bits)}"
        mapping = VBPTC12873.FULL_DEINTERLEAVING_MAP

        out = bitarray([0] * len(mapping), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def deinterleave_data_bits(bits: bitarray, include_cs5: bool = True) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 72 or 77 bits of data
        :param bits: 128 bits of on-air payload
        :param include_cs5:
        :return: 72 or 77 bits of data (info bits)
        """
        assert (
            len(bits) == 128
        ), f"BPTC 128,72 decode requires 128 bits, got {len(bits)}"
        mapping = VBPTC12873.DEINTERLEAVE_INFO_BITS_ONLY_MAP

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        if include_cs5:
            out.extend(VBPTC12873.deinterleave_cs5_bits(bits))

        return out

    @staticmethod
    def deinterleave_cs5_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 5 bits of checksum for 72-bits of data
        :param bits: 128 bits of on-air payload
        :return: 5 bits of data (5-bit checksum)
        """
        assert (
            len(bits) == 128
        ), f"BPTC 128,72 decode requires 128 bits, got {len(bits)}"
        mapping = VBPTC12873.DEINTERLEAVE_5BIT_CHECKSUM

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def make_encoding_table() -> numpy.ndarray:
        # create table 8 rows, 16 columns, for FEC encoding
        table: numpy.ndarray = numpy.ndarray(shape=(8, 16), dtype=int)
        table.fill(0)

        return table

    @staticmethod
    def fill_encoding_table(
        table: numpy.ndarray, bits_deinterleaved: bitarray
    ) -> numpy.ndarray:
        assert (
            len(bits_deinterleaved) == 72 or len(bits_deinterleaved) == 128
        ), f"Can fill encoding table only with data bits (len 72) or full bits (len 128), got {len(bits_deinterleaved)}"

        # make bitarray of size 128, fill with provided bits
        mapping = (
            VBPTC12873.DEINTERLEAVE_INFO_BITS_ONLY_MAP
            if len(bits_deinterleaved) == 72
            else VBPTC12873.FULL_DEINTERLEAVING_MAP
        )
        bits_interleaved: bitarray = bitarray([0] * 128, endian="big")

        for index, interleave_index in mapping.items():
            bits_interleaved[interleave_index] = bits_deinterleaved[index]

        for data_index, (
            interleave_idx,
            row_no,
            col_no,
            is_hamming,
            is_cs5,
        ) in VBPTC12873.INTERLEAVING_INDICES.items():
            table[row_no - 1][col_no] = bits_interleaved[interleave_idx]

        return table

    @staticmethod
    def encode(bits_deinterleaved: bitarray) -> bitarray:
        """
        Takes 72 bits of data (info bits) and return interleaved and FEC protected 128 bits
        :param bits_deinterleaved:
        :return:
        """
        if len(bits_deinterleaved) == 77:
            # cut out cs5
            bits_deinterleaved = bits_deinterleaved[:72]
        elif len(bits_deinterleaved) == 128:
            # full deinterleaved data including cs5, hamming and parity
            # interleave again and deinterleave only data bits
            interleaved: bitarray = bitarray([0] * 128)
            for data_index, (
                interleave_index,
                _,
                _,
                _,
                _,
            ) in VBPTC12873.INTERLEAVING_INDICES.items():
                interleaved[data_index] = bits_deinterleaved[interleave_index]
            bits_deinterleaved = VBPTC12873.deinterleave_data_bits(
                interleaved, include_cs5=False
            )

        assert (
            len(bits_deinterleaved) == 72
        ), f"Unexpected number of bits fed to VBPTC12872.encode, expected 72, 77 or 128, got {len(bits_deinterleaved)}"

        table: numpy.ndarray = VBPTC12873.make_encoding_table()
        table = VBPTC12873.fill_encoding_table(
            table=table, bits_deinterleaved=bits_deinterleaved
        )

        # calculate 5-bit checksum and put bits in correct table positions
        cs5 = FiveBitChecksum.calculate(bits_deinterleaved.tobytes())
        cs5_bits = int2ba(cs5, length=5)
        table[2][10] = cs5_bits[4]
        table[3][10] = cs5_bits[3]
        table[4][10] = cs5_bits[2]
        table[5][10] = cs5_bits[1]
        table[6][10] = cs5_bits[0]

        # fill rows 0 - 6 with hamming
        for row in range(0, 7):
            table[row] = Hamming16114.generate(table[row][:11])

        # fill columns with parity bit
        for column in range(0, 16):
            table[:, column] = VBPTC12873.set_parity(table[:7, column])

        out: bitarray = bitarray([0] * 128)
        for index, info_tuple in VBPTC12873.INTERLEAVING_INDICES.items():
            out[info_tuple[0]] = table[info_tuple[1] - 1][info_tuple[2]]

        return out

    @staticmethod
    def set_parity(column: numpy.array) -> numpy.array:
        assert len(column) in (7, 8)
        if len(column) == 7:
            column = numpy.append(column, [0])
        column[7] = (
            column[0]
            ^ column[1]
            ^ column[2]
            ^ column[3]
            ^ column[4]
            ^ column[5]
            ^ column[6]
        )
        return column
