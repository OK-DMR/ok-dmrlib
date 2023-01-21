from okdmr.dmrlib.etsi.layer3.elements.talker_alias_data_format import (
    TalkerAliasDataFormat,
)


def test_encode_decode():
    test_str: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    utf8_bytes = TalkerAliasDataFormat.UnicodeUTF8.encode(test_str)
    utf16le_bytes = TalkerAliasDataFormat.UnicodeUTF16LE.encode(test_str)
    iso8859_bytes = TalkerAliasDataFormat.ISOEightBitCharacters.encode(test_str)
    iec646_bytes = TalkerAliasDataFormat.SevenBitCharacters.encode(test_str)

    assert TalkerAliasDataFormat.UnicodeUTF8.decode(utf8_bytes) == test_str
    assert TalkerAliasDataFormat.UnicodeUTF16LE.decode(utf16le_bytes) == test_str
    assert TalkerAliasDataFormat.ISOEightBitCharacters.decode(iso8859_bytes) == test_str
    assert TalkerAliasDataFormat.SevenBitCharacters.decode(iec646_bytes) == test_str
