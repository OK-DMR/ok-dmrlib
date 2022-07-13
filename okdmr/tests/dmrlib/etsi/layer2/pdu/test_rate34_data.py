from bitarray import bitarray

from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34Data, Rate34DataTypes


def test_rate34_data():
    # R_3_4_DATA PDU content for unconfirmed data
    r34u: Rate34Data = Rate34Data(
        data=b"\xdd\xda\xe4\xa1\xaeT'oe\xc9\xf6\xe4\x97\x0e#\xed\x17s"
    )
    r34u_bits = r34u.as_bits()
    assert (
        Rate34Data.from_bits_typed(
            r34u_bits, data_type=Rate34DataTypes.Unconfirmed
        ).as_bits()
        == r34u_bits
    )
    assert len(repr(r34u))

    r34c: Rate34Data = Rate34Data(
        data=b"\xc1\x1bb\x1a\xd4\x8b\x97\x91\x17A\x9e\xb1r\xeb\xe0\xb8",
        dbsn=1,
        crc9=173,
    )
    r34c_bits = r34c.as_bits()
    assert r34c.crc9_ok
    assert r34c.is_confirmed()
    assert (
        Rate34Data.from_bits_typed(
            r34c_bits, data_type=Rate34DataTypes.Confirmed
        ).as_bits()
        == r34c_bits
    )
    assert len(repr(r34c))

    r34ul: Rate34Data = Rate34Data(
        data=b"\x90\xbc\x85\x00\x89\xc1[K\xe4l\x83P\x88\xe0", crc32=b"\xdb\xb2p\xe5"
    )
    r34ul_bits = r34ul.as_bits()
    assert r34ul.is_last_block()
    assert (
        Rate34Data.from_bits_typed(
            r34ul_bits, data_type=Rate34DataTypes.UnconfirmedLastBlock
        ).as_bits()
        == r34ul_bits
    )
    assert len(repr(r34ul))

    r34cl: Rate34Data = Rate34Data(
        data=b"\xfe\x1ey\x9cR\xb5\xe4&T\xc2#\x83", dbsn=1, crc32=b'\x12"\x18N', crc9=205
    )
    r34cl_bits = r34cl.as_bits()
    assert r34cl.is_confirmed()
    assert r34cl.is_last_block()
    assert (
        Rate34Data.from_bits_typed(
            r34cl_bits, data_type=Rate34DataTypes.ConfirmedLastBlock
        ).as_bits()
        == r34cl_bits
    )
    assert r34cl.crc9_ok
    assert len(repr(r34cl))

    assert (
        r34cl_bits
        == r34cl.convert(Rate34DataTypes.UnconfirmedLastBlock).as_bits()
        == r34cl.convert(Rate34DataTypes.Unconfirmed).as_bits()
    )
    assert (
        r34c_bits
        == r34c.convert(Rate34DataTypes.Unconfirmed)
        .convert(Rate34DataTypes.Confirmed)
        .as_bits()
    )


def test_rate34_data_types():
    assert (
        Rate34DataTypes.resolve(confirmed=True, last=True)
        == Rate34DataTypes.ConfirmedLastBlock
    )
    assert Rate34DataTypes(0) == Rate34DataTypes.Undefined


def test_rate34_conversion():
    bits: bitarray = bitarray(
        "000000000001011101000101000000000000000000101110111111111111111100000000000000000100000000010001111100100111111100001100001000110011011111111100"
    )
    r34_confirmed: Rate34Data = Rate34Data.from_bits_typed(
        bits=bits, data_type=Rate34DataTypes.Confirmed
    )
    calculated: int = CRC9.calculate_from_parts(
        data=r34_confirmed.data,
        serial_number=r34_confirmed.dbsn,
        mask=CrcMasks.Rate34DataContinuation,
    )
    assert calculated == r34_confirmed.calculate_crc9()
