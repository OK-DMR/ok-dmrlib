from typing import Optional

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer3.elements.ip_address_identifier import IPAddressIdentifier
from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)
from okdmr.dmrlib.motorola.text_messaging_service import (
    TextMessagingService,
    TMSPDUType,
    FirstHeader,
)
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


def test_extended_headers():
    both: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader.from_bits(
        bitarray("0" * 72)
    )
    assert both.extended_header_2 is not None
    assert both.extended_header_1 is not None
    assert both.as_bits() == bitarray("0" * 72)

    single: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader.from_bits(
        bitarray("0" * 31 + "1" + "0" * 40)
    )
    assert single.extended_header_1 is not None
    assert single.extended_header_2 is None
    assert single.as_bits() == bitarray("0" * 31 + "1" + "0" * 40)


def test_reconstruct(do_return: bool = False) -> Optional[UDPIPv4CompressedHeader]:
    msg_bytes: bytes = bytes.fromhex("d6790062620003bf0007")
    msg_pdu: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader.from_bytes(msg_bytes)
    assert msg_pdu.as_bytes() == msg_bytes

    tms: TextMessagingService = TextMessagingService(
        first_header=FirstHeader(
            pdu_type=TMSPDUType.TMS_ACKNOWLEDGEMENT,
            is_reserved=True,
        ),
        sequence_number=7,
    )
    assert tms.as_bytes() == msg_bytes[5:]
    pdu0: UDPIPv4CompressedHeader = UDPIPv4CompressedHeader(
        ipv4_identification=54905,
        user_data=bytes_to_bits(tms.as_bytes()),
        udp_source_port_id=98,
        udp_destination_port_id=98,
        source_ip_address_id=IPAddressIdentifier.RadioNetwork,
        destination_ip_address_id=IPAddressIdentifier.RadioNetwork,
    )
    assert pdu0.as_bytes() == msg_bytes
    return pdu0 if do_return else None
