from typing import List

from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RCPOpcode,
    RadioControlProtocol,
)


def test_opcodes():
    assert 0x8139 == int.from_bytes(
        RCPOpcode.RadioCallSetupModeReply.as_bytes(), byteorder="big"
    )


def test_pdus():
    pdus: List[str] = [
        # call request, private call to 1234
        "024108050000d20400000e03",
        # call result
        "0241880100006803",
    ]
    for pdu in pdus:
        pdu_bytes: bytes = bytes.fromhex(pdu)
        rcp: RadioControlProtocol = RadioControlProtocol.from_bytes(pdu_bytes)
        assert rcp.as_bytes() == pdu_bytes
        assert len(repr(rcp))
