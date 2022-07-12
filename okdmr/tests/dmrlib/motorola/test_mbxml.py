from typing import List, Tuple

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.motorola.mbxml import MBXML, MBXMLDocumentIdentifier
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits
from okdmr.tests.dmrlib.motorola.test_lrrp import lrrp_asserts


def test_uintvar():
    uintvars: List[Tuple[str, int]] = [
        # (hex encoded uintvar, int value)
        ("25", 0x25),
        ("8120", 0xA0),
        ("828F25", 0x87A5),
        ("8757", 0x3D7),
    ]
    for (uint_hex, uint_val) in uintvars:
        uint_bytes = bytes.fromhex(uint_hex)
        (uint, idx) = MBXML.read_uintvar(uint_bytes, 0)
        # assert value is read out correctly
        assert uint == uint_val
        # assert that data index moves
        assert idx == len(uint_bytes)
        # assert serialized is exact as original
        assert MBXML.write_uintvar(uint) == uint_bytes


def test_sintvar():
    sintvars: List[Tuple[str, int]] = [
        # (hex encoded sintvar, int value)
        ("65", -0x25),
        ("C120", -0xA0),
    ]
    for (sint_hex, sint_val) in sintvars:
        sint_bytes = bytes.fromhex(sint_hex)
        (sint, idx) = MBXML.read_sintvar(sint_bytes, 0)
        assert sint == sint_val
        assert idx == len(sint_bytes)
        assert MBXML.write_sintvar(sint_val) == sint_bytes


def test_ufloatvar():
    ufloatvars: List[Tuple[float, str, int]] = [
        # (float value, hex encoded ufloatvar, precision)
        (37 + (64 / 128), "2540", 1),
        (37 + (8192 / (128**2)), "2540", 1),
        (160 + (7 / 128), "812007", 2),
        (160 + (983 / (128**2)), "81208757", 2),
    ]
    for (ufloat_val, ufloat_hex, expected_precision) in ufloatvars:
        ufloat_bytes = bytes.fromhex(ufloat_hex)
        (ufloat, idx) = MBXML.read_ufloatvar(ufloat_bytes, 0)
        assert idx == len(ufloat_bytes)
        assert round(ufloat, expected_precision) == round(
            ufloat_val, expected_precision
        )
        assert MBXML.write_ufloatvar(ufloat_val, expected_precision) == ufloat_bytes


def test_sfloatvar():
    sfloatvars: List[Tuple[float, str, int]] = [
        # (float value, hex encoded sfloatvar, precision)
        (-37 - (64 / 128), "6540", 1),
        (-160 - (983 / (128**2)), "C1208757", 2),
    ]
    for (sfloat_val, sfloat_hex, expected_precision) in sfloatvars:
        sfloat_bytes = bytes.fromhex(sfloat_hex)
        (sfloat, idx) = MBXML.read_sfloatvar(sfloat_bytes, 0)
        assert idx == len(sfloat_bytes)
        assert round(sfloat, expected_precision) == round(
            sfloat_val, expected_precision
        )
        assert MBXML.write_sfloatvar(sfloat_val, expected_precision) == sfloat_bytes


def test_lrrp_constant_table():
    expected = (
        b"\x04HIGH"
        + b"\x06NORMAL"
        + b"\x04APCO"
        + b"\x04IPV4"
        + b"\x04IPV6"
        + b"\x04PLMN"
        + b"\x05TETRA"
        + b"\x0EUSER-SPECIFIED"
        + b"\x07http://"
        + b"\x0Bhttp://www."
        + b"\x03YES"
        + b"\x02NO"
        + b"\x03LTD"
    )
    built = MBXML.build_constants_table(
        MBXMLDocumentIdentifier.LRRP_ImmediateLocationRequest_NCDT
    )
    assert built == expected


def test_lrrp_example():
    serialized: bytes = bytes.fromhex("050822042468ACE05162")
    xml: str = """<?xml version="1.0" ?>
<Immediate-Location-Request>
\t<request-id>2468ACE0</request-id>
\t<query-info>
\t\t<ret-info ret-info-accuracy="YES" ret-info-time="YES"/>
\t\t<request-speed-hor/>
\t</query-info>
</Immediate-Location-Request>
"""
    lrrp_asserts(
        msg=serialized,
        xml=xml,
        docid=MBXMLDocumentIdentifier.LRRP_ImmediateLocationRequest_NCDT,
    )


def test_infotime():
    as_bytes: bytes = bytes.fromhex("1F4DBC7780")
    as_string: str = "20030630073000"
    bits: bitarray = bytes_to_bits(as_bytes)
    assert as_string == (
        f"{ba2int(bits[0:-26]):4}"
        f"{ba2int(bits[-26:-22]):02}"
        f"{ba2int(bits[-22:-17]):02}"
        f"{ba2int(bits[-17:-12]):02}"
        f"{ba2int(bits[-12:-6]):02}"
        f"{ba2int(bits[-6:]):02}"
    )
