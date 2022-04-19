from okdmr.dmrlib.etsi.layer2.pdu.rate1_data import Rate1Data, Rate1DataTypes


def test_rate12_data():
    r12u: Rate1Data = Rate1Data(
        data=b"\xe9\xdf\x9e\x0b\xff\xd3\xf0Y\xd1\x91\xd2\xf1\\\xee\x93\x81\x13]\\\xce\xff\x95\xd5\\"
    )
    r12u_bits = r12u.as_bits()
    assert len(repr(r12u))
    assert (
        Rate1Data.from_bits_typed(
            r12u_bits, data_type=Rate1DataTypes.Unconfirmed
        ).as_bits()
        == r12u_bits
    )

    r12c: Rate1Data = Rate1Data(
        data=b"SL\xe3\x18\x03\x8b\xf2\x85V\x9ex\x1f\n&\xe8\xcc\xf5o\xac\x97\xe2c",
        dbsn=1,
        crc9=225,
    )
    r12c_bits = r12c.as_bits()
    assert r12c.crc9_ok
    assert r12c.is_confirmed()
    assert (
        Rate1Data.from_bits_typed(
            r12c_bits, data_type=Rate1DataTypes.Confirmed
        ).as_bits()
        == r12c_bits
    )
    assert len(repr(r12c))

    r12ul: Rate1Data = Rate1Data(
        data=b"\xef\xc0\x1f\xafG__\x8a\xe3\xf7s\x0fx\x8f8\x89\x1c\x99>\x0b",
        crc32=b"\n\xfc\xb3\xe1",
    )
    r12ul_bits = r12ul.as_bits()
    assert r12ul.is_last_block()
    assert (
        Rate1Data.from_bits_typed(
            r12ul_bits, data_type=Rate1DataTypes.UnconfirmedLastBlock
        ).as_bits()
        == r12ul_bits
    )
    assert len(repr(r12ul))

    r12cl: Rate1Data = Rate1Data(
        data=b"*\xe2|\xff\xe8\x12\xa3\xea\xa3\xc4!;\xc0f\xdc}\xf9S",
        crc32=b"\x82j\xfdX",
        dbsn=1,
        crc9=285,
    )
    r12cl_bits = r12cl.as_bits()
    assert r12cl.is_last_block()
    assert r12cl.is_confirmed()
    assert r12cl.crc9_ok
    assert len(repr(r12cl))
    assert (
        Rate1Data.from_bits_typed(
            r12cl_bits, Rate1DataTypes.ConfirmedLastBlock
        ).as_bits()
        == r12cl_bits
    )

    assert (
        r12cl_bits
        == r12cl.convert(Rate1DataTypes.UnconfirmedLastBlock).as_bits()
        == r12cl.convert(Rate1DataTypes.Unconfirmed).as_bits()
    )
    assert (
        r12c_bits
        == r12c.convert(Rate1DataTypes.Unconfirmed)
        .convert(Rate1DataTypes.Confirmed)
        .as_bits()
    )


def test_rate12_data_types():
    assert (
        Rate1DataTypes.resolve(confirmed=True, last=True)
        == Rate1DataTypes.ConfirmedLastBlock
    )
    assert Rate1DataTypes(0) == Rate1DataTypes.Undefined
