from okdmr.dmrlib.hytera.pdu.radio_control_protocol import RCPOpcode


def test_opcodes():
    assert 0x8139 == int.from_bytes(
        RCPOpcode.RadioCallSetupModeReply.as_bytes(), byteorder="big"
    )
