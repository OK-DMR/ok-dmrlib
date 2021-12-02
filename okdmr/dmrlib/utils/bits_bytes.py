from bitarray import bitarray


def bytes_to_bits(payload: bytes) -> bitarray:
    out: bitarray = bitarray()
    out.frombytes(payload)
    return out


def bits_to_bytes(bits: bitarray) -> bytes:
    return bits.tobytes()
