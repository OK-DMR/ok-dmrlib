from typing import Dict


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
