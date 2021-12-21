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
    # add padding, that will get removed, to have odd number of bytes
    if len(data) % 2 != 0:
        last = bytes([data[-1]])
        data = data[0:-1]
    data[0::2], data[1::2] = data[1::2], data[0::2]
    return bytes(data[:trim]) + last
