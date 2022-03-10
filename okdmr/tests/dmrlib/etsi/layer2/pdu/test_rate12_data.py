from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data


def test_rate12_data():
    r12u: Rate12Data = Rate12Data(data=b"\xc0K;\xb7NN\x83\xb5\xc9\x01\x03\xcb")
    r12u_bits = r12u.as_bits()
    assert len(repr(r12u))
    assert Rate12Data.from_bits(r12u_bits).as_bits() == r12u_bits

    r12c: Rate12Data = Rate12Data(data=b"t~\xa3B5\xcc\xc4JwK", dbsn=1)
    r12c_bits = r12c.as_bits()
    assert r12c.crc9_ok
    assert Rate12Data.from_bits(r12c_bits).as_bits() == r12c_bits
    assert len(repr(r12c))

    r12ul: Rate12Data = Rate12Data(
        data=b"y\x02\xe8\xf3c\xc3\x82\x88", crc32=b"\n\xfc\xb3\xe1"
    )
    r12ul_bits = r12ul.as_bits()
    assert Rate12Data.from_bits(r12ul_bits).as_bits() == r12ul_bits
    assert len(repr(r12ul))

    r12cl: Rate12Data = Rate12Data(
        data=b"\xaf\x12\xf4O\xdeK", crc32=b"\x82j\xfdX", dbsn=1
    )
    r12cl_bits = r12cl.as_bits()
    assert r12cl.crc9_ok
    assert len(repr(r12cl))
    assert Rate12Data.from_bits(r12cl_bits).as_bits() == r12cl_bits
