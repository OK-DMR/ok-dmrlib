import enum
import math
from copy import copy
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Type, Union
from xml.dom import minidom

from bitarray.util import ba2int

from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits

MBXMLToken_Value: Type = Union[str, int, float, tuple, bytes, None]


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
    CIRCLE_2D = -0x03
    """
    Special structure that is serialized specially [lat 4 octets | lon 4 octets | radius 2 octets ufloatvar ]
    """
    CIRCLE_3D = -0x04
    """
    Special structure that is serialized specially [lat 4 octets | lon 4 octets | radius 2 octets ufloatvar ]
    """
    INFO_TIME = -0x05
    """
    5 byte opaque value encoding date+time
    """
    POINT_2D = -0x06
    """
    Special structure [lat 4 octets | lon 4 octets]
    """
    POINT_3D = -0x07
    """
    Special structure [lat 4 octets | lon 4 octets | altitude sfloatvar ]
    """
    POINT_3D_WITH_ACC = -0x08
    """
    Special structure [lat 4 octets | lon 4 octets | altitude sfloatvar | altitude-acc ufloatvar ]
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

    # fmt:off
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
    LRRP_TriggeredLocationStopRequest_NCDT = (0x0F, True, "Triggered-Location-Stop-Request")
    LRRP_TriggeredLocationStopAnswer = (0x10, False, "Triggered-Location-Stop-Answer")
    LRRP_TriggeredLocationStopAnswer_NCDT = (0x11, True, "Triggered-Location-Stop-Answer")
    LRRP_UnsolicitedLocationReport = (0x12, False, "Location-Protocol-Report")
    LRRP_UnsolicitedLocationReport_NCDT = (0x13, True, "Location-Protocol-Report")
    LRRP_LocationProtocolRequest_NCDT = (0x14, True, "Location-Protocol-Request")
    LRRP_LocationProtocolReport_NCDT = (0x15, True, "Location-Protocol-Report")
    # ARRP = Accessories Request/Response Protocol
    ARRP_ImmediateInformationRequest = (0x16, False, "")
    ARRP_ImmediateInformationRequest_NCDT = (0x17, True, "")
    ARRP_ImmediateInformationReport = (0x18, False, "")
    ARRP_ImmediateInformationReport_NCDT = (0x19, True, "")
    ARRP_TriggeredInformationRequest = (0x1A, False, "")
    ARRP_TriggeredInformationRequest_NCDT = (0x1B, True, "")
    ARRP_TriggeredInformationAnswer = (0x1C, False, "")
    ARRP_TriggeredInformationAnswer_NCDT = (0x1D, True, "")
    ARRP_TriggeredInformationReport = (0x1E, False, "")
    ARRP_TriggeredInformationReport_NCDT = (0x1F, True, "")
    ARRP_TriggeredInformationStopRequest = (0x20, False, "")
    ARRP_TriggeredInformationStopRequest_NCDT = (0x21, True, "")
    ARRP_TriggeredInformationStopAnswer = (0x22, False, "")
    ARRP_TriggeredInformationStopAnswer_NCDT = (0x23, True, "")
    ARRP_UnsolicitedInformationReport = (0x24, False, "")
    ARRP_UnsolicitedInformationReport_NCDT = (0x25, True, "")
    ARRP_InformationProtocolRequest_NCDT = (0x26, True, "")
    ARRP_InformationProtocolReport_NCDT = (0x27, True, "")

    # fmt:on

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
        value: Optional[MBXMLToken_Value] = None,
        constant_position: Optional[int] = None,
    ) -> None:
        self.name: str = name
        self.token_type: GlobalToken = _type
        self.token_id: int = token_id
        self.last_attribute: bool = last_attribute
        self.attributes: List[Union[int, MBXMLToken]] = attributes or []
        self.length: Optional[int] = length
        self.path: Optional[str] = path
        self.value: Optional[MBXMLToken_Value] = value
        self.constant_position: Optional[int] = constant_position

    def get_value(self, doc: "MBXMLDocument") -> MBXMLToken_Value:
        if self.token_type in (GlobalToken.STR8_ST, GlobalToken.OPAQUE_T):
            (val, idx) = MBXML.read_opaque(doc.constants_table, self.value)
            return val.decode("ascii")
        elif isinstance(self.value, bytes):
            return self.value.hex().upper()
        elif self.token_type in (GlobalToken.SFLOATVAR, GlobalToken.UFLOATVAR):
            return round(self.value, 5)
        return self.value

    def get_attributes(self, doc: "MBXMLDocument") -> Dict[str, str]:
        """
        Will return dictionary of attributes {attr name => value}
        """
        rtn: Dict[str, str] = {}
        for attr_id in self.attributes:
            if isinstance(attr_id, int):
                attr_def = doc.attributes_config[attr_id]
                rtn[attr_def.name] = attr_def.get_value(doc)
            elif isinstance(attr_id, MBXMLToken):
                rtn[attr_id.name] = attr_id.value

        return rtn

    def as_xml(
        self,
        document: minidom.Document,
        root: minidom.Element,
        mbxml_document: "MBXMLDocument",
    ):
        part_element: minidom.Element = document.createElement(self.name)

        if self.token_type == GlobalToken.CIRCLE_2D:
            lat_el: minidom.Element = document.createElement("lat")
            long_el: minidom.Element = document.createElement("long")
            radius_el: minidom.Element = document.createElement("radius")

            (_lat, _long, _radius) = self.value
            _lat = int.from_bytes(_lat, byteorder="big")
            _long = int.from_bytes(_long, byteorder="big")

            lat_el.appendChild(
                document.createTextNode(str(round((_lat * 90) / 2**31, 6)))
            )
            long_el.appendChild(
                document.createTextNode(str(round((_long * 360) / 2**32, 6)))
            )
            radius_el.appendChild(document.createTextNode(str(round(_radius, 2))))

            part_element.appendChild(lat_el)
            part_element.appendChild(long_el)
            part_element.appendChild(radius_el)
        elif self.token_type == GlobalToken.POINT_2D:
            (_lat, _long) = self.value

            lat_el: minidom.Element = document.createElement("lat")
            long_el: minidom.Element = document.createElement("long")

            _lat = int.from_bytes(_lat, byteorder="big")
            _long = int.from_bytes(_long, byteorder="big")

            lat_el.appendChild(
                document.createTextNode(str(round((_lat * 90) / 2**31, 6)))
            )
            long_el.appendChild(
                document.createTextNode(str(round((_long * 360) / 2**32, 6)))
            )

            part_element.appendChild(lat_el)
            part_element.appendChild(long_el)

        elif self.token_type == GlobalToken.POINT_3D:
            (_lat, _long, _altitude) = self.value

            lat_el: minidom.Element = document.createElement("lat")
            long_el: minidom.Element = document.createElement("long")
            alt_el: minidom.Element = document.createElement("altitude")

            _lat = int.from_bytes(_lat, byteorder="big")
            _long = int.from_bytes(_long, byteorder="big")

            lat_el.appendChild(
                document.createTextNode(str(round((_lat * 90) / 2**31, 6)))
            )
            long_el.appendChild(
                document.createTextNode(str(round((_long * 360) / 2**32, 6)))
            )
            alt_el.appendChild(document.createTextNode(str(_altitude)))

            part_element.appendChild(lat_el)
            part_element.appendChild(long_el)
            part_element.appendChild(alt_el)

        elif self.token_type == GlobalToken.INFO_TIME:
            bits = bytes_to_bits(self.value)
            part_element.appendChild(
                document.createTextNode(
                    f"{ba2int(bits[0:-26]):4}"
                    f"{ba2int(bits[-26:-22]):02}"
                    f"{ba2int(bits[-22:-17]):02}"
                    f"{ba2int(bits[-17:-12]):02}"
                    f"{ba2int(bits[-12:-6]):02}"
                    f"{ba2int(bits[-6:]):02}"
                )
            )
        else:
            val: Optional[MBXMLToken_Value] = self.get_value(mbxml_document)
            if val:
                part_value: minidom.Text = document.createTextNode(str(val))
                part_element.appendChild(part_value)
            for attr_name, attr_value in self.get_attributes(mbxml_document).items():
                part_element.setAttribute(attr_name, str(attr_value))

        parent = root

        if isinstance(self.path, str) and len(self.path) > 1:
            for path_part in self.path.split("."):
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
                    _elm = document.createElement(path_part)
                    parent.appendChild(_elm)
                    parent = _elm

        parent.appendChild(part_element)

    def __str__(self) -> str:
        return f"[{self.name} is {self.token_type.name} ({hex(self.token_id)})]"

    def __repr__(self) -> str:
        repre: str = f"[{self.token_type.name} {self.name} ({hex(self.token_id)})]"
        if self.value:
            repre += f" [VAL: {self.value.hex() if isinstance(self.value, bytes) else self.value}]"
        for attr in self.attributes:
            if isinstance(attr, MBXMLToken):
                repre += "\n\t" + repr(attr)
        return repre


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

    @staticmethod
    def get_configuration(
        doc_type: MBXMLDocumentIdentifier,
    ) -> Dict[MBXMLTokenType, Dict[int, MBXMLToken]]:
        """
        In implementation (LRRP, ARRP, ...) this should return configuration dictionary appropriate for given doc_type

        structure should always look like this
        {
          MBXMLTokenType.ELEMENT_TOKEN: Dict[int, MBXMLToken],
          MBXMLTokenType.CONSTANT_TOKEN: Dict[int, MBXMLToken],
          MBXMLTokenType.ATTRIBUTE_TOKEN: Dict[int, MBXMLToken]
        }
        """

    def as_xml(self) -> str:
        document: minidom.Document = minidom.Document()

        root: minidom.Element = document.createElement(
            self.id.value[2] or "Unknown-XML-Root-Element"
        )
        document.appendChild(root)

        for part in self.parts:
            part.as_xml(root=root, document=document, mbxml_document=self)

        return document.toprettyxml(indent="\t")

    @classmethod
    def get_known_tokens(cls, is_request: bool = True) -> List[Dict[int, MBXMLToken]]:
        """
        Return list of dictionaries of known tokens, reflecting on whether those are meant for request or response (is_request)
        """

    @classmethod
    def get_known_attributes(
        cls, is_request: bool = True
    ) -> List[Dict[int, MBXMLToken]]:
        """
        Returns list of dictionaries of known attributes, reflecting on whether those are meant for request or response (is_request)
        """

    @classmethod
    def get_token(
        cls,
        name: Union[str, int],
        value: Optional[MBXMLToken_Value],
        attributes: Dict[Union[int, str], MBXMLToken_Value],
        is_request: bool = True,
    ) -> MBXMLToken:
        """
        attributes can be specified as name=>value or id=>value
        """
        tokens = cls.get_known_tokens(is_request=is_request)
        for tokenset in tokens:
            for (tokendef_id, tokendef_setting) in tokenset.items():

                valid_candidate: bool = (
                    tokendef_setting.name == name
                    if isinstance(name, str)
                    else tokendef_id == name
                )
                attributes_to_set: List[MBXMLToken] = list()

                if valid_candidate:
                    # verify found token has required attributes
                    for (attr_key, attr_val) in attributes.items():
                        (attr_copy, value_changed) = cls.get_attribute(
                            name=attr_key, value=attr_val
                        )
                        if attr_copy.token_id not in tokendef_setting.attributes:
                            valid_candidate = False
                            break
                        elif value_changed:
                            attributes_to_set.append(attr_copy)

                if valid_candidate:
                    t: MBXMLToken = copy(tokendef_setting)
                    t.token_id = tokendef_id
                    t.value = value

                    for attr_inst in attributes_to_set:
                        # remove attr id from list
                        t.attributes.remove(attr_inst.token_id)
                        # put attr instance
                        t.attributes.append(attr_inst)

                    return t

        raise ModuleNotFoundError(
            f"MBXMLToken (get_token) {name} with attributes {attributes.keys()} not found"
        )

    @classmethod
    def get_attribute(
        cls,
        name: Union[str, int],
        value: Optional[MBXMLToken_Value],
        is_request: bool = True,
    ) -> (MBXMLToken, bool):
        """
        Returns token (if found, otherwise raises ModuleNotFoundError) and bool indication, whether the value is different from default (implied) one
        """
        attrs = cls.get_known_attributes(is_request=is_request)
        for attrset in attrs:
            for (attrdef_id, attrdef_setting) in attrset.items():
                if (
                    attrdef_setting.name == name
                    if isinstance(name, str)
                    else attrdef_id == name
                ):
                    if (
                        attrdef_setting.value is not None
                        and attrdef_setting.value != value
                    ):
                        # skip attributes when they have pre-set value, and it does not match the expected value
                        continue
                    a: MBXMLToken = copy(attrdef_setting)
                    a.token_id = attrdef_id
                    a.value = value
                    return a, (value is not None and value != attrdef_setting.value)

        raise ModuleNotFoundError(
            f"MBXMLToken (get_attribute) {name} with value {value} not found"
        )


class MBXML:
    """
    Utility class to serialize (as_bytes) and de-serialize (from_bytes) MBXML documents
    """

    UINTVAR_MAX: int = 4294967295
    SINTVAR_MAX: int = 2147483647
    DEBUG: bool = False

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
    def read_sintvar(cls, data: bytes, idx: int) -> Tuple[int, int, int]:
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

        return (sintvar * sign), idx, sign

    @classmethod
    def write_sintvar(cls, value: int, negative_zero: bool = False) -> bytes:
        """
        write sintvar and return bytes representation
        """
        assert abs(value) <= cls.SINTVAR_MAX, (
            f"write_sintvar cannot write integers bigger than {cls.SINTVAR_MAX} "
            f"(or smaller than -{cls.SINTVAR_MAX}"
        )
        sintvar: bytes = cls.write_uintvar(abs(value))
        return (
            sintvar
            if value >= 0 and not negative_zero
            else (bytes([sintvar[0] | 0x40]) + sintvar[1:])
        )

    @classmethod
    def read_ufloatvar(cls, data: bytes, idx: int) -> Tuple[float, int]:
        """
        read ufloatvar from data[idx] on, return (float value, new idx)
        """
        (integer, idx) = cls.read_uintvar(data, idx)
        (decimal, idx_2) = cls.read_uintvar(data, idx)
        return (integer + (decimal / 128 ** (idx_2 - idx))), idx_2

    @classmethod
    def read_uint8(cls, data: bytes, idx: int) -> Tuple[int, int]:
        """
        Read single byte and return as unsigned value
        """
        uint = int.from_bytes(data[idx : idx + 1], byteorder="big", signed=False)
        return uint, idx + 1

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
        (integer, idx, sign) = cls.read_sintvar(data, idx)
        (decimal, idx_2) = cls.read_uintvar(data, idx)
        return (
            math.copysign((abs(integer) + (decimal / 128 ** (idx_2 - idx))), sign),
            idx_2,
        )

    @classmethod
    def write_sfloatvar(cls, value: float, precision: int) -> bytes:
        assert precision >= 1, f"write_sfloatvar precision must be at least 1 decimal"
        int_part = int(value)
        dec_part = int(abs(value % (1 if value >= 0 else -1)) * 128**precision)
        integer = cls.write_sintvar(int_part, negative_zero=value < 0)
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
    def read_opaque_defined_size(
        cls, data: bytes, idx: int, size: int
    ) -> Tuple[bytes, int]:
        """
        Just read number of bytes and move the pointer
        """
        return data[idx : idx + size], idx + size

    @classmethod
    def write_latitude(cls, value: float) -> bytes:
        """
        Results in 4 bytes of opaque data for Latitude token
        """
        if math.isclose(value, 90.0):
            value = int(2**31 - 1)
        else:
            value = int((round(value, 6) * (2**31)) / 90)

        return value.to_bytes(length=4, byteorder="big")

    @classmethod
    def write_longitude(cls, value: float) -> bytes:
        """
        Results in 4 bytes of opaque data for Longitude token
        """
        return int((round(value, 6) * (2**32)) / 360).to_bytes(
            length=4, byteorder="big"
        )

    @classmethod
    def write_infotime(cls, value: Union[datetime, str, int]) -> bytes:
        """
        Results in 5 bytes of opaque data for date+time information
        """
        # if provided int, get string value
        if isinstance(value, int):
            value = str(value)

        if isinstance(value, str):
            assert (
                len(value) == 14
            ), f"formatted infotime value shall be 14 numbers (eg. 20030630073000) got {value} of len {len(value)}"
            value = datetime.strptime(value, "%Y%m%d%H%M%S")

        assert isinstance(
            value, datetime
        ), f"datetime.datetime expected at this point, got {type(value)}"

        return int(
            value.year * 2**26
            + value.month * 2**22
            + value.day * 2**17
            + value.hour * 2**12
            + value.minute * 2**6
            + value.second
        ).to_bytes(byteorder="big", length=5)

    @classmethod
    def read_document(
        cls, doctype: MBXMLDocumentIdentifier, data: bytes, idx: int
    ) -> MBXMLDocument:
        doctype_configuration = cls.get_implementation(doctype).get_configuration(
            doctype
        )
        (document_id, has_no_constants_table, _) = doctype.value
        doc = MBXMLDocument(
            document_id=doctype,
            elements_config=doctype_configuration[MBXMLTokenType.ELEMENT_TOKEN],
            attributes_config=doctype_configuration[MBXMLTokenType.ATTRIBUTE_TOKEN],
        )
        if cls.DEBUG:
            print(repr(doc))

        if not has_no_constants_table:
            # fill in constants, if indicated
            (constants, idx) = cls.read_opaque(data, idx)
            doc.constants_table = constants
        elif MBXMLTokenType.CONSTANT_TOKEN in doctype_configuration:
            doc.set_default_constants_table(
                doctype_configuration[MBXMLTokenType.CONSTANT_TOKEN]
            )

        _lastidx = 0
        while idx != len(data):
            _lastidx = copy(idx)
            (token_id, idx) = cls.read_uintvar(data, idx)
            if cls.DEBUG:
                print(
                    f"token {token_id} in hex {hex(token_id)} data[{_lastidx}:{idx}]={data[_lastidx:idx].hex()}"
                )
            token_config: MBXMLToken = copy(
                doctype_configuration[MBXMLTokenType.ELEMENT_TOKEN][token_id]
            )
            token_config.token_id = token_id
            if cls.DEBUG:
                print(f"read_document token {token_config}")
                # print(repr(doc))

            if token_config.token_type == GlobalToken.OPAQUE_I:
                if token_config.length:
                    (token_config.value, idx) = cls.read_opaque_defined_size(
                        data, idx, token_config.length
                    )
                elif token_config.length != 0 and len(token_config.attributes):
                    newattrs = []
                    for attr_id in token_config.attributes:
                        attr_config = copy(
                            doctype_configuration[MBXMLTokenType.ATTRIBUTE_TOKEN][
                                attr_id
                            ]
                        )
                        (attr_config.value, idx) = cls.read_uintvar(data, idx)
                        newattrs.append(attr_config)
                    token_config.attributes = newattrs
                    (token_config.value, idx) = cls.read_opaque(data, idx)
                elif token_config.length == 0:
                    token_config.value = b""
                else:
                    (token_config.value, idx) = cls.read_opaque(data, idx)
            elif token_config.token_type == GlobalToken.INFO_TIME:
                (token_config.value, idx) = cls.read_opaque_defined_size(data, idx, 5)
            elif token_config.token_type == GlobalToken.UINT8:
                (token_config.value, idx) = cls.read_uint8(data, idx)
            elif token_config.token_type == GlobalToken.NO_VALUE:
                pass
            elif token_config.token_type == GlobalToken.UFLOATVAR:
                (token_config.value, idx) = cls.read_ufloatvar(data, idx)
            elif token_config.token_type == GlobalToken.SFLOATVAR:
                (token_config.value, idx) = cls.read_sfloatvar(data, idx)
            elif token_config.token_type == GlobalToken.UINTVAR:
                (token_config.value, idx) = cls.read_uintvar(data, idx)
            elif token_config.token_type == GlobalToken.CIRCLE_2D:
                (lat, idx) = cls.read_opaque_defined_size(data, idx, 4)
                (long, idx) = cls.read_opaque_defined_size(data, idx, 4)
                (radius, idx) = cls.read_ufloatvar(data, idx)
                token_config.value = (lat, long, radius)
            elif token_config.token_type == GlobalToken.POINT_2D:
                (lat, idx) = cls.read_opaque_defined_size(data, idx, 4)
                (long, idx) = cls.read_opaque_defined_size(data, idx, 4)
                token_config.value = (lat, long)
            elif token_config.token_type == GlobalToken.POINT_3D:
                (lat, idx) = cls.read_opaque_defined_size(data, idx, 4)
                (long, idx) = cls.read_opaque_defined_size(data, idx, 4)
                (altitude, idx) = cls.read_sfloatvar(data, idx)
                token_config.value = (lat, long, altitude)
            else:
                raise ValueError(
                    f"read_document not implemented for config {token_config}"
                )

            doc.parts.append(token_config)

        return doc

    @classmethod
    def write_part(cls, part: MBXMLToken) -> bytes:
        if part.token_type == GlobalToken.OPAQUE_I:
            if part.length:
                return bytes([part.token_id]) + part.value
            else:
                attributes: bytes = b""
                for attr in part.attributes:
                    if isinstance(attr, MBXMLToken):
                        attributes += cls.write_uintvar(attr.value)

                return (
                    bytes([part.token_id])
                    + attributes
                    + (
                        (cls.write_uintvar(len(part.value)) + part.value)
                        if len(part.value)
                        else b""
                    )
                )
        elif part.token_type == GlobalToken.UINTVAR:
            return bytes([part.token_id]) + cls.write_uintvar(part.value)
        elif part.token_type == GlobalToken.INFO_TIME:
            return bytes([part.token_id]) + part.value
        elif part.token_type == GlobalToken.POINT_2D:
            (lat, lon) = part.value
            return bytes([part.token_id]) + lat + lon
        elif part.token_type == GlobalToken.POINT_3D:
            (lat, lon, alt) = part.value
            return bytes([part.token_id]) + lat + lon + cls.write_sfloatvar(alt, 1)
        elif part.token_type == GlobalToken.NO_VALUE:
            return bytes([part.token_id])
        elif part.token_type == GlobalToken.UINT8:
            return bytes([part.token_id]) + int(part.value).to_bytes(
                length=1, byteorder="big", signed=False
            )
        elif part.token_type == GlobalToken.STR8_I:
            return (
                bytes([part.token_id])
                + cls.write_uintvar(len(part.value))
                + part.value.encode("ascii")
            )
        elif part.token_type == GlobalToken.UFLOATVAR:
            return bytes([part.token_id]) + cls.write_ufloatvar(part.value, 1)
        elif part.token_type == GlobalToken.SFLOATVAR:
            return bytes([part.token_id]) + cls.write_sfloatvar(part.value, 1)
        elif part.token_type == GlobalToken.CIRCLE_2D:
            (lat, long, radius) = part.value
            return bytes([part.token_id]) + lat + long + cls.write_ufloatvar(radius, 1)

        raise ValueError(f"write_part not implemented for {part.token_type}")

    @classmethod
    def get_implementation(
        cls, doc_type: MBXMLDocumentIdentifier
    ) -> Type[MBXMLDocument]:
        """
        This just proxies classes implementing different MBXML-represented protocols
        """
        prefix: str = doc_type.name[0:4]
        if prefix == "LRRP":
            from okdmr.dmrlib.motorola.lrrp import LRRP

            return LRRP
        elif prefix == "ARRP":
            from okdmr.dmrlib.motorola.arrp import ARRP

            return ARRP

        print(f"get_implementation returns default for {doc_type}")
        return MBXMLDocument

    @classmethod
    def build_constants_table(cls, document_type: MBXMLDocumentIdentifier):
        impl = cls.get_implementation(doc_type=document_type)
        values: Dict[int, MBXMLToken] = impl.get_configuration(doc_type=document_type)[
            MBXMLTokenType.CONSTANT_TOKEN
        ]
        tbl = b""
        for i in range(0, len(values)):
            # strip first byte which marks type of value, CDT contains only LV (from TLV, missing TYPE indication uintvar)
            tbl += cls.write_part(values[i])[1:]
        return tbl

    @classmethod
    def from_bytes(cls, data: bytes, debug: bool = False) -> List["MBXMLDocument"]:
        """
        Parse bytes and return all found de-serialized documents
        """
        cls.DEBUG = debug
        data_len = len(data)
        rtn: List[MBXMLDocument] = []

        if cls.DEBUG:
            print(f"MBXML.from_bytes {data.hex()}")

        idx: int = 0
        while True:
            (doc_id, idx) = cls.read_uintvar(data, idx)
            doctype = MBXMLDocumentIdentifier.resolve(doc_id)
            (doc_len_bytes, idx) = cls.read_uintvar(data, idx)
            rtn.append(cls.read_document(doctype, data, idx))
            idx += doc_len_bytes
            if idx == data_len:
                break

        cls.DEBUG = False
        return rtn

    @classmethod
    def as_bytes(cls, doc: MBXMLDocument) -> bytes:
        rtn = cls.write_uintvar(doc.id.value[0])

        body = b""
        for part in doc.parts:
            body += cls.write_part(part)

        return rtn + cls.write_uintvar(len(body)) + body
