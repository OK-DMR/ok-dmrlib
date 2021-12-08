from typing import Dict, Tuple

from okdmr.dmrlib.etsi.crc.crc_masks import CrcMasks
from okdmr.dmrlib.etsi.fec.reed_solomon_12_9_4 import ReedSolomon1294


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
