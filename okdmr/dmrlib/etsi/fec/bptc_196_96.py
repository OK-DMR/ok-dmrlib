from typing import Dict, Tuple

import numpy
from bitarray import bitarray

from okdmr.dmrlib.etsi.fec.hamming_13_9_3 import Hamming1393
from okdmr.dmrlib.etsi.fec.hamming_15_11_3 import Hamming15113


class BPTC19696:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B1.1.1  BPTC 196,96
    """

    # disable formatter for this whole table, as manual formatting is applied
    # fmt: off
    # @formatter:off
    INTERLEAVING_INDICES: Dict[int, Tuple[int, int, int, bool, bool]] = {
        # (key) index => (value) interleave index, row, column, is reserved, is hamming
        # rows are numbered from 1 to match the documentation/specification
        0: (0,    0, 0,  True,  False),  # R(3) is padding not assigned place in encoding/decoding table

        # row 1, starts with R(2)
        1: (181,  1, 0,  True,  False),
        2: (166,  1, 1,  True,  False),
        3: (151,  1, 2,  True,  False),
        # I(95) first info bit
        4: (136,  1, 3,  False, False),
        5: (121,  1, 4,  False, False),
        6: (106,  1, 5,  False, False),
        7: (91,   1, 6,  False, False),
        8: (76,   1, 7,  False, False),
        9: (61,   1, 8,  False, False),
        10: (46,  1, 9,  False, False),
        11: (31,  1, 10, False, False),
        # row 1 hamming
        12: (16,  1, 11, False, True),
        13: (1,   1, 12, False, True),
        14: (182, 1, 13, False, True),
        15: (167, 1, 14, False, True),

        # row 2, starts with I(87)
        16: (152, 2, 0,  False, False),
        17: (137, 2, 1,  False, False),
        18: (122, 2, 2,  False, False),
        19: (107, 2, 3,  False, False),
        20: (92,  2, 4,  False, False),
        21: (77,  2, 5,  False, False),
        22: (62,  2, 6,  False, False),
        23: (47,  2, 7,  False, False),
        24: (32,  2, 8,  False, False),
        25: (17,  2, 9,  False, False),
        26: (2,   2, 10, False, False),
        # row 2 hamming
        27: (183, 2, 11, False, True),
        28: (168, 2, 12, False, True),
        29: (153, 2, 13, False, True),
        30: (138, 2, 14, False, True),

        # row 3
        31: (123, 3, 0,  False, False),
        32: (108, 3, 1,  False, False),
        33: (93,  3, 2,  False, False),
        34: (78,  3, 3,  False, False),
        35: (63,  3, 4,  False, False),
        36: (48,  3, 5,  False, False),
        37: (33,  3, 6,  False, False),
        38: (18,  3, 7,  False, False),
        39: (3,   3, 8,  False, False),
        40: (184, 3, 9,  False, False),
        41: (169, 3, 10, False, False),
        # row 3 hamming
        42: (154, 3, 11, False, True),
        43: (139, 3, 12, False, True),
        44: (124, 3, 13, False, True),
        45: (109, 3, 14, False, True),

        # row 4
        46: (94,  4, 0,  False, False),
        47: (79,  4, 1,  False, False),
        48: (64,  4, 2,  False, False),
        49: (49,  4, 3,  False, False),
        50: (34,  4, 4,  False, False),
        51: (19,  4, 5,  False, False),
        52: (4,   4, 6,  False, False),
        53: (185, 4, 7,  False, False),
        54: (170, 4, 8,  False, False),
        55: (155, 4, 9,  False, False),
        56: (140, 4, 10, False, False),
        # row 4 hamming
        57: (125, 4, 11, False, True),
        58: (110, 4, 12, False, True),
        59: (95,  4, 13, False, True),
        60: (80,  4, 14, False, True),

        # row 5
        61: (65,  5, 0,  False, False),
        62: (50,  5, 1,  False, False),
        63: (35,  5, 2,  False, False),
        64: (20,  5, 3,  False, False),
        65: (5,   5, 4,  False, False),
        66: (186, 5, 5,  False, False),
        67: (171, 5, 6,  False, False),
        68: (156, 5, 7,  False, False),
        69: (141, 5, 8,  False, False),
        70: (126, 5, 9,  False, False),
        71: (111, 5, 10, False, False),
        # row 5 hamming
        72: (96,  5, 11, False, True),
        73: (81,  5, 12, False, True),
        74: (66,  5, 13, False, True),
        75: (51,  5, 14, False, True),

        # row 6
        76: (36,  6, 0,  False, False),
        77: (21,  6, 1,  False, False),
        78: (6,   6, 2,  False, False),
        79: (187, 6, 3,  False, False),
        80: (172, 6, 4,  False, False),
        81: (157, 6, 5,  False, False),
        82: (142, 6, 6,  False, False),
        83: (127, 6, 7,  False, False),
        84: (112, 6, 8,  False, False),
        85: (97,  6, 9,  False, False),
        86: (82,  6, 10, False, False),
        # row 6 hamming
        87: (67,  6, 11, False, True),
        88: (52,  6, 12, False, True),
        89: (37,  6, 13, False, True),
        90: (22,  6, 14, False, True),

        # row 7
        91:  (7,   7, 0,  False, False),
        92:  (188, 7, 1,  False, False),
        93:  (173, 7, 2,  False, False),
        94:  (158, 7, 3,  False, False),
        95:  (143, 7, 4,  False, False),
        96:  (128, 7, 5,  False, False),
        97:  (113, 7, 6,  False, False),
        98:  (98,  7, 7,  False, False),
        99:  (83,  7, 8,  False, False),
        100: (68,  7, 9,  False, False),
        101: (53,  7, 10, False, False),
        # row 7 hamming
        102: (38,  7, 11, False, True),
        103: (23,  7, 12, False, True),
        104: (8,   7, 13, False, True),
        105: (189, 7, 14, False, True),

        # row 8
        106: (174, 8, 0,  False, False),
        107: (159, 8, 1,  False, False),
        108: (144, 8, 2,  False, False),
        109: (129, 8, 3,  False, False),
        110: (114, 8, 4,  False, False),
        111: (99,  8, 5,  False, False),
        112: (84,  8, 6,  False, False),
        113: (69,  8, 7,  False, False),
        114: (54,  8, 8,  False, False),
        115: (39,  8, 9,  False, False),
        116: (24,  8, 10, False, False),
        # row 8 hamming
        117: (9,   8, 11, False, True),
        118: (190, 8, 12, False, True),
        119: (175, 8, 13, False, True),
        120: (160, 8, 14, False, True),

        # row 9
        121: (145, 9, 0,  False, False),
        122: (130, 9, 1,  False, False),
        123: (115, 9, 2,  False, False),
        124: (100, 9, 3,  False, False),
        125: (85,  9, 4,  False, False),
        126: (70,  9, 5,  False, False),
        127: (55,  9, 6,  False, False),
        128: (40,  9, 7,  False, False),
        129: (25,  9, 8,  False, False),
        130: (10,  9, 9,  False, False),
        131: (191, 9, 10, False, False),
        # row 9 hamming
        132: (176, 9, 11, False, True),
        133: (161, 9, 12, False, True),
        134: (146, 9, 13, False, True),
        135: (131, 9, 14, False, True),

        # start of column hamming values, no data/info bits further on
        136: (116, 10, 0,  False, True),  # H_C1
        137: (101, 10, 1,  False, True),  # H_C2
        138: (86,  10, 2,  False, True),  # H_C3
        139: (71,  10, 3,  False, True),  # H_C4
        140: (56,  10, 4,  False, True),  # H_C5
        141: (41,  10, 5,  False, True),  # H_C6
        142: (26,  10, 6,  False, True),  # H_C7
        143: (11,  10, 7,  False, True),  # H_C8
        144: (192, 10, 8,  False, True),  # H_C9
        145: (177, 10, 9,  False, True),  # H_C10
        146: (162, 10, 10, False, True),  # H_C11
        147: (147, 10, 11, False, True),  # H_C12
        148: (132, 10, 12, False, True),  # H_C13
        149: (117, 10, 13, False, True),  # H_C14
        150: (102, 10, 14, False, True),  # H_C15

        151: (87,  11, 0,  False, True),  # H_C1
        152: (72,  11, 1,  False, True),  # H_C2
        153: (57,  11, 2,  False, True),  # H_C3
        154: (42,  11, 3,  False, True),  # H_C4
        155: (27,  11, 4,  False, True),  # H_C5
        156: (12,  11, 5,  False, True),  # H_C6
        157: (193, 11, 6,  False, True),  # H_C7
        158: (178, 11, 7,  False, True),  # H_C8
        159: (163, 11, 8,  False, True),  # H_C9
        160: (148, 11, 9,  False, True),  # H_C10
        161: (133, 11, 10, False, True),  # H_C11
        162: (118, 11, 11, False, True),  # H_C12
        163: (103, 11, 12, False, True),  # H_C13
        164: (88,  11, 13, False, True),  # H_C14
        165: (73,  11, 14, False, True),  # H_C15

        166: (58,  12, 0,  False, True),  # H_C1
        167: (43,  12, 1,  False, True),  # H_C2
        168: (28,  12, 2,  False, True),  # H_C3
        169: (13,  12, 3,  False, True),  # H_C4
        170: (194, 12, 4,  False, True),  # H_C5
        171: (179, 12, 5,  False, True),  # H_C6
        172: (164, 12, 6,  False, True),  # H_C7
        173: (149, 12, 7,  False, True),  # H_C8
        174: (134, 12, 8,  False, True),  # H_C9
        175: (119, 12, 9,  False, True),  # H_C10
        176: (104, 12, 10, False, True),  # H_C11
        177: (89,  12, 11, False, True),  # H_C12
        178: (74,  12, 12, False, True),  # H_C13
        179: (59,  12, 13, False, True),  # H_C14
        180: (44,  12, 14, False, True),  # H_C15

        181: (29,  13, 0,  False, True),  # H_C1
        182: (14,  13, 1,  False, True),  # H_C2
        183: (195, 13, 2,  False, True),  # H_C3
        184: (180, 13, 3,  False, True),  # H_C4
        185: (165, 13, 4,  False, True),  # H_C5
        186: (150, 13, 5,  False, True),  # H_C6
        187: (135, 13, 6,  False, True),  # H_C7
        188: (120, 13, 7,  False, True),  # H_C8
        189: (105, 13, 8,  False, True),  # H_C9
        190: (90,  13, 9,  False, True),  # H_C10
        191: (75,  13, 10, False, True),  # H_C11
        192: (60,  13, 11, False, True),  # H_C12
        193: (45,  13, 12, False, True),  # H_C13
        194: (30,  13, 13, False, True),  # H_C14
        195: (15,  13, 14, False, True),  # H_C15
    }
    """Interleave table as key(index) => value(interleave index, row, column, is reserved, is hamming)"""
    # @formatter:on
    # fmt: on

    FULL_INTERLEAVING_MAP: Dict[int, int] = dict(
        (k, v[0]) for k, v in INTERLEAVING_INDICES.items()
    )
    """Extract only (index -> interleave index)"""
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
                if not v[3] and not v[4]  # not reserved or hamming bits
            ).values()
        )
    )
    """Extract only (interleave index -> index) where it's not reserved or hamming bit"""
    INTERLEAVE_INFO_BITS_ONLY_MAP: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (v[0], k)
                for k, v in INTERLEAVING_INDICES.items()
                if not v[3] and not v[4]  # not reserved or hamming bits
            ).values()
        )
    )
    """Extract only (index -> interleave index) where it's not reserved or hamming bit"""

    @staticmethod
    def deinterleave_all_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 196 bits of deinterleaved bits
        :param bits:
        :return:
        """
        assert (
            len(bits) == 196
        ), f"BPTC 196,96 deinterleave_all_bits requires 196 bits, got {len(bits)}"
        mapping = BPTC19696.FULL_DEINTERLEAVING_MAP

        out = bitarray([0] * len(mapping), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def deinterleave_data_bits(
        bits: bitarray, repair_if_necessary: bool = True
    ) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 96 bits of data
        :param repair_if_necessary:
        :param bits: 196 bits of on-air payload
        :return: 96 bits of data (info bits)
        """
        assert (
            len(bits) == 196
        ), f"BPTC 196,96 decode requires 196 bits, got {len(bits)}"
        mapping = BPTC19696.DEINTERLEAVE_INFO_BITS_ONLY_MAP

        if repair_if_necessary:
            bits = BPTC19696.repair_if_necessary(bits=bits)

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def repair_if_necessary(bits: bitarray, deinterleaved: bool = False) -> bitarray:
        """
        Takes all 196 of interleaved or deinterleaved BPT 196.96 payload and will perform Hamming corrections
        if necessary

        :param bits:
        :param deinterleaved:
        :return:
        """
        assert (
            len(bits) == 196
        ), f"BPTC 196,96 can repair only full 196 bits, got {len(bits)}"

        if not deinterleaved:
            bits = BPTC19696.deinterleave_all_bits(bits)

        table = BPTC19696.make_encoding_table()
        table = BPTC19696.fill_encoding_table(table, bits)

        for row in range(0, table.shape[0]):
            table[row] = Hamming15113.correct_numpy_array(table[row])
            for col in range(0, table.shape[1]):
                table[:, col] = Hamming1393.correct_numpy_array(table[:, col])

        for data_index, (
            interleave_index,
            row,
            column,
            is_reserved,
            is_hamming,
        ) in BPTC19696.INTERLEAVING_INDICES.items():
            bits[data_index if deinterleaved else interleave_index] = table[row - 1][
                column
            ]

        return bits

    @staticmethod
    def make_encoding_table() -> numpy.ndarray:
        # create table 13 rows, 15 columns, for FEC encoding
        table: numpy.ndarray = numpy.ndarray(shape=(13, 15), dtype=int)
        table.fill(0)

        return table

    @staticmethod
    def fill_encoding_table(
        table: numpy.ndarray, bits_deinterleaved: bitarray
    ) -> numpy.ndarray:
        assert (
            len(bits_deinterleaved) == 96 or len(bits_deinterleaved) == 196
        ), f"Can fill encoding table only with data bits (len 96) or full bits (len 196), got {len(bits_deinterleaved)}"

        # make bitarray of size 196, fill with provided bits
        mapping = (
            BPTC19696.DEINTERLEAVE_INFO_BITS_ONLY_MAP
            if len(bits_deinterleaved) == 96
            else BPTC19696.FULL_DEINTERLEAVING_MAP
        )
        bits_interleaved: bitarray = bitarray([0] * 196, endian="big")

        for index, interleave_index in mapping.items():
            bits_interleaved[interleave_index] = bits_deinterleaved[index]

        for data_index, info_tuple in BPTC19696.INTERLEAVING_INDICES.items():
            # info_tuple structure: interleave index, row (numbered from 1), column (numbered from 0), is reserved, is hamming
            table[info_tuple[1] - 1][info_tuple[2]] = bits_interleaved[info_tuple[0]]

        return table

    @staticmethod
    def encode(bits_deinterleaved: bitarray) -> bitarray:
        """
        Takes 96 bits of data (info bits) and return interleaved and FEC protected 196 bits
        :param bits_deinterleaved:
        :return:
        """
        table: numpy.ndarray = BPTC19696.make_encoding_table()
        table = BPTC19696.fill_encoding_table(
            table=table, bits_deinterleaved=bits_deinterleaved
        )

        # fill rows with hamming
        for row in range(0, 13):
            table[row] = Hamming15113.generate(table[row][0:11])

        # fill columns with hamming
        for column in range(0, 15):
            table[:, column] = Hamming1393.generate(table[:, column][0:9])

        out: bitarray = bitarray([0] * 196)
        for index, (
            interleave_index,
            row,
            column,
            is_reserved,
            is_hamming,
        ) in BPTC19696.INTERLEAVING_INDICES.items():
            if is_reserved:
                continue
            out[interleave_index] = table[row - 1][column]

        return out
