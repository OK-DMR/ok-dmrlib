from typing import List

from okdmr.dmrlib.motorola.mbxml import MBXML, MBXMLDocument, MBXMLDocumentIdentifier


def lrrp_asserts(msg: bytes, xml: str, docid: MBXMLDocumentIdentifier) -> None:
    assert msg[1] == (
        len(msg) - 2
    ), f"single message document length should be {len(msg)-2} got {msg[1]}"
    docs: List[MBXMLDocument] = MBXML.from_bytes(msg)
    assert len(docs) == 1
    doc: MBXMLDocument = docs[0]
    assert doc.id == docid
    assert MBXML.as_bytes(doc) == msg
    if len(xml) > 1:
        assert doc.as_xml() == xml
    else:
        print(repr(doc))
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
    )


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


def test_random_samples():
    msg: bytes = bytes.fromhex("1313232F341F99B20E87664728A1C70A38D29F561A")

    lrrp_asserts(
        xml="",
        msg=msg,
        docid=MBXMLDocumentIdentifier.LRRP_UnsolicitedLocationReport_NCDT,
    )
