#!/usr/bin/env python3
# Strong-typed bitarray-based CRC
# Based on Nicola Coretti work here: https://github.com/Nicoretti/crc/blob/eb27ca85cae760f7727fedcb3644209fa5386116/crc.py

import abc
import enum
import functools
from dataclasses import dataclass
from typing import Union

from bitarray import bitarray
from bitarray.util import int2ba, ba2int


class AbstractBitCrcRegister(metaclass=abc.ABCMeta):
    """
    Abstract base class / Interface a crc register needs to implement.

    Workflow:
        1. The Crc-Register needs to be initialized.    1 time     (init)
        2. Data is feed into the crc register.          1..n times (update)
        3. Final result is calculated.                  1 time     (digest)
    """

    @abc.abstractmethod
    def init(self) -> None:
        """
        Initializes the crc register.
        """

    @abc.abstractmethod
    def update(self, data: bitarray) -> bitarray:
        """
        Feeds the provided data into the crc register.

        :param bitarray data: a bitarray source data object
        :return: the current value of the crc register.
        """

    @abc.abstractmethod
    def digest(self) -> bitarray:
        """
        Final crc checksum will be calculated.

        :return: the final crc checksum.
        :rtype: int.
        """

    @abc.abstractmethod
    def reverse(self) -> bitarray:
        """
        Calculates the reversed value of the crc register.

        :return: the the reversed value of the crc register.
        """


@dataclass(frozen=True)
class BitCrcConfiguration:
    """
    A Configuration provides all settings necessary to determine the concrete
    implementation of a specific crc algorithm/register.
    """

    width_bits: int
    polynomial: int
    init_value: int = 0
    final_xor_value: int = 0
    reverse_input_bytes: bool = False
    reverse_output_bytes: bool = False


class BitCrcRegisterBase(AbstractBitCrcRegister):
    """
    Implements the common crc algorithm, assuming a user of this base
    class will provide override for the _process_bits method.
    """

    def __init__(self, configuration: Union[BitCrcConfiguration, enum.Enum]):
        """
        Create a new BitCrcRegisterBase.

        :param configuration: used for the crc algorithm.
        """
        if isinstance(configuration, enum.Enum):
            configuration = configuration.value
        assert isinstance(
            configuration, BitCrcConfiguration
        ), f"BitCrcConfiguration not provided, got ${type(configuration)} instead"
        self._topbit: bitarray = bitarray([1]) + bitarray(
            [0] * (configuration.width_bits - 1)
        )
        # bitarray(123) creates bitarray of length 123 where those bits are UN-INITIALIZED, meaning, random data from memory
        self._bitmask: bitarray = int2ba(2 ** configuration.width_bits - 1)
        self._config: BitCrcConfiguration = configuration
        self._register: bitarray = (
            int2ba(configuration.init_value, length=configuration.width_bits)
            & self._bitmask
        )

    def __len__(self):
        """
        Returns the length (width) of the register.

        :return: the register size/width in bits.
        """
        return self._config.width_bits

    def __getitem__(self, index) -> bitarray:
        """
        Gets a single chunk of the register.

        :param index: index of first bit
        :return: number of bits (per configuration width)
        :raises IndexError: if the index is out of bounce.
        """
        if index >= self.register or index < 0:
            raise IndexError
        return self.register[index : index + self._config.width_bits]

    def init(self):
        """
        See AbstractCrcRegister.init
        """
        self.register = int2ba(self._config.init_value, length=self._config.width_bits)

    def update(self, bits: bitarray) -> bitarray:
        """
        See AbstractCrcRegister.update
        """
        if self._config.reverse_input_bytes:
            bits.bytereverse()

        for start_bit in range(0, len(bits), self._config.width_bits):
            self._process_bits(bits[start_bit : start_bit + self._config.width_bits])

        return self.register

    @abc.abstractmethod
    def _process_bits(self, bits: bitarray) -> bitarray:
        """
        Processes an entire bits feed to the crc register.

        :param bitarray bits: bits which shall be processed by the crc register.
        :return: the new value of the crc register will have after the bits have been processed.
        """

    def digest(self) -> bitarray:
        """
        See AbstractCrcRegister.digest
        """
        if self._config.reverse_output_bytes:
            self.reverse()
        return self.register ^ int2ba(
            self._config.final_xor_value, length=self._config.width_bits
        )

    def reverse(self) -> bitarray:
        """
        See AbstractCrcRegister.digest
        """
        # in place for some reason does not work
        rev = self.register.copy()
        rev.reverse()
        self.register = rev
        return self.register

    def _is_division_possible(self):
        return ba2int(self.register & self._topbit) > 0

    @property
    def register(self) -> bitarray:
        return self._register & self._bitmask

    @register.setter
    def register(self, value):
        self._register = value & self._bitmask


class BitCrcRegister(BitCrcRegisterBase):
    """
    Simple crc register, which will process one bitarray at the time.

    note: If performance is an important issue for the crc calculation use a table based register.
    """

    def _process_bits(self, bits: bitarray):
        """
        See BitCrcRegisterBase._process_bits
        """
        if len(bits) < 1:
            return self.register

        self.register = int2ba(
            ba2int(bits) ^ ba2int(self.register), length=self._config.width_bits
        )
        polynomial: bitarray = int2ba(
            self._config.polynomial, length=self._config.width_bits
        )
        for _ in bits:
            if self._is_division_possible():
                self.register = (self.register << 1) ^ polynomial
            else:
                self.register <<= 1
        return self.register


class TableBasedBitCrcRegister(BitCrcRegisterBase):
    """
    Lookup table based crc register.

    .. note::

        this register type will be much faster than a simple bit by bit based crc register.
        (e.g. CrcRegister)
    """

    def __init__(self, configuration: Union[BitCrcConfiguration, enum.Enum]):
        """
        Creates a new table based crc register.

        :param configuration: used for the crc algorithm.

        :attention: creating a table based register initially might take some extra time, due to the
                    fact that some lookup tables need to be calculated/initialized .
        """
        super().__init__(configuration)
        self._lookup_table = bits_create_lookup_table(
            self._config.width_bits, self._config.polynomial
        )

    def _process_bits(self, bits: bitarray):
        """
        See BitCrcRegisterBase._process_bits
        """
        if len(bits) != len(self.register):
            print("correct", bits, ba2int(bits))
            bits = int2ba(ba2int(bits), length=len(self.register))
            print("correct", bits, ba2int(bits))

        self.register = self._lookup_table[ba2int(bits ^ self.register)] ^ (
            self.register << self._config.width_bits
        )
        return self.register


@functools.lru_cache()
def bits_create_lookup_table(width_bits: int, polynomial: int):
    """
    Creates a crc lookup table.

    :param int width_bits: of the crc checksum.
    :param int polynomial: polynomial without top-bit
    :parma int polynomial: which is used for the crc calculation.
    """
    config = BitCrcConfiguration(width_bits=width_bits, polynomial=polynomial)
    crc_register = BitCrcRegister(config)
    lookup_table = []
    for index in range(0, 1 << width_bits):
        crc_register.init()
        data = int2ba(index, length=width_bits)
        crc_register.update(data)
        lookup_table.append(crc_register.digest())
    return lookup_table


class BitCrcCalculator:
    def __init__(
        self,
        configuration: Union[BitCrcConfiguration, enum.Enum],
        table_based: bool = False,
    ):
        """
        Creates a new CrcCalculator.

        :param configuration: for the crc algorithm.
        :param table_based: if true a tables based register will be used for the calculations.

        :attention: initializing a table based calculator might take some extra time, due to the
                    fact that the lookup table need to be initialized.
        """
        if table_based:
            self._crc_register = TableBasedBitCrcRegister(configuration)
        else:
            self._crc_register = BitCrcRegister(configuration)

    def calculate_checksum(self, data: bitarray) -> bitarray:
        self._crc_register.init()
        self._crc_register.update(data)
        return self._crc_register.digest()

    def verify_checksum(self, data: bitarray, expected_checksum: int) -> bool:
        return ba2int(self.calculate_checksum(data)) == expected_checksum


@enum.unique
class Crc9(enum.Enum):
    ETSI_DMR = BitCrcConfiguration(
        width_bits=9,
        polynomial=0x059,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input_bytes=False,
        reverse_output_bytes=False,
    )
