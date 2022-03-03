from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.service_options import ServiceOptions


def test_service_options_bits():
    e = ServiceOptions(
        is_emergency=True,
        is_broadcast=False,
        priority_level=1,
        is_open_voice_call_mode=False,
        is_privacy=False,
    )
    assert e.as_bits() == ServiceOptions.from_bits(e.as_bits()).as_bits()


def test_reserved():
    # test that reserved bits are preserved if non-default value is provided
    payload: bitarray = bitarray("00110000")

    null_reserved: bitarray = bitarray(payload)
    null_reserved[2:4] = 0

    e = ServiceOptions.from_bits(payload)
    assert e.as_bits() != null_reserved
    assert e.as_bits() == payload
