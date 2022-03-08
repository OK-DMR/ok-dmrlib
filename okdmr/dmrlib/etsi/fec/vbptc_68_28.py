from typing import Dict, Tuple

import numpy
from bitarray import bitarray
from bitarray.util import int2ba

from okdmr.dmrlib.etsi.crc.crc8 import CRC8
from okdmr.dmrlib.etsi.fec.hamming_17_12_3 import Hamming17123


class VBPTC6828:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.2.3 Variable length BPTC for CACH signalling

    Full size of embedded signalling LC is 68 bits, providing 28 bits of LC information, 8 bits of 8-bit checksum (per B.3.7),
    rest (32 bits) are row hammings (3 rows, each 5 hamming bits, total 15 bits) and column parity check bits (17 bits)
    """

    # disable formatter for this whole table, as manual formatting is applied
    # fmt: off
    # @formatter:off
    INTERLEAVING_INDICES: Dict[int, Tuple[int, int, int, bool, bool]] = {
        # (key) index => (value) interleave index, row, column, is row hamming, is 8-bit checksum
        # rows are numbered from 1 to match the documentation/specification

        # Row 1 of table, starts with LC(27)
        0: (0, 1, 0, False, False),
        1: (4, 1, 1, False, False),
        2: (8, 1, 2, False, False),
        3: (12, 1, 3, False, False),
        4: (16, 1, 4, False, False),
        5: (20, 1, 5, False, False),
        6: (24, 1, 6, False, False),
        7: (28, 1, 7, False, False),
        8: (32, 1, 8, False, False),
        9: (36, 1, 9, False, False),
        10: (40, 1, 10, False, False),
        11: (44, 1, 11, False, False),
        # Row 1 hamming bits, starts with H1(4)
        12: (48, 1, 12, True, False),
        13: (52, 1, 13, True, False),
        14: (56, 1, 14, True, False),
        15: (60, 1, 15, True, False),
        16: (64, 1, 16, True, False),

        # Row 2 of table, starts with LC(15)
        17: (1, 2, 0, False, False),
        18: (5, 2, 1, False, False),
        19: (9, 2, 2, False, False),
        20: (13, 2, 3, False, False),
        21: (17, 2, 4, False, False),
        22: (21, 2, 5, False, False),
        23: (25, 2, 6, False, False),
        24: (29, 2, 7, False, False),
        25: (33, 2, 8, False, False),
        26: (37, 2, 9, False, False),
        27: (41, 2, 10, False, False),
        28: (45, 2, 11, False, False),
        # Row 2 hamming bits, starts with H2(4)
        29: (49, 2, 12, True, False),
        30: (53, 2, 13, True, False),
        31: (57, 2, 14, True, False),
        32: (61, 2, 15, True, False),
        33: (65, 2, 16, True, False),

        # Row 3 of table, starts with LC(3)
        34: (2, 3, 0, False, False),
        35: (6, 3, 1, False, False),
        36: (10, 3, 2, False, False),
        37: (14, 3, 3, False, False),
        # 8-bit checksum, starts with CR(7)
        38: (18, 3, 4, False, True),
        39: (22, 3, 5, False, True),
        40: (26, 3, 6, False, True),
        41: (30, 3, 7, False, True),
        42: (34, 3, 8, False, True),
        43: (38, 3, 9, False, True),
        44: (42, 3, 10, False, True),
        45: (46, 3, 11, False, True),
        # Row 3 hamming bits, starts with H3(4)
        46: (50, 3, 12, True, False),
        47: (54, 3, 13, True, False),
        48: (58, 3, 14, True, False),
        49: (62, 3, 15, True, False),
        50: (66, 3, 16, True, False),

        # Row 4 of table, starts with PC(16)
        51: (3, 4, 0, False, False),
        52: (7, 4, 1, False, False),
        53: (11, 4, 2, False, False),
        54: (15, 4, 3, False, False),
        55: (19, 4, 4, False, False),
        56: (23, 4, 5, False, False),
        57: (27, 4, 6, False, False),
        58: (31, 4, 7, False, False),
        59: (35, 4, 8, False, False),
        60: (39, 4, 9, False, False),
        61: (43, 4, 10, False, False),
        62: (47, 4, 11, False, False),
        63: (51, 4, 12, False, False),
        64: (55, 4, 13, False, False),
        65: (59, 4, 14, False, False),
        66: (63, 4, 15, False, False),
        67: (67, 4, 16, False, False),
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
                (idx, interleave_idx)
                for idx, (
                    interleave_idx,
                    row,
                    col,
                    is_hamming,
                    is_crc,
                ) in INTERLEAVING_INDICES.items()
                if not is_hamming and not is_crc and row != 4  # not parity bits / row 4
            ).values()
        )
    )
    """Extract only (interleave index -> index) where it's not reserved or hamming bit"""
    DEINTERLEAVE_8BIT_CHECKSUM: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (idx, interleave_idx)
                for idx, (
                    interleave_idx,
                    row,
                    col,
                    is_hamming,
                    is_crc,
                ) in INTERLEAVING_INDICES.items()
                if not is_hamming and is_crc and row != 4  # not parity bits / row 4
            ).values()
        )
    )
    """Extract only (interleave index -> index) where 8-bit checksum"""
    INTERLEAVE_INFO_BITS_ONLY_MAP: Dict[int, int] = dict(
        (i, l)
        for i, l in enumerate(
            dict(
                (interleave_idx, idx)
                for idx, (
                    interleave_idx,
                    row,
                    col,
                    is_hamming,
                    is_crc,
                ) in INTERLEAVING_INDICES.items()
                if not is_hamming
                and not is_crc
                and row != 4  # not reserved or hamming bits or row 8 (parity bits)
            ).values()
        )
    )
    """Extract only (index -> interleave index) where it's not reserved or hamming bit"""

    @staticmethod
    def deinterleave_all_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 68 bits of deinterleaved bits
        :param bits:
        :return:
        """
        assert (
            len(bits) == 68
        ), f"VBPTC 68,28 deinterleave_all_bits requires 68 bits, got {len(bits)}"
        mapping = VBPTC6828.FULL_DEINTERLEAVING_MAP

        out = bitarray([0] * len(mapping), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def deinterleave_data_bits(bits: bitarray, include_crc8: bool = True) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 28 or 36 bits of data
        :param bits: 68 bits of on-air payload
        :param include_crc8:
        :return: bitarray with 28 (data bits) or 36 (data+crc, aka. info bits)
        """
        assert len(bits) == 68, f"VBPTC 68,28 decode requires 68 bits, got {len(bits)}"
        mapping = VBPTC6828.DEINTERLEAVE_INFO_BITS_ONLY_MAP

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        if include_crc8:
            out.extend(VBPTC6828.deinterleave_crc8_bits(bits))

        return out

    @staticmethod
    def deinterleave_crc8_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 8 bits of checksum for 28-bits of data
        :param bits: 68 bits of on-air payload
        :return: 8 bits of data (CRC-8)
        """
        assert len(bits) == 68, f"VBPTC 68,28 decode requires 68 bits, got {len(bits)}"
        mapping = VBPTC6828.DEINTERLEAVE_8BIT_CHECKSUM

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        out.bytereverse()

        return out

    @staticmethod
    def make_encoding_table() -> numpy.ndarray:
        # create table 4 rows, 17 columns, for FEC encoding
        table: numpy.ndarray = numpy.ndarray(shape=(4, 17), dtype=int)
        table.fill(0)

        return table

    @staticmethod
    def fill_encoding_table(
        table: numpy.ndarray, bits_deinterleaved: bitarray
    ) -> numpy.ndarray:
        assert (
            len(bits_deinterleaved) == 28 or len(bits_deinterleaved) == 68
        ), f"Can fill encoding table only with data bits (len 28) or full bits (len 68), got {len(bits_deinterleaved)}"

        # make bitarray of size 68, fill with provided bits
        mapping = (
            VBPTC6828.DEINTERLEAVE_INFO_BITS_ONLY_MAP
            if len(bits_deinterleaved) == 28
            else VBPTC6828.FULL_DEINTERLEAVING_MAP
        )
        bits_interleaved: bitarray = bitarray([0] * 68, endian="big")

        for index, interleave_index in mapping.items():
            bits_interleaved[interleave_index] = bits_deinterleaved[index]

        for data_index, (
            interleave_idx,
            row_no,
            col_no,
            is_hamming,
            is_crc8,
        ) in VBPTC6828.INTERLEAVING_INDICES.items():
            table[row_no - 1][col_no] = bits_interleaved[interleave_idx]

        return table

    @staticmethod
    def encode(bits_deinterleaved: bitarray) -> bitarray:
        """
        Takes 28 bits of data (info bits) and return interleaved and FEC protected 68 bits
        :param bits_deinterleaved:
        :return:
        """
        if len(bits_deinterleaved) == 36:
            # cut out crc8
            cut_crc8 = bits_deinterleaved[28:]
            bits_deinterleaved = bits_deinterleaved[:28]
        elif len(bits_deinterleaved) == 68:
            # full deinterleaved data including crc8, hamming and parity
            # interleave again and deinterleave only data bits
            interleaved: bitarray = bitarray([0] * 68)
            for data_index, (
                interleave_index,
                _,
                _,
                _,
                _,
            ) in VBPTC6828.INTERLEAVING_INDICES.items():
                interleaved[data_index] = bits_deinterleaved[interleave_index]
            bits_deinterleaved = VBPTC6828.deinterleave_data_bits(
                interleaved, include_crc8=False
            )

        assert (
            len(bits_deinterleaved) == 28
        ), f"Unexpected number of bits fed to VBPTC6828.encode, expected 28, 36 or 68, got {len(bits_deinterleaved)}"

        table: numpy.ndarray = VBPTC6828.make_encoding_table()
        table = VBPTC6828.fill_encoding_table(
            table=table, bits_deinterleaved=bits_deinterleaved
        )
        # calculate 8-bit checksum and put bits in correct table positions
        crc8 = CRC8.calculate(bits_deinterleaved)
        crc8_bits = int2ba(crc8, length=8)
        table[2][4] = crc8_bits[0]
        table[2][5] = crc8_bits[1]
        table[2][6] = crc8_bits[2]
        table[2][7] = crc8_bits[3]
        table[2][8] = crc8_bits[4]
        table[2][9] = crc8_bits[5]
        table[2][10] = crc8_bits[6]
        table[2][11] = crc8_bits[7]

        # fill rows 0 - 2 with hamming
        for row in range(0, 3):
            table[row] = Hamming17123.generate(table[row][:12])

        # fill columns with parity bit
        for column in range(0, 17):
            table[:, column] = VBPTC6828.set_parity(table[:3, column])

        out: bitarray = bitarray([0] * 68)
        for index, (
            interleave_index,
            row,
            col,
            is_hamming,
            is_crc,
        ) in VBPTC6828.INTERLEAVING_INDICES.items():
            out[interleave_index] = table[row - 1][col]

        return out

    @staticmethod
    def set_parity(column: numpy.ndarray) -> numpy.ndarray:
        assert len(column) in (3, 4)
        if len(column) == 3:
            column = numpy.append(column, [0])
        column[3] = column[0] ^ column[1] ^ column[2]
        return column
