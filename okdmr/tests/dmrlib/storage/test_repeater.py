import sys

from okdmr.dmrlib.storage.repeater import Repeater


def test_repeater():
    rpt: Repeater = Repeater(
        dmr_id=2305519,
        callsign="OK1DMR",
        serial="ABCDEF",
        address_in=("", 1),
        address_out=("", 0),
        nat_enabled=True,
        snmp_enabled=True,
    )
    assert rpt.callsign == "OK1DMR"
    assert rpt.dmr_id == 2305519
    assert rpt.serial == "ABCDEF"
    assert rpt.address_out == ("", 0)
    assert rpt.address_in == ("", 1)
    assert rpt.nat_enabled
    assert rpt.snmp_enabled

    rpt.attr("custom_attr", 123_456)
    assert rpt.attr("custom_attr") == 123_456
    rpt.delete_attr("custom_attr")
    assert rpt.attr("custom_attr") == None

    rpt.nat_enabled = True
    assert rpt.repeater_target_address() == ("", 0)
    rpt.nat_enabled = False
    assert rpt.repeater_target_address() == ("", 1)

    rpt.patch({"different_attr": False, "callsign": "OK4DMR"})
    assert rpt.attr("different_attr") == False
    assert rpt.callsign == "OK4DMR"

    # suppress puresnmp_plugins experimental warning
    if not sys.warnoptions:
        import warnings

        warnings.filterwarnings(
            message="Experimental SNMPv1 support", category=UserWarning, action="ignore"
        )
    rpt.address_out = ("127.0.0.1", 50000)
    rpt.read_snmp_values()

    rpt.snmp_enabled = False
    assert len(rpt.read_snmp_values()) == 0
