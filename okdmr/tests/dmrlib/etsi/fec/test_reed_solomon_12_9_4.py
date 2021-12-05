from okdmr.kaitai.etsi.full_link_control import FullLinkControl

from okdmr.dmrlib.etsi.fec.reed_solomon_12_9_4 import ReedSolomon1294


def test_rs1294():
    voice_lc_header: bytes = bytes.fromhex("000000000009280722504778")
    lc: FullLinkControl = FullLinkControl.from_bytes(voice_lc_header)
    assert ReedSolomon1294.generate(voice_lc_header[:9]) == voice_lc_header
