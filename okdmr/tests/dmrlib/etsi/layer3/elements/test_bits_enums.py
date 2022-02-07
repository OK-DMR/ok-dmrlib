from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer3.elements.dynamic_identifier import DynamicIdentifier


def test_bits_enums():
    e = DynamicIdentifier.LeaderPreferenceHigh
    assert e == DynamicIdentifier.from_bits(e.as_bits())

    e = CsbkOpcodes.ChannelTimingCSBK
    assert e == CsbkOpcodes.from_bits(e.as_bits())
