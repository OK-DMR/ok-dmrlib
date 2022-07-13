from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data, Rate12DataTypes


def test_rate12_data():
    r12u: Rate12Data = Rate12Data(data=b"\xc0K;\xb7NN\x83\xb5\xc9\x01\x03\xcb")
    r12u_bits = r12u.as_bits()
    assert len(repr(r12u))
    assert (
        Rate12Data.from_bits_typed(
            r12u_bits, data_type=Rate12DataTypes.Unconfirmed
        ).as_bits()
        == r12u_bits
    )

    r12c: Rate12Data = Rate12Data(data=b"t~\xa3B5\xcc\xc4JwK", dbsn=1, crc9=69)
    r12c_bits = r12c.as_bits()
    assert r12c.crc9_ok
    assert r12c.is_confirmed()
    assert (
        Rate12Data.from_bits_typed(
            r12c_bits, data_type=Rate12DataTypes.Confirmed
        ).as_bits()
        == r12c_bits
    )
    assert len(repr(r12c))

    r12ul: Rate12Data = Rate12Data(
        data=b"y\x02\xe8\xf3c\xc3\x82\x88", crc32=b"\n\xfc\xb3\xe1"
    )
    r12ul_bits = r12ul.as_bits()
    assert r12ul.is_last_block()
    assert (
        Rate12Data.from_bits_typed(
            r12ul_bits, data_type=Rate12DataTypes.UnconfirmedLastBlock
        ).as_bits()
        == r12ul_bits
    )
    assert len(repr(r12ul))

    r12cl: Rate12Data = Rate12Data(
        data=b"\xaf\x12\xf4O\xdeK", crc32=b"\x82j\xfdX", dbsn=1, crc9=84
    )
    r12cl_bits = r12cl.as_bits()
    assert r12cl.is_last_block()
    assert r12cl.is_confirmed()
    assert r12cl.crc9_ok
    assert len(repr(r12cl))
    assert (
        Rate12Data.from_bits_typed(
            r12cl_bits, Rate12DataTypes.ConfirmedLastBlock
        ).as_bits()
        == r12cl_bits
    )

    assert (
        r12cl_bits
        == r12cl.convert(Rate12DataTypes.UnconfirmedLastBlock).as_bits()
        == r12cl.convert(Rate12DataTypes.Unconfirmed).as_bits()
    )
    assert (
        r12c_bits
        == r12c.convert(Rate12DataTypes.Unconfirmed)
        .convert(Rate12DataTypes.Confirmed)
        .as_bits()
    )


def test_rate12_data_types():
    assert (
        Rate12DataTypes.resolve(confirmed=True, last=True)
        == Rate12DataTypes.ConfirmedLastBlock
    )
    assert Rate12DataTypes(0) == Rate12DataTypes.Undefined
