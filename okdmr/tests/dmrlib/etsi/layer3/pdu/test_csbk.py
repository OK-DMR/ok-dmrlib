from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer3.pdu.csbk import CSBK


def test_csbk():
    mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(
        bytes.fromhex(
            "444d52440923383b0008fd0006690fe33391012951dd0c4d8bb40ac413a86c5094fdff57d75df5dcadfa1268aaa87b82b9d8291910003c"
        )
    )
    burst: Burst = Burst.from_mmdvm(mmdvm.command_data)
    csbk = CSBK.from_bits(burst.info_bits_deinterleaved)
    assert csbk.last_block
    assert not csbk.protect_flag
    assert csbk.csbko == CsbkOpcodes.PreambleCSBK
    assert csbk.feature_set == FeatureSetIDs.StandardizedFID
    assert csbk.target_address == 2301
    assert csbk.source_address == 2308155
    # todo: add test for crc-ccit and to_bits
