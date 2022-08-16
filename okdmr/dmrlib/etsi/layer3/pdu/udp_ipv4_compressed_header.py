from typing import Union, Optional

from bitarray import bitarray
from bitarray.util import ba2int

from okdmr.dmrlib.etsi.layer3.elements.ip_address_identifier import IPAddressIdentifier
from okdmr.dmrlib.etsi.layer3.elements.udp_port_identifier import UDPPortIdentifier
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class UDPIPv4CompressedHeader(BitsInterface):
    def __init__(
        self,
        ipv4_identification: int,
        source_ip_address_id: Union[IPAddressIdentifier, int],
        destination_ip_address_id: Union[IPAddressIdentifier, int],
        udp_source_port_id: Union[UDPPortIdentifier, int],
        udp_destination_port_id: Union[UDPPortIdentifier, int],
        user_data: bitarray,
        extended_header_1: Optional[int] = None,
        extended_header_2: Optional[int] = None,
    ):
        self.ipv4_identification: int = ipv4_identification
        self.source_ip_address_id: IPAddressIdentifier = (
            source_ip_address_id
            if isinstance(source_ip_address_id, IPAddressIdentifier)
            else IPAddressIdentifier(source_ip_address_id)
        )
        self.destination_ip_address_id: IPAddressIdentifier = (
            destination_ip_address_id
            if isinstance(destination_ip_address_id, IPAddressIdentifier)
            else IPAddressIdentifier(destination_ip_address_id)
        )
        self.udp_source_port_id: UDPPortIdentifier = (
            udp_source_port_id
            if isinstance(udp_source_port_id, UDPPortIdentifier)
            else UDPPortIdentifier(udp_source_port_id)
        )
        self.udp_destination_port_id: UDPPortIdentifier = (
            udp_destination_port_id
            if isinstance(udp_destination_port_id, UDPPortIdentifier)
            else UDPPortIdentifier(udp_destination_port_id)
        )
        self.user_data: bitarray = user_data
        self.extended_header_1: Optional[int] = extended_header_1
        self.extended_header_2: Optional[int] = extended_header_2

    def __repr__(self) -> str:
        return (
            f"[IPv4 id: {self.ipv4_identification}] "
            f"[IP src: {self.source_ip_address_id}] "
            f"[IP dst: {self.destination_ip_address_id}] "
            f"[UDP src: {self.udp_source_port_id}] "
            f"[UDP dst: {self.udp_destination_port_id}] "
            + (
                f"[extended header 1 {self.extended_header_1}] "
                if self.extended_header_1
                else ""
            )
            + (
                f"[extended header 2 {self.extended_header_2}] "
                if self.extended_header_2
                else ""
            )
            + f" [DATA: {bits_to_bytes(self.user_data).hex()}] "
        )

    @staticmethod
    def from_bits(bits: bitarray) -> "UDPIPv4CompressedHeader":
        assert (
            len(bits) >= 40
        ), f"UDP/IPv4 compressed header must be at least 40 bits, got {len(bits)} instead"
        spid = UDPPortIdentifier.from_bits(bits[25:32])
        dpid = UDPPortIdentifier.from_bits(bits[33:40])
        e1: Optional[int] = None
        e2: Optional[int] = None
        data_start: int = 40

        if (
            spid == UDPPortIdentifier.InExtendedHeader
            and dpid == UDPPortIdentifier.InExtendedHeader
        ):
            # both udp port numbers are in extended headers
            e1 = ba2int(bits[data_start : data_start + 16])
            e2 = ba2int(bits[data_start + 16 : data_start + 32])
            data_start += 32
        elif (
            spid == UDPPortIdentifier.InExtendedHeader
            or dpid == UDPPortIdentifier.InExtendedHeader
        ):
            # single udp port id is in extended header
            e1 = ba2int(bits[data_start : data_start + 16])
            data_start += 16

        return UDPIPv4CompressedHeader(
            ipv4_identification=ba2int(bits[0:16]),
            source_ip_address_id=ba2int(bits[16:20]),
            destination_ip_address_id=ba2int(bits[20:24]),
            udp_source_port_id=spid,
            udp_destination_port_id=dpid,
            extended_header_1=e1,
            extended_header_2=e2,
            user_data=bits[data_start:],
        )
