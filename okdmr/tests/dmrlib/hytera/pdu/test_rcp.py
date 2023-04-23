from typing import List

from okdmr.dmrlib.hytera.pdu.hrnp import HRNPOpcodes, HRNP
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RCPOpcode,
    RadioControlProtocol,
    StatusChangeNotificationSetting,
    StatusChangeNotificationTargets,
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
        # repeater broadcast transmit status
        "0245b810000100040004000000fd080000fa372300c303",
        #
        "0245b81000010005000000000000000000000000001F03",
        # request
        "02471808000000000000000000cb03",
        # response success
        "0247880100006203",
    ]
    for pdu in pdus:
        pdu_bytes: bytes = bytes.fromhex(pdu)
        rcp: RadioControlProtocol = RadioControlProtocol.from_bytes(pdu_bytes)
        assert rcp.as_bytes() == pdu_bytes
        assert len(repr(rcp))


def test_status_notify_pdus():
    r = RadioControlProtocol(
        opcode=RCPOpcode.StatusChangeNotificationRequest,
        status_change_settings={
            StatusChangeNotificationTargets.RSSI: StatusChangeNotificationSetting.ENABLE_NOTIFY,
            StatusChangeNotificationTargets.CHANNEL: StatusChangeNotificationSetting.ENABLE_NOTIFY,
            StatusChangeNotificationTargets.ZONE: StatusChangeNotificationSetting.DISABLE_NOTIFY,
            StatusChangeNotificationTargets.RADIO_DISABLE: StatusChangeNotificationSetting.ENABLE_NOTIFY,
        },
    )

    assert (
        r.as_bytes() == RadioControlProtocol.from_bytes(r.as_bytes()).as_bytes()
    ), f"unstable"

    r2 = HRNP(
        opcode=HRNPOpcodes.DATA,
        data=RadioControlProtocol(
            opcode=RCPOpcode.RadioStatusReport,
            status_change_target=StatusChangeNotificationTargets.RSSI,
            # RSSI value 0-4
            status_change_value=4,
        ),
    )
    assert r2.as_bytes() == HRNP.from_bytes(r2.as_bytes()).as_bytes(), f"unstable"
