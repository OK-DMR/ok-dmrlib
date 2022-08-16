from copy import copy
from typing import List

import pytest

from okdmr.dmrlib.motorola.lrrp import LRRP
from okdmr.dmrlib.motorola.mbxml import MBXML, MBXMLDocument, MBXMLDocumentIdentifier


def lrrp_asserts(
    msg: bytes, xml: str, docid: MBXMLDocumentIdentifier, debug: bool = False
) -> None:
    assert msg[1] == (
        len(msg) - 2
    ), f"single message document length should be {len(msg) - 2} got {msg[1]}"
    docs: List[MBXMLDocument] = MBXML.from_bytes(data=msg, debug=debug)
    assert len(docs) == 1
    doc: MBXMLDocument = docs[0]
    assert doc.id == docid
    assert MBXML.as_bytes(doc) == msg
    if len(xml) > 1:
        assert doc.as_xml() == xml
        assert len(str(doc))
        assert len(repr(doc))

        for part in doc.parts:
            assert len(repr(part))
            assert len(str(part))
    else:
        print()
        print(repr(doc))
        print()
        print(doc.as_xml())


def test_example_report():
    xml: str = """<?xml version="1.0" ?>
<Immediate-Location-Report>
\t<request-id>2468ACE0</request-id>
\t<info-data>
\t\t<info-time>20030630073000</info-time>
\t\t<shape>
\t\t\t<circle-2d>
\t\t\t\t<lat>12.345345</lat>
\t\t\t\t<long>24.668866</long>
\t\t\t\t<radius>0.77</radius>
\t\t\t</circle-2d>
\t\t</shape>
\t\t<speed-hor>0.04688</speed-hor>
\t</info-data>
</Immediate-Location-Report>
"""
    msg_bytes: bytes = bytes.fromhex(
        "071A22042468ACE0341F4DBC778051118ECD8D118AD47B00636C0006"
    )
    lrrp_asserts(
        msg=msg_bytes,
        xml=xml,
        docid=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT,
    )

    # assemble document from parts
    doc = LRRP(document_id=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT)
    doc.parts.append(
        doc.get_token(
            name="request-id",
            value=bytes.fromhex("2468ACE0"),
            attributes={},
            is_request=False,
        )
    )
    doc.parts.append(
        doc.get_token(
            name="info-time",
            value=MBXML.write_infotime(20030630073000),
            attributes={},
            is_request=False,
        )
    )
    doc.parts.append(
        doc.get_token(
            name="circle-2d",
            value=(
                MBXML.write_latitude(12.345345),
                MBXML.write_longitude(24.668866),
                # see test_mbxml.py::test_ufloatvar_example for explanation
                0.7734375,
            ),
            attributes={},
            is_request=False,
        )
    )
    doc.parts.append(
        doc.get_token("speed-hor", value=0.04688, attributes={}, is_request=False)
    )
    assert MBXML.as_bytes(doc) == msg_bytes


def test_example_report_with_error():
    xml: str = """<?xml version="1.0" ?>
<Immediate-Location-Report>
\t<request-id>2468ACE0</request-id>
\t<operation-error>
\t\t<result result-code="5">515355</result>
\t</operation-error>
</Immediate-Location-Report>
"""
    msg_bytes: bytes = bytes.fromhex("070C22042468ACE0390503515355")
    lrrp_asserts(
        xml=xml,
        msg=msg_bytes,
        docid=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT,
        debug=False,
    )

    # assemble document from parts
    doc = LRRP(document_id=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT)
    doc.parts.append(
        doc.get_token(
            name="request-id",
            value=bytes.fromhex("2468ACE0"),
            attributes={},
            is_request=False,
        )
    )
    # using 0x39 instead of "result" since only this one is "operation-error" information element
    doc.parts.append(
        doc.get_token(
            name=0x39,
            value=bytes.fromhex("515355"),
            attributes={"result-code": 5},
            is_request=False,
        )
    )
    assert MBXML.as_bytes(doc) == msg_bytes


def test_example_triggered_request():
    xml: str = """<?xml version="1.0" ?>
<Triggered-Location-Request>
\t<request-id>2468ACE0</request-id>
\t<periodic-trigger>
\t\t<interval>60</interval>
\t</periodic-trigger>
</Triggered-Location-Request>
"""
    msg_bytes: bytes = bytes.fromhex("090922042468ACE034313C")
    lrrp_asserts(
        xml=xml,
        msg=msg_bytes,
        docid=MBXMLDocumentIdentifier.LRRP_TriggeredLocationRequest_NCDT,
    )

    # assemble document from parts
    doc = LRRP(document_id=MBXMLDocumentIdentifier.LRRP_TriggeredLocationRequest_NCDT)
    doc.parts.append(
        doc.get_token(
            name="request-id",
            value=bytes.fromhex("2468ACE0"),
            attributes={},
            is_request=True,
        )
    )
    doc.parts.append(doc.get_token(name="periodic-trigger", value=None, attributes={}))
    doc.parts.append(
        doc.get_token(name="interval", value=60, attributes={}, is_request=True)
    )
    assert msg_bytes == MBXML.as_bytes(doc)


def test_example_triggered_report():
    xml: str = """<?xml version="1.0" ?>
<Triggered-Location-Report>
\t<request-id>2468ACE0</request-id>
\t<info-data>
\t\t<shape>
\t\t\t<point-2d>
\t\t\t\t<lat>12.345345</lat>
\t\t\t\t<long>24.668866</long>
\t\t\t</point-2d>
\t\t</shape>
\t</info-data>
</Triggered-Location-Report>
"""
    msg: bytes = bytes.fromhex("0D0F22042468ACE066118ECD8D118AD47B")
    lrrp_asserts(
        xml=xml,
        msg=msg,
        docid=MBXMLDocumentIdentifier.LRRP_TriggeredLocationReport_NCDT,
    )

    # assemble document from parts
    doc = LRRP(document_id=MBXMLDocumentIdentifier.LRRP_TriggeredLocationReport_NCDT)
    doc.parts.append(
        doc.get_token(
            name="request-id",
            value=bytes.fromhex("2468ACE0"),
            attributes={},
            is_request=False,
        )
    )
    doc.parts.append(
        doc.get_token(
            name="point-2d",
            value=(MBXML.write_latitude(12.345345), MBXML.write_longitude(24.668866)),
            attributes={},
            is_request=False,
        )
    )
    assert msg == MBXML.as_bytes(doc)


def test_example_triggered_stop_request():
    xml: str = """<?xml version="1.0" ?>
<Triggered-Location-Stop-Request>
\t<request-id>2468ACE0</request-id>
</Triggered-Location-Stop-Request>
"""
    msg: bytes = bytes.fromhex("0F0622042468ACE0")
    lrrp_asserts(
        xml=xml,
        msg=msg,
        docid=MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopRequest_NCDT,
    )

    # assemble document from parts
    doc = LRRP(
        document_id=MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopRequest_NCDT
    )
    doc.parts.append(
        doc.get_token(name="request-id", value=bytes.fromhex("2468ACE0"), attributes={})
    )
    assert MBXML.as_bytes(doc) == msg


def test_example_triggered_stop_answer():
    xml: str = """<?xml version="1.0" ?>
<Triggered-Location-Stop-Answer>
\t<request-id>2468ACE0</request-id>
\t<result result-code="0"/>
</Triggered-Location-Stop-Answer>
"""
    msg: bytes = bytes.fromhex("110722042468ACE038")
    lrrp_asserts(
        xml=xml,
        msg=msg,
        docid=MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopAnswer_NCDT,
    )

    # working manual way of assembly
    doc = MBXMLDocument(
        document_id=MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopAnswer_NCDT
    )

    rid = copy(LRRP.COMMON_ELEMENT_TOKENS[0x22])
    rid.value = bytes.fromhex("2468ACE0")
    rid.token_id = 0x22
    doc.parts.append(rid)

    rc = copy(LRRP.ANSWER_AND_REPORT_MESSAGES_ELEMENT_TOKENS[0x38])
    rc.value = b""
    rc.token_id = 0x38
    doc.parts.append(rc)

    assert MBXML.as_bytes(doc) == msg

    # assemble document from parts
    doc = LRRP(
        document_id=MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopAnswer_NCDT
    )
    doc.parts.append(
        doc.get_token(
            name="request-id",
            value=bytes.fromhex("2468ACE0"),
            attributes={},
            is_request=False,
        )
    )
    doc.parts.append(
        doc.get_token(name="result", value=b"", attributes={0x23: 0}, is_request=False)
    )
    assert MBXML.as_bytes(doc) == msg


def test_unknown_samples():
    samples: List[str] = [
        "1315232F341F4AD07B2E66474326660A4D56E46B0B5620",
        "1313232F341F99B20E87664728A1C70A38D29F561A",
    ]
    for sample in samples:
        msg: bytes = bytes.fromhex(sample)
        lrrp_asserts(
            xml="",
            msg=msg,
            debug=True,
            docid=MBXMLDocumentIdentifier.LRRP_UnsolicitedLocationReport_NCDT,
        )


def test_triggered_report_samples():
    samples: List[str] = [
        "0d162204c00000005148610c340ad0ecf70c126c003656a2",
        "0d1a22047fffffff69486109950ad0ecd28338156c000856a270400a",
        "0d162204c00000005148610be00ad0ecaa0b5b6c000956a2",
        "0d162204c00000005148610e0c0ad0ec0d0a736c001056a2",
        "0d1a22047fffffff6948610e0c0ad0ec0d8337606c001056a2704001",
        "0d162204c00000005148610b2b0ad0eca109796c000256a2",
        "0d1a22047fffffff6948610b4a0ad0ec9d833c516c000656a2704007",
        "0d162204c00000005148610b430ad0ec78083e6c000456a2",
        "0d162204c000000051486109b90ad0eb120a4e6c002556a2",
        "0d1a22047fffffff69486109b90ad0eb12833f656c002556a2704009",
        "0d162204c0000000514861096a0ad0ebdb091c6c000756a2",
        "0d1a22047fffffff69486108d70ad0ec15833f546c000456a2704005",
    ]
    for sample in samples:
        lrrp_asserts(
            xml="",
            msg=bytes.fromhex(sample),
            debug=False,
            docid=MBXMLDocumentIdentifier.LRRP_TriggeredLocationReport_NCDT,
        )


class TestRaising:
    def test_raising_token(self):
        with pytest.raises(ModuleNotFoundError):
            LRRP(
                document_id=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT
            ).get_token(name="nonexistant", value=None, attributes={})

    def test_raising_attribute(self):
        with pytest.raises(ModuleNotFoundError):
            LRRP(
                document_id=MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT
            ).get_attribute(name="nonexistant", value=None)
