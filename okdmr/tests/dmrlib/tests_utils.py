from pprint import pprint
from typing import Dict

from kaitaistruct import KaitaiStruct


def prettyprint(data: KaitaiStruct, stream=None) -> None:
    pprint(_prettyprint(data), stream=stream)


def _array_prettyprint(data: list) -> list:
    return list(
        map(
            lambda x: (
                _prettyprint(x)
                if isinstance(x, KaitaiStruct)
                else (_array_prettyprint(x) if isinstance(x, list) else x)
            ),
            data,
        )
    )


def _prettyprint(data: KaitaiStruct) -> dict:
    acceptable_items = {
        key: value
        for (key, value) in data.__dict__.items()
        if key not in ["_io", "_parent", "_root", "_debug"]
    }
    return {
        key: (
            _prettyprint(value)
            if isinstance(value, KaitaiStruct)
            else (_array_prettyprint(value) if isinstance(value, list) else value)
        )
        for (key, value) in acceptable_items.items()
    }


def assert_expected_attribute_values(obj: object, expectations: Dict[str, any]):
    for attrname, attrvalue in expectations.items():
        if isinstance(attrvalue, dict):
            assert_expected_attribute_values(
                getattr(obj, attrname), attrvalue
            ) if hasattr(obj, attrname) else None
        else:
            assert (
                getattr(obj, attrname) == attrvalue
            ), f"{obj} attribute {attrname} value ({getattr(obj, attrname)}) is incorrect, expected {attrvalue}"


class PrintEscapeBytes(bytes):
    def __str__(self):
        return "b'{}'".format("".join("\\x{:02x}".format(b) for b in self))
