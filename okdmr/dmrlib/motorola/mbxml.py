import enum
import math
from copy import copy
from typing import List, Optional, Tuple, Dict
from xml.dom import minidom


@enum.unique
class GlobalToken(enum.Enum):
    NO_VALUE = -0x02
    """ To indicate xml elements that have no value """
    UNKNOWN = -0x01
    """ Unrecognized tokens """

    END = 0x00
    """ End of attribute list or element """
    UINTVAR = 0x01
    """ unsigned int32 """
    SINTVAR = 0x02
    """ signed int32 """
    UFLOATVAR = 0x03
    """ unsigned float32 """
    SFLOATVAR = 0x04
    """ signed float32 """
    ENTITY = 0x05
    """
    character entity (as unicode code point)
    
    [ 05        | 20                                                             ]
    [ ENTITY    | XML ENTITY UNICODE CODE POINT (space \x20 also &#x20; or &#32; ]
    """
    OPAQUE_I = 0x06
    """
    Opaque data, size specified by UINTVAR
    
    [ 06         | 04                | 24 68 AC E0  ]
    [ OPAQUE_I   | LENGTH (4 bytes)  | DATA         ] 
    """
    OPAQUE_T = 0x07
    """
    Opaque data from CDT (constant data table), offset specified by UINTVAR
    
    [ 07        | 08                                  ]
    [ OPAQUE_T  | OFFSET FROM START OF CONSTANT TABLE ]
    """
    UINT8 = 0x08
    """ Single byte unsigned integer follows """
    STR8_I = 0x09
    """ Inline string 8-bits per character [0A | UINTVAR (string length) | DATA (n bytes)] """
    STR7_I = 0x0A
    """ Inline string 7-bits per character [0A | UINTVAR (string length) | DATA (n bytes)] """
    STR8_ST = 0x0B
    """
    Constant data table reference, string 8-bits per character
    [ 0B        | 08                                  ]
    [ STR8_ST   | OFFSET FROM START OF CONSTANT TABLE ]
    """
    CONCAT = 0x0C
    """
    Concatenate two strings together, preceding token and following token should be always in (STR8_I, STR7_I, STR8_ST)
    eg. like this [STR8_ST] [CONCAT] [STR8_ST]
    """
    RESERVED = 0x0D
    """
    Values 0D - 1C are reserved values for global tokens
    """
    DOCUMENT_SPECIFIC = 0x1D
    """
    Values 1D - 1F are used for document specific use
    """

    @classmethod
    def _missing_(cls, value: int) -> "GlobalToken":
        if 0x0D <= value <= 0x1C:
            return GlobalToken.RESERVED
        elif 0x1D <= value <= 0x1F:
            return GlobalToken.DOCUMENT_SPECIFIC

        return GlobalToken.UNKNOWN


@enum.unique
class MBXMLDocumentIdentifier(enum.Enum):
    """
    NCDT means "No Constant Data Table"

    Tuple structure is (document id, is NCDT, root xml element name)
    """

    Reserved = (0x00, False, "Reserved")
    ReservedNCDT = (0x01, True, "Reserved")
    ReservedTesting = (0x02, False, "Reserved-Testing")
    ReservedTesting_NCDT = (0x03, True, "Reserved-Testing")
    # LRRP = Location Request/Response Protocol
    LRRP_ImmediateLocationRequest = (0x04, False, "Immediate-Location-Request")
    LRRP_ImmediateLocationRequest_NCDT = (0x05, True, "Immediate-Location-Request")
    LRRP_ImmediateLocationReport = (0x06, False, "Immediate-Location-Report")
    LRRP_ImmediateLocationReport_NCDT = (0x07, True, "Immediate-Location-Report")
    LRRP_TriggeredLocationRequest = (0x08, False, "Triggered-Location-Request")
    LRRP_TriggeredLocationRequest_NCDT = (0x09, True, "Triggered-Location-Request")
    LRRP_TriggeredLocationAnswer = (0x0A, False, "Triggered-Location-Answer")
    LRRP_TriggeredLocationAnswer_NCDT = (0x0B, True, "Triggered-Location-Answer")
    LRRP_TriggeredLocationReport = (0x0C, False, "Triggered-Location-Report")
    LRRP_TriggeredLocationReport_NCDT = (0x0D, True, "Triggered-Location-Report")
    LRRP_TriggeredLocationStopRequest = (0x0E, False, "Triggered-Location-Stop-Request")
    LRRP_TriggeredLocationStopRequest_NCDT = (
        0x0F,
        True,
        "Triggered-Location-Stop-Request",
    )
    LRRP_TriggeredLocationStopAnswer = (0x10, False, "Triggered-Location-Stop-Answer")
    LRRP_TriggeredLocationStopAnswer_NCDT = (
        0x11,
        True,
        "Triggered-Location-Stop-Answer",
    )
    LRRP_UnsolicitedLocationReport = (0x12, False, "Location-Protocol-Report")
    LRRP_UnsolicitedLocationReport_NCDT = (0x13, True, "Location-Protocol-Report")
    LRRP_LocationProtocolRequest_NCDT = (0x14, True, "Location-Protocol-Request")
    LRRP_LocationProtocolReport_NCDT = (0x15, True, "Location-Protocol-Report")
    # ARRP = Accessories Request/Response Protocol
    ARRP_ImmediateInformationRequest = (0x16, False)
    ARRP_ImmediateInformationRequest_NCDT = (0x17, True)
    ARRP_ImmediateInformationReport = (0x18, False)
    ARRP_ImmediateInformationReport_NCDT = (0x19, True)
    ARRP_TriggeredInformationRequest = (0x1A, False)
    ARRP_TriggeredInformationRequest_NCDT = (0x1B, True)
    ARRP_TriggeredInformationAnswer = (0x1C, False)
    ARRP_TriggeredInformationAnswer_NCDT = (0x1D, True)
    ARRP_TriggeredInformationReport = (0x1E, False)
    ARRP_TriggeredInformationReport_NCDT = (0x1F, True)
    ARRP_TriggeredInformationStopRequest = (0x20, False)
    ARRP_TriggeredInformationStopRequest_NCDT = (0x21, True)
    ARRP_TriggeredInformationStopAnswer = (0x22, False)
    ARRP_TriggeredInformationStopAnswer_NCDT = (0x23, True)
    ARRP_UnsolicitedInformationReport = (0x24, False)
    ARRP_UnsolicitedInformationReport_NCDT = (0x25, True)
    ARRP_InformationProtocolRequest_NCDT = (0x26, True)
    ARRP_InformationProtocolReport_NCDT = (0x27, True)

    @classmethod
    def resolve(cls, docid: int) -> Optional["MBXMLDocumentIdentifier"]:

        for _doc in cls:
            (_docid, _is_ncdt, _) = _doc.value
            if _docid == docid:
                return _doc

        return None


@enum.unique
class MBXMLTokenType(enum.Enum):
    ELEMENT_TOKEN = 0x01
    ATTRIBUTE_TOKEN = 0x02
    CONSTANT_TOKEN = 0x03


class MBXMLToken:
    def __init__(
        self,
        name: str,
        _type: GlobalToken,
        token_id: int = 0,
        last_attribute: bool = False,
        attributes: Optional[List[int]] = None,
        length: Optional[int] = None,
        path: Optional[str] = None,
        value: Optional[any] = None,
        constant_position: Optional[int] = None,
    ):
        self.name: str = name
        self.token_type: GlobalToken = _type
        self.token_id: int = token_id
        self.last_attribute: bool = last_attribute
        self.attributes: List[int] = attributes or []
        self.length: Optional[int] = length
        self.path: Optional[str] = path
        self.value: Optional[any] = value
        self.constant_position: Optional[int] = constant_position

    def get_value(self, doc: "MBXMLDocument") -> any:
        if self.token_type in (GlobalToken.STR8_ST, GlobalToken.OPAQUE_T):
            (val, idx) = MBXML.read_opaque(doc.constants_table, self.value)
            return val.decode("ascii")
        elif isinstance(self.value, bytes):
            return self.value.hex().upper()
        return self.value

    def get_attributes(self, doc: "MBXMLDocument") -> Dict[str, str]:
        """
        Will return dictionary of attributes {attr name => value}
        """
        rtn: Dict[str, str] = {}
        for attr_id in self.attributes:
            attr_def = doc.attributes_config[attr_id]
            rtn[attr_def.name] = attr_def.get_value(doc)

        return rtn

    def __str__(self):
        return f"[{self.name} is {self.token_type.name} ({hex(self.token_id)})]"

    def __repr__(self):
        return f"[{self.token_type.name} {self.name} ({hex(self.token_id)})]" + (
            f" [VAL: {self.value.hex() if isinstance(self.value, bytes) else self.value}]"
            if self.value
            else ""
        )


LRRP_CONSTANT_TABLE: Dict[int, MBXMLToken] = {
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
}

DOCUMENT_CONFIGURATION: Dict[
    MBXMLDocumentIdentifier, Dict[MBXMLTokenType, Dict[int, MBXMLToken]]
] = {
    MBXMLDocumentIdentifier.LRRP_ImmediateLocationRequest_NCDT: {
        MBXMLTokenType.ELEMENT_TOKEN: {
            0x22: MBXMLToken("request-id", GlobalToken.OPAQUE_I),
            0x23: MBXMLToken("request-id", GlobalToken.OPAQUE_I, length=1),
            0x24: MBXMLToken("request-id", GlobalToken.OPAQUE_T),
            0x50: MBXMLToken(
                "ret-info", GlobalToken.NO_VALUE, attributes=[0x50], path="query-info"
            ),
            0x51: MBXMLToken(
                "ret-info",
                GlobalToken.NO_VALUE,
                attributes=[0x51, 0x54],
                path="query-info",
            ),
            0x52: MBXMLToken(
                "ret-info", GlobalToken.NO_VALUE, attributes=[0x54], path="query-info"
            ),
            0x53: MBXMLToken("ret-info", GlobalToken.NO_VALUE, path="query-info"),
            0x62: MBXMLToken(
                "request-speed-hor", GlobalToken.NO_VALUE, path="query-info"
            ),
        },
        MBXMLTokenType.ATTRIBUTE_TOKEN: {
            0x22: MBXMLToken("result-code", GlobalToken.UINTVAR, last_attribute=True),
            0x23: MBXMLToken(
                "result-code", GlobalToken.UINTVAR, length=0, last_attribute=True
            ),
            0x50: MBXMLToken(
                "ret-info-accuracy",
                GlobalToken.STR8_ST,
                value=0x49,
                last_attribute=True,
            ),
            0x51: MBXMLToken("ret-info-accuracy", GlobalToken.STR8_ST, value=0x49),
            0x52: MBXMLToken(
                "ret-info-no-req-id",
                GlobalToken.STR8_ST,
                value=0x49,
                last_attribute=True,
            ),
            0x53: MBXMLToken("ret-info-no-req-id", GlobalToken.STR8_ST, value=0x49),
            0x54: MBXMLToken(
                "ret-info-time", GlobalToken.STR8_ST, value=0x49, last_attribute=True
            ),
            0x55: MBXMLToken("ret-info-time", GlobalToken.STR8_ST, value=0x49),
        },
        MBXMLTokenType.CONSTANT_TOKEN: LRRP_CONSTANT_TABLE,
    }
}


class MBXMLDocument:
    """
    Parent class for all documents, to hold the elements, attributes and
    """

    def __init__(
        self,
        document_id: MBXMLDocumentIdentifier,
        elements_config: Optional[Dict[int, MBXMLToken]] = None,
        attributes_config: Optional[Dict[int, MBXMLToken]] = None,
        constants_table: bytes = b"",
        default_constants_table: Optional[Dict[int, MBXMLToken]] = None,
    ) -> None:
        self.id: MBXMLDocumentIdentifier = document_id
        self.constants_table: bytes = constants_table
        self.default_constants_table: Dict[int, MBXMLToken] = (
            default_constants_table or {}
        )
        self.parts: List[MBXMLToken] = []
        self.elements_config: Dict[int, MBXMLToken] = elements_config or {}
        self.attributes_config: Dict[int, MBXMLToken] = attributes_config or {}

    def set_default_constants_table(
        self, constants: Dict[int, MBXMLToken]
    ) -> "MBXMLDocument":
        self.default_constants_table = constants
        self.constants_table = MBXML.build_constants_table(self.id)
        return self

    def __str__(self) -> str:
        return f"[MBXMLDocument {self.id.name} (+ {len(self.parts)} elements)"

    def __repr__(self) -> str:
        _repr: str = f"[MBXMLDocument {self.id.name}]"
        for part in self.parts:
            _repr += "\n\t" + repr(part)
        return _repr

    def as_xml(self) -> str:
        root: minidom.Document = minidom.Document()

        xml: minidom.Element = root.createElement(
            self.id.value[2] or "Unknown-XML-Root-Element"
        )
        root.appendChild(xml)

        for part in self.parts:
            part_element: minidom.Element = root.createElement(part.name)
            val: Optional[any] = part.get_value(self)
            if val:
                part_value: minidom.Text = root.createTextNode(str(val))
                part_element.appendChild(part_value)
            for attr_name, attr_value in part.get_attributes(self).items():
                part_element.setAttribute(attr_name, attr_value)

            parent = xml

            if isinstance(part.path, str) and len(part.path) > 1:
                for path_part in part.path.split("."):
                    path_part_exists: bool = False
                    for _child in parent.childNodes:
                        if (
                            isinstance(_child, minidom.Element)
                            and _child.nodeName == path_part
                        ):
                            parent = _child
                            path_part_exists = True
                            break
                    if not path_part_exists:
                        _elm = root.createElement(path_part)
                        parent.appendChild(_elm)
                        parent = _elm

            parent.appendChild(part_element)

        return root.toprettyxml(indent="\t")


class MBXML:
    """
    Utility class to serialize (as_bytes) and de-serialize (from_bytes) MBXML documents
    """

    UINTVAR_MAX = 4294967295
    SINTVAR_MAX = 2147483647

    @classmethod
    def read_uintvar(cls, data: bytes, idx: int) -> Tuple[int, int]:
        """
        Start at data[idx] and read uintvar, return read uint value and new idx
        """
        uintvar = 0
        while True:
            this = data[idx]
            # apend 7 bits to uintvar
            uintvar = (uintvar << 7) + (this & 0x7F)
            # raise data index
            idx += 1
            if this & 0x80 == 0:
                break

        return uintvar, idx

    @classmethod
    def write_uintvar(cls, value: int) -> bytes:
        assert value >= 0, f"write_uintvar cannot write negative integers"
        assert (
            value <= cls.UINTVAR_MAX
        ), f"write_uintvar cannot write integers bigger than {cls.UINTVAR_MAX}"
        bin_val: str = bin(value)[2:][::-1]

        if bin_val[0:7] == "0000000" and (len(bin_val) / 7) > 1:
            # remove appended zeroes
            bin_val = bin_val[7:]

        bin_len: int = len(bin_val)
        byte_len: int = math.ceil(bin_len / 7)

        uintvar: bytes = b""
        for i in range(0, byte_len):
            bval = int(bin_val[i * 7 : (i + 1) * 7][::-1], 2)
            uintvar += int.to_bytes(
                bval | (0x00 if i == 0 else 0x80), length=1, byteorder="big"
            )

        return uintvar[::-1]

    @classmethod
    def read_sintvar(cls, data: bytes, idx: int) -> Tuple[int, int]:
        """
        Start at data[idx] and read sintvar, return read sint value and new idx
        """
        sintvar = 0
        first: bool = True
        sign: int = 0
        while True:
            this = data[idx]
            mask = 0x7F
            # first bit of first data byte is sign-bit (+/-)
            if first:
                sign = -1 if (this & 0x40) > 0 else 1
                mask = 0x3F
                first = False
            sintvar = (sintvar << 7) + (this & mask)
            # raise data index
            idx += 1

            if this & 0x80 == 0:
                break

        return (sintvar * sign), idx

    @classmethod
    def write_sintvar(cls, value: int) -> bytes:
        """
        write sintvar and return bytes representation
        """
        assert abs(value) <= cls.SINTVAR_MAX, (
            f"write_sintvar cannot write integers bigger than {cls.SINTVAR_MAX} "
            f"(or smaller than -{cls.SINTVAR_MAX}"
        )
        sintvar: bytes = cls.write_uintvar(abs(value))
        return sintvar if value >= 0 else (bytes([sintvar[0] | 0x40]) + sintvar[1:])

    @classmethod
    def read_ufloatvar(cls, data: bytes, idx: int) -> Tuple[float, int]:
        """
        read ufloatvar from data[idx] on, return (float value, new idx)
        """
        (integer, idx) = cls.read_uintvar(data, idx)
        (decimal, idx_2) = cls.read_uintvar(data, idx)
        return (integer + (decimal / 128 ** (idx_2 - idx))), idx_2

    @classmethod
    def write_ufloatvar(cls, value: float, precision: int) -> bytes:
        """
        write ufloatvar and return bytes representation
        """
        assert precision >= 1, f"write_ufloatvar precision must be at least 1 decimal"
        int_part = int(value)
        dec_part = int(value % 1 * 128**precision)
        integer = cls.write_uintvar(int_part)
        decimal = cls.write_uintvar(dec_part)
        return integer + decimal

    @classmethod
    def read_sfloatvar(cls, data: bytes, idx: int) -> Tuple[float, int]:
        """
        read sfloatvar from data[idx] on, return (float value, new idx)
        """
        (integer, idx) = cls.read_sintvar(data, idx)
        (decimal, idx_2) = cls.read_uintvar(data, idx)
        return (
            math.copysign((abs(integer) + (decimal / 128 ** (idx_2 - idx))), integer),
            idx_2,
        )

    @classmethod
    def write_sfloatvar(cls, value: float, precision: int) -> bytes:
        assert precision >= 1, f"write_sfloatvar precision must be at least 1 decimal"
        int_part = int(value)
        dec_part = int(abs(value % (1 if value >= 0 else -1)) * 128**precision)
        integer = cls.write_sintvar(int_part)
        decimal = cls.write_uintvar(dec_part)
        return integer + decimal

    @classmethod
    def read_opaque(cls, data: bytes, idx: int) -> Tuple[bytes, int]:
        """
        Read opaque bytes encoded as [ length(uintvar) | data(byte*) ]
        """
        (bytes_len, idx) = cls.read_uintvar(data, idx)
        return data[idx : idx + bytes_len], idx + bytes_len

    @classmethod
    def read_document(
        cls, doctype: MBXMLDocumentIdentifier, data: bytes, idx: int
    ) -> MBXMLDocument:
        doctype_configuration = DOCUMENT_CONFIGURATION[doctype]
        (document_id, has_no_constants_table, _) = doctype.value
        doc = MBXMLDocument(
            document_id=doctype,
            elements_config=doctype_configuration[MBXMLTokenType.ELEMENT_TOKEN],
            attributes_config=doctype_configuration[MBXMLTokenType.ATTRIBUTE_TOKEN],
        )

        if not has_no_constants_table:
            # fill in constants, if indicated
            (constants, idx) = cls.read_opaque(data, idx)
            doc.constants_table = constants
        elif MBXMLTokenType.CONSTANT_TOKEN in doctype_configuration:
            doc.set_default_constants_table(
                doctype_configuration[MBXMLTokenType.CONSTANT_TOKEN]
            )

        while idx != len(data):
            (token_id, idx) = cls.read_uintvar(data, idx)
            token_config: MBXMLToken = copy(
                doctype_configuration[MBXMLTokenType.ELEMENT_TOKEN][token_id]
            )
            token_config.token_id = token_id

            if token_config.token_type == GlobalToken.OPAQUE_I:
                (token_config.value, idx) = cls.read_opaque(data, idx)
            elif token_config.token_type == GlobalToken.NO_VALUE:
                pass
            else:
                raise NotImplementedError(f"not implemented for config {token_config}")

            doc.parts.append(token_config)

        return doc

    @classmethod
    def write_part(cls, part: MBXMLToken) -> bytes:
        if part.token_type == GlobalToken.OPAQUE_I:
            return (
                bytes([part.token_id]) + cls.write_uintvar(len(part.value)) + part.value
            )
        elif part.token_type == GlobalToken.NO_VALUE:
            return bytes([part.token_id])
        elif part.token_type == GlobalToken.STR8_I:
            return (
                bytes([part.token_id])
                + cls.write_uintvar(len(part.value))
                + part.value.encode("ascii")
            )

        raise NotImplementedError(f"write_part not implemented for {part.token_type}")

    @classmethod
    def build_constants_table(cls, document_type: MBXMLDocumentIdentifier):
        assert document_type in DOCUMENT_CONFIGURATION, f"Not implemented document type"
        assert (
            MBXMLTokenType.CONSTANT_TOKEN in DOCUMENT_CONFIGURATION[document_type]
        ), f"Missing constants configuration"
        values: Dict[int, MBXMLToken] = DOCUMENT_CONFIGURATION[document_type][
            MBXMLTokenType.CONSTANT_TOKEN
        ]
        tbl = b""
        for i in range(0, len(values)):
            # strip first byte which marks type of value, CDT contains only LV (from TLV, missing TYPE indication uintvar)
            tbl += cls.write_part(values[i])[1:]
        return tbl

    @classmethod
    def from_bytes(cls, data: bytes) -> List["MBXMLDocument"]:
        """
        Parse bytes and return all found de-serialized documents
        """
        data_len = len(data)
        rtn: List[MBXMLDocument] = []

        idx: int = 0
        while True:
            (doc_id, idx) = cls.read_uintvar(data, idx)
            doctype = MBXMLDocumentIdentifier.resolve(doc_id)
            (doc_len_bytes, idx) = cls.read_uintvar(data, idx)
            rtn.append(cls.read_document(doctype, data, idx))
            idx += doc_len_bytes
            if idx == data_len:
                break

        return rtn

    @classmethod
    def as_bytes(cls, doc: MBXMLDocument) -> bytes:
        rtn = cls.write_uintvar(doc.id.value[0])

        body = b""
        for part in doc.parts:
            body += cls.write_part(part)

        return rtn + cls.write_uintvar(len(body)) + body
