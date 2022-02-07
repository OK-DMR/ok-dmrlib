from okdmr.dmrlib.etsi.layer3.elements.service_options import ServiceOptions


def test_service_options_bits():
    e = ServiceOptions(
        is_emergency=True,
        is_broadcast=False,
        priority_level=1,
        is_open_voice_call_mode=False,
    )
    assert e.as_bits() == ServiceOptions.from_bits(e.as_bits()).as_bits()
