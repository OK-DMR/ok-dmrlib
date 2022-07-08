from typing import Dict

from okdmr.dmrlib.motorola.mbxml import (
    MBXMLToken,
    GlobalToken,
    MBXMLDocument,
    MBXMLDocumentIdentifier,
    MBXMLTokenType,
)


class LRRP(MBXMLDocument):
    LRRP_CONSTANT_TABLE: Dict[int, MBXMLToken] = {
        # fmt:off
        0: MBXMLToken("", GlobalToken.STR8_I, value="HIGH"),
        1: MBXMLToken("", GlobalToken.STR8_I, value="NORMAL"),
        2: MBXMLToken("", GlobalToken.STR8_I, value="APCO"),
        3: MBXMLToken("", GlobalToken.STR8_I, value="IPV4"),
        4: MBXMLToken("", GlobalToken.STR8_I, value="IPV6"),
        5: MBXMLToken("", GlobalToken.STR8_I, value="PLMN"),
        6: MBXMLToken("", GlobalToken.STR8_I, value="TETRA"),
        7: MBXMLToken("", GlobalToken.STR8_I, value="USER-SPECIFIED"),
        8: MBXMLToken("", GlobalToken.STR8_I, value="http://"),
        9: MBXMLToken("", GlobalToken.STR8_I, value="http://www."),
        10: MBXMLToken("", GlobalToken.STR8_I, value="YES"),
        11: MBXMLToken("", GlobalToken.STR8_I, value="NO"),
        12: MBXMLToken("", GlobalToken.STR8_I, value="LTD"),
        # fmt:on
    }

    COMMON_ELEMENT_TOKENS: Dict[int, MBXMLToken] = {
        # fmt:off
        0x22: MBXMLToken("request-id", GlobalToken.OPAQUE_I),
        0x23: MBXMLToken("request-id", GlobalToken.OPAQUE_I, length=1),
        0x24: MBXMLToken("request-id", GlobalToken.OPAQUE_T),
        # fmt:on
    }

    QUERY_REQUEST_MESSAGES_ELEMENT_TOKENS: Dict[int, MBXMLToken] = {
        # fmt:off
        0x31: MBXMLToken("interval", GlobalToken.UINTVAR, path="periodic-trigger"),
        0x33: MBXMLToken("oneshot-trigger", GlobalToken.NO_VALUE),
        0x34: MBXMLToken("periodic-trigger", GlobalToken.NO_VALUE),
        # start of query-info sub-elements
        0x54: MBXMLToken("request-altitude", GlobalToken.NO_VALUE, path="query-info"),
        0x55: MBXMLToken("request-altitude-acc", GlobalToken.UINTVAR, path="query-info"),
        0x56: MBXMLToken("request-altitude-acc", GlobalToken.UFLOATVAR, path="query-info"),
        0x57: MBXMLToken("request-direction-hor", GlobalToken.NO_VALUE, path="query-info"),
        0x5F: MBXMLToken("request-hor-acc", GlobalToken.UINTVAR, path="query-info"),
        0x60: MBXMLToken("request-hor-acc", GlobalToken.UFLOATVAR, path="query-info"),
        0x61: MBXMLToken("request-lev-conf", GlobalToken.UINT8, path="query-info"),
        0x3F: MBXMLToken("request-protocol-version", GlobalToken.UINTVAR, path="query-info"),
        0x62: MBXMLToken("request-speed-hor", GlobalToken.NO_VALUE, path="query-info"),
        0x64: MBXMLToken("request-speed-vrt", GlobalToken.NO_VALUE, path="query-info"),
        0x42: MBXMLToken("require-max-info-age", GlobalToken.UINTVAR, path="query-info"),
        0x66: MBXMLToken("require-altitude", GlobalToken.NO_VALUE, path="query-info"),
        0x67: MBXMLToken("require-altitude-acc", GlobalToken.UINTVAR, path="query-info"),
        0x68: MBXMLToken("require-altitude-acc", GlobalToken.UFLOATVAR, path="query-info"),
        0x69: MBXMLToken("require-direction-hor", GlobalToken.NO_VALUE, path="query-info"),
        0x71: MBXMLToken("require-hor-acc", GlobalToken.UINTVAR, path="query-info"),
        0x72: MBXMLToken("require-hor-acc", GlobalToken.UFLOATVAR, path="query-info"),
        0x73: MBXMLToken("require-lev-conf", GlobalToken.UINT8, path="query-info"),
        0x74: MBXMLToken("require-speed-hor", GlobalToken.NO_VALUE, path="query-info"),
        0x76: MBXMLToken("require-speed-vrt", GlobalToken.NO_VALUE, path="query-info"),
        0x50: MBXMLToken("ret-info", GlobalToken.NO_VALUE, attributes=[0x50], path="query-info"),
        0x51: MBXMLToken("ret-info", GlobalToken.NO_VALUE, attributes=[0x51, 0x54], path="query-info"),
        0x52: MBXMLToken("ret-info", GlobalToken.NO_VALUE, attributes=[0x54], path="query-info"),
        0x53: MBXMLToken("ret-info", GlobalToken.NO_VALUE, path="query-info"),
        0x4A: MBXMLToken("trg-condition", GlobalToken.UINTVAR)
        # fmt:on
    }

    ANSWER_AND_REPORT_MESSAGES_ELEMENT_TOKENS: Dict[int, MBXMLToken] = {
        # fmt:off
        0x51: MBXMLToken("circle-2d", GlobalToken.CIRCLE_2D, path="info-data.shape"),
        0x54: MBXMLToken("circle-3d", GlobalToken.CIRCLE_3D, path="info-data.shape"),
        0x55: MBXMLToken("circle-3d", GlobalToken.CIRCLE_3D, path="info-data.shape"),
        0x56: MBXMLToken("direction-hor", GlobalToken.UINT8),
        0x34: MBXMLToken("info-time", GlobalToken.INFO_TIME, length=5, path="info-data"),
        0x35: MBXMLToken("info-time", GlobalToken.INFO_TIME, path="info-data"),
        0x65: MBXMLToken("lev-conf", GlobalToken.UINT8),
        0x66: MBXMLToken("point-2d", GlobalToken.POINT_2D, path="info-data.shape"),
        0x69: MBXMLToken("point-3d", GlobalToken.POINT_3D, path="info-data.shape"),
        0x6A: MBXMLToken("point-3d", GlobalToken.POINT_3D, path="info-data.shape"),
        0x36: MBXMLToken("protocol-version", GlobalToken.UINTVAR),
        0x37: MBXMLToken("result", GlobalToken.OPAQUE_I, length=0, attributes=[0x22]),
        0x38: MBXMLToken("result", GlobalToken.OPAQUE_I, length=0, attributes=[0x23]),
        0x39: MBXMLToken("result", GlobalToken.OPAQUE_I, attributes=[0x22], path="operation-error"),
        0x6C: MBXMLToken("speed-hor", GlobalToken.UFLOATVAR, path="info-data"),
        0x70: MBXMLToken("speed-vrt", GlobalToken.SFLOATVAR, path="info-data")
        # fmt:on
    }

    ATTRIBUTE_TOKENS: Dict[int, MBXMLToken] = {
        # fmt:off
        0x22: MBXMLToken("result-code", GlobalToken.UINTVAR, last_attribute=True),
        0x23: MBXMLToken("result-code", GlobalToken.UINTVAR, value=0, length=0, last_attribute=True),
        0x50: MBXMLToken("ret-info-accuracy", GlobalToken.STR8_ST, value=0x49, last_attribute=True),
        0x51: MBXMLToken("ret-info-accuracy", GlobalToken.STR8_ST, value=0x49, last_attribute=False),
        0x52: MBXMLToken("ret-info-no-req-id", GlobalToken.STR8_ST, value=0x49, last_attribute=True),
        0x53: MBXMLToken("ret-info-no-req-id", GlobalToken.STR8_ST, value=0x49, last_attribute=False),
        0x54: MBXMLToken("ret-info-time", GlobalToken.STR8_ST, value=0x49, last_attribute=True),
        0x55: MBXMLToken("ret-info-time", GlobalToken.STR8_ST, value=0x49, last_attribute=False),
        # fmt:on
    }

    @staticmethod
    def get_configuration(
        doc_type: MBXMLDocumentIdentifier,
    ) -> Dict[MBXMLTokenType, Dict[int, MBXMLToken]]:
        element_tokens: Dict[int, MBXMLToken] = LRRP.COMMON_ELEMENT_TOKENS

        if doc_type in (
            MBXMLDocumentIdentifier.LRRP_ImmediateLocationRequest,
            MBXMLDocumentIdentifier.LRRP_ImmediateLocationRequest_NCDT,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationRequest,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationRequest_NCDT,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopRequest,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopRequest_NCDT,
            MBXMLDocumentIdentifier.LRRP_LocationProtocolRequest_NCDT,
        ):
            element_tokens = {
                **element_tokens,
                **LRRP.QUERY_REQUEST_MESSAGES_ELEMENT_TOKENS,
            }
        elif doc_type in (
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationReport,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationReport_NCDT,
            MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport,
            MBXMLDocumentIdentifier.LRRP_ImmediateLocationReport_NCDT,
            MBXMLDocumentIdentifier.LRRP_UnsolicitedLocationReport,
            MBXMLDocumentIdentifier.LRRP_UnsolicitedLocationReport_NCDT,
            MBXMLDocumentIdentifier.LRRP_LocationProtocolReport_NCDT,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopAnswer,
            MBXMLDocumentIdentifier.LRRP_TriggeredLocationStopAnswer_NCDT,
        ):
            element_tokens = {
                **element_tokens,
                **LRRP.ANSWER_AND_REPORT_MESSAGES_ELEMENT_TOKENS,
            }

        return {
            MBXMLTokenType.ATTRIBUTE_TOKEN: LRRP.ATTRIBUTE_TOKENS,
            MBXMLTokenType.CONSTANT_TOKEN: LRRP.LRRP_CONSTANT_TABLE,
            MBXMLTokenType.ELEMENT_TOKEN: element_tokens,
        }
