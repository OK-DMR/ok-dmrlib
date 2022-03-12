from typing import Dict, Tuple

import numpy
from bitarray import bitarray
from okdmr.dmrlib.etsi.fec.hamming_16_11_4 import Hamming16114


class VBPTC3211:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.2.2  Single Burst Variable length BPTC
    """

    # disable formatter for this whole table, as manual formatting is applied
    # fmt: off
    # @formatter:off
    INTERLEAVING_INDICES: Dict[int, Tuple[int, int, int, bool, bool]] = {
        # (key) index => (value) interleave index, row, column, is row hamming, is parity check bit
        # rows are numbered from 1 to match the documentation/specification

        # Row 1 of table, starts with SB(10)/RC(10)
        0: (0, 1, 0, False, False),
        1: (2, 1, 1, False, False),
        2: (4, 1, 2, False, False),
        3: (6, 1, 3, False, False),
        4: (8, 1, 4, False, False),
        5: (10, 1, 5, False, False),
        6: (12, 1, 6, False, False),
        7: (14, 1, 7, False, False),
        8: (16, 1, 8, False, False),
        9: (18, 1, 9, False, False),
        10: (20, 1, 10, False, False),
        # Row 1 hamming bits, starts with H1(4)
        11: (22, 1, 11, True, False),
        12: (24, 1, 12, True, False),
        13: (26, 1, 13, True, False),
        14: (28, 1, 14, True, False),
        15: (30, 1, 15, True, False),

        # Row 4 of table, starts with PC(15)
        16: (17, 2, 0, False, True),
        17: (19, 2, 1, False, True),
        18: (21, 2, 2, False, True),
        19: (23, 2, 3, False, True),
        20: (25, 2, 4, False, True),
        21: (27, 2, 5, False, True),
        22: (29, 2, 6, False, True),
        23: (31, 2, 7, False, True),
        24: (1, 2, 8, False, True),
        25: (3, 2, 9, False, True),
        26: (5, 2, 10, False, True),
        27: (7, 2, 11, False, True),
        28: (9, 2, 12, False, True),
        29: (11, 2, 13, False, True),
        30: (13, 2, 14, False, True),
        31: (15, 2, 15, False, True),
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
                    is_parity,
                ) in INTERLEAVING_INDICES.items()
                if not is_hamming and not is_parity  # not parity bits or hamming
            ).values()
        )
    )
    """Extract only (interleave index -> index) where it's not reserved or hamming bit"""
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
                    is_parity,
                ) in INTERLEAVING_INDICES.items()
                if not is_hamming and not is_parity
            ).values()
        )
    )
    """Extract only (index -> interleave index) where it's not reserved or hamming bit"""

    @staticmethod
    def deinterleave_all_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 11 bits of deinterleaved bits
        :param bits: 32 bits of on-air payload
        :return:
        """
        assert (
            len(bits) == 32
        ), f"VBPTC 31,11 deinterleave_all_bits requires 32 bits, got {len(bits)}"
        mapping = VBPTC3211.FULL_DEINTERLEAVING_MAP

        out = bitarray([0] * len(mapping), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def deinterleave_data_bits(bits: bitarray) -> bitarray:
        """
        Will take BPTC interleaved (and FEC protected) bits and return 11bits of data
        :param bits: 32 bits of on-air payload
        :return: bitarray with 11 (data bits)
        """
        assert len(bits) == 32, f"VBPTC 32,11 decode requires 32 bits, got {len(bits)}"
        mapping = VBPTC3211.DEINTERLEAVE_INFO_BITS_ONLY_MAP

        out = bitarray([0] * len(mapping.keys()), endian="big")
        for i, n in mapping.items():
            out[i] = bits[n]

        return out

    @staticmethod
    def make_encoding_table() -> numpy.ndarray:
        # create table 4 rows, 17 columns, for FEC encoding
        table: numpy.ndarray = numpy.ndarray(shape=(2, 16), dtype=int)
        table.fill(0)

        return table

    @staticmethod
    def fill_encoding_table(
        table: numpy.ndarray, bits_deinterleaved: bitarray
    ) -> numpy.ndarray:
        assert (
            len(bits_deinterleaved) == 11 or len(bits_deinterleaved) == 32
        ), f"Can fill encoding table only with data bits (len 11) or full bits (len 32), got {len(bits_deinterleaved)}"

        # make bitarray of size 32, fill with provided bits
        mapping = (
            VBPTC3211.DEINTERLEAVE_INFO_BITS_ONLY_MAP
            if len(bits_deinterleaved) == 11
            else VBPTC3211.FULL_DEINTERLEAVING_MAP
        )
        bits_interleaved: bitarray = bitarray([0] * 32, endian="big")

        for index, interleave_index in mapping.items():
            bits_interleaved[interleave_index] = bits_deinterleaved[index]

        for data_index, (
            interleave_idx,
            row_no,
            col_no,
            is_hamming,
            is_parity,
        ) in VBPTC3211.INTERLEAVING_INDICES.items():
            table[row_no - 1][col_no] = bits_interleaved[interleave_idx]

        return table

    @staticmethod
    def encode(bits_deinterleaved: bitarray) -> bitarray:
        """
        Takes 11 bits of data (info bits) and return interleaved and FEC protected 32 bits
        :param bits_deinterleaved:
        :return:
        """
        if len(bits_deinterleaved) == 32:
            # full deinterleaved data including hamming and parity
            # interleave again and deinterleave only data bits
            interleaved: bitarray = bitarray([0] * 32)
            for data_index, (
                interleave_index,
                _,
                _,
                _,
                _,
            ) in VBPTC3211.INTERLEAVING_INDICES.items():
                interleaved[data_index] = bits_deinterleaved[interleave_index]
            bits_deinterleaved = VBPTC3211.deinterleave_data_bits(interleaved)

        assert (
            len(bits_deinterleaved) == 11
        ), f"Unexpected number of bits fed to VBPTC3211.encode, expected 11 or 32, got {len(bits_deinterleaved)}"

        table: numpy.ndarray = VBPTC3211.make_encoding_table()
        table = VBPTC3211.fill_encoding_table(
            table=table, bits_deinterleaved=bits_deinterleaved
        )

        # fill row 0 with hamming
        for row in range(0, 1):
            table[row] = Hamming16114.generate(table[row][:11])

        # fill columns with parity bit
        for column in range(0, 16):
            table[:, column] = VBPTC3211.set_parity(table[:, column])

        out: bitarray = bitarray([0] * 32)
        for index, (
            interleave_index,
            row,
            col,
            is_hamming,
            is_parity,
        ) in VBPTC3211.INTERLEAVING_INDICES.items():
            out[interleave_index] = table[row - 1][col]

        return out

    @staticmethod
    def set_parity(column: numpy.ndarray) -> numpy.ndarray:
        assert len(column) in (1, 2)
        if len(column) == 1:
            column = numpy.append(column, [0])
        column[1] = column[0]
        return column
