from typing import List

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType


def test_encode_decode():
    hex_slottypes: List[str] = ["01010011111100101011"]
    for hex_slottype in hex_slottypes:
        original_bits: bitarray = bitarray(hex_slottype)
        slot: SlotType = SlotType.from_bits(original_bits)
        assert slot.check_parity(), "Parity does not match in test data"
        serialized_bits: bitarray = slot.as_bits()
        assert serialized_bits == original_bits
        reconstructed: SlotType = SlotType(
            colour_code=slot.colour_code, data_type=slot.data_type
        )
        assert original_bits == reconstructed.as_bits()
        print(reconstructed)
