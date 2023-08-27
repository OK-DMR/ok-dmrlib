import logging
import sys
from typing import Dict

from okdmr.dmrlib.hytera.snmp import octet_string_to_utf8, SNMP
from okdmr.dmrlib.storage.repeater import Repeater


def test_octet_filtering():
    # key(non-filtered): value(filtered)
    test_strings: Dict[str, str] = {
        "abcd": "abcd",
        "abcd\0": "abcd",
        "abcd\n": "abcd\n",
    }
    for test_value, test_expect in test_strings.items():
        assert test_expect == octet_string_to_utf8(test_value)


def test_snmp():
    # suppress puresnmp_plugins experimental warning
    if not sys.warnoptions:
        import warnings

        warnings.filterwarnings(
            message="Experimental SNMPv1 support", category=UserWarning, action="ignore"
        )

    rpt = Repeater(address_out=("127.0.0.1", 0))
    rpt.read_snmp_values()


def test_snmp_print(caplog):
    caplog.set_level(logging.DEBUG)
    SNMP().print_snmp_data({"key": "value", SNMP.OID_RADIO_ID: 12345}, "0.1.2.3")
    assert len(caplog.messages)
