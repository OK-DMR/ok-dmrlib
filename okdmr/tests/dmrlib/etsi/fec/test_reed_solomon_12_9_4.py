from typing import Dict

from okdmr.dmrlib.etsi.fec.reed_solomon_12_9_4 import ReedSolomon1294
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks


def test_rs1294():
    hex_payloads: Dict[str, CrcMasks] = {
        "0300002635a903d475cb8795": CrcMasks.VoiceLCHeader,
        "03000003d4752635a96fed09": CrcMasks.VoiceLCHeader,
        "03000003d4752635a960e206": CrcMasks.TerminatorWithLC,
        "0300002635a903d475c4889a": CrcMasks.TerminatorWithLC,
    }
    for hex_payload, mask in hex_payloads.items():
        assert ReedSolomon1294.check(
            bytes.fromhex(hex_payload), mask.value.to_bytes(3, byteorder="big")
        )


def test_rs1294_multiply():
    assert 0 == ReedSolomon1294.log_multiply(0, 0)
    assert 0 == ReedSolomon1294.log_multiply(0, 1)
    assert 0 == ReedSolomon1294.log_multiply(1, 0)
