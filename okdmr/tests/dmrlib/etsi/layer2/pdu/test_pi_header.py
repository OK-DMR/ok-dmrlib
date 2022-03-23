from typing import List

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.pdu.pi_header import PIHeader
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_pi_header():
    hexpdus: List[str] = ["211002177afc730000090dda"]
    for hexpdu in hexpdus:
        pi_bytes: bytes = bytes.fromhex(hexpdu)
        pi_bits: bitarray = bytes_to_bits(pi_bytes)
        pi_header = PIHeader.from_bits(pi_bits)
        assert pi_header.crc_ok
        assert pi_header.as_bits() == pi_bits
        assert len(repr(pi_header))
