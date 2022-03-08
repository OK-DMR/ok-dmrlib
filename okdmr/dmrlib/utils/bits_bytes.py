from typing import Union

import numpy
from bitarray import bitarray


def bytes_to_bits(payload: bytes, endian: str = "big") -> bitarray:
    """
    Convert from bytes to bitarray
    :param payload:
    :param endian:
    :return:
    """
    out: bitarray = bitarray(endian=endian)
    out.frombytes(payload)
    return out


def bits_to_bytes(bits: bitarray) -> bytes:
    """
    Convert from bitarray to bytes
    :param bits:
    :return:
    """
    return bits.tobytes()


def byteswap_bytes(data: bytes) -> bytes:
    """
    Swap bytes (endiannes)
    :param data:
    :return:
    """
    return byteswap_bytearray(bytearray(data))


def byteswap_bytearray(data: bytearray) -> bytes:
    """
    Swap bytearray (endiannes)
    :param data:
    :return:
    """
    trim = len(data)
    last: bytes = bytes()
    # add padding, that will get removed, to not have odd number of bytes
    if len(data) % 2 != 0:
        last = bytes([data[-1]])
        data = data[0:-1]
    data[0::2], data[1::2] = data[1::2], data[0::2]
    return bytes(data[:trim]) + last


def numpy_array_to_int(data: Union[numpy.array, numpy.ndarray]) -> int:
    return int(data.dot(2 ** numpy.arange(data.size)[::-1]))


def numpy_array_to_bitarray(data: Union[numpy.ndarray, numpy.array]) -> bitarray:
    """
    This method can process only single dimensional numpy array
    :param data:
    :return:
    """
    if len(data.shape) > 1:
        raise ValueError(
            f"numpy_array_to_bitarray cannot convert array of more than 1 dimension, got shape {data.shape}"
        )
    values = data.tolist()
    assert isinstance(
        values, list
    ), f"Unexpected result of numpy.(nd)array.tolist, got type: {type(values)}, values: {values}"
    return bitarray(values) if isinstance(values, list) else bitarray()


def bitarray_to_numpy_array(bits: bitarray) -> numpy.ndarray:
    """
    Will return numpy array as bitarray
    :param bits:
    :return:
    """
    return numpy.array(bits.tolist())
