from pprint import pprint

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
