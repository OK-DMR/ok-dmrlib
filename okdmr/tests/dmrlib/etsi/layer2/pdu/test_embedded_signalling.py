from typing import List

from bitarray import bitarray
from okdmr.dmrlib.etsi.layer2.pdu.embedded_signalling import EmbeddedSignalling


def test_embedded_signalling():
    bursts: List[str] = [
        "0001001110010001",
        "0001011101110100",
        "0001011101110100",
        "0001010100000111",
        "0001000111100010",
        "0001011101110100",
    ]
    for burst in bursts:
        e: EmbeddedSignalling = EmbeddedSignalling.from_bits(bitarray(burst))
        assert e.emb_parity_ok
        assert (
            e.emb_parity
            == EmbeddedSignalling.from_bits(bitarray(burst[:7] + ("0" * 9))).emb_parity
        )
