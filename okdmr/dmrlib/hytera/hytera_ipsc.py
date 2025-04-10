from typing import Union

from okdmr.dmrlib.hytera.ipsc_elements.call_type import CallType
from okdmr.dmrlib.hytera.ipsc_elements.frame_type import FrameType
from okdmr.dmrlib.hytera.ipsc_elements.packet_type import PacketType
from okdmr.dmrlib.hytera.ipsc_elements.slot_type import SlotType
from okdmr.dmrlib.hytera.ipsc_elements.timeslot import Timeslot
from okdmr.dmrlib.utils.bits_bytes import byteswap_bytes, half_byte_to_bytes
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol


class HyteraIPSC:
    """
    Metaclass for all representations of IPSC transported messages (dmr data, ipsc wakeup, ipsc sync, ...)
    """

    DEFAULT_FIRST_HEADER: bytes = b"\x5a\x5a"
    DEFAULT_SECOND_HEADER: bytes = b"\x5a\x5a"
    DEFAULT_RESERVED_3: bytes = b"\x00\x00\x00"
    DEFAULT_RESERVED_7A: bytes = b"\x00\x05\x01\x01\x00\x00\x00"
    DEFAULT_RESERVED_2A: bytes = b"\x40\x00"
    DEFAULT_RESERVED_2B: bytes = b"\xe2\x08"
    DEFAULT_RESERVED_1: bytes = b"\x00"

    def __init__(
        self,
        call_type: CallType,
        frame_type: FrameType,
        packet_type: PacketType,
        slot_type: SlotType,
        timeslot: Timeslot,
        sequence_number: int,
        color_code: int,
        destination_radio_id: int,
        source_radio_id: int,
        payload: Union[bytes, "Burst"],
    ):
        """"""
        from okdmr.dmrlib.etsi.layer2.burst import Burst

        self.call_type = call_type
        self.frame_type = frame_type
        self.packet_type = packet_type
        self.slot_type = slot_type
        self.timeslot: Timeslot = timeslot
        self.sequence_number = sequence_number
        self.color_code = color_code
        self.payload: Union[bytes, "Burst"] = payload
        self.destination_radio_id = destination_radio_id
        self.source_radio_id = source_radio_id
        # following are IPSC segments whose purpose/contents are unknown, filled with pre-defined values
        # exposed to be possibly changed by implementing party
        self.first_header: bytes = HyteraIPSC.DEFAULT_FIRST_HEADER
        self.second_header: bytes = HyteraIPSC.DEFAULT_SECOND_HEADER
        self.reserved_3: bytes = HyteraIPSC.DEFAULT_RESERVED_3
        self.reserved_7a: bytes = HyteraIPSC.DEFAULT_RESERVED_7A
        self.reserved_2a: bytes = HyteraIPSC.DEFAULT_RESERVED_2A
        self.reserved_2b: bytes = HyteraIPSC.DEFAULT_RESERVED_2B
        self.reserved_1: bytes = HyteraIPSC.DEFAULT_RESERVED_1

    def __repr__(self) -> str:
        return (
            f"[{self.call_type}] "
            f"[{self.timeslot}] "
            f"[COLOR_CODE: {self.color_code}] "
            f"[SEQ: {self.sequence_number}] "
            f"[{self.packet_type}] "
            f"[{self.slot_type}] "
            f"[{self.frame_type}] "
            f"[{self.payload.hex() if isinstance(self.payload, bytes) else self.payload}] "
        )

    def is_wakeup(self) -> bool:
        return self.slot_type == SlotType.Wakeup or self.call_type in [
            CallType.WakeupCall_2,
            CallType.WakeupCall_c,
        ]

    @staticmethod
    def from_ipsc_bytes(ipsc: bytes) -> "HyteraIPSC":
        first_header = ipsc[0:2]
        second_header = ipsc[2:4]
        sequence_number = int.from_bytes(ipsc[4:5])
        reserved_3 = ipsc[5:8]
        packet_type = PacketType(int.from_bytes(ipsc[8:9]))
        reserved_7a = ipsc[9:16]
        timeslot = Timeslot(int.from_bytes(ipsc[16:18], "little"))
        slot_type = SlotType(int.from_bytes(ipsc[18:20], "little"))
        color_code = int.from_bytes(ipsc[20:22], "little")
        frame_type = FrameType(int.from_bytes(ipsc[22:24], "little"))
        reserved_2a = ipsc[24:26]
        payload = byteswap_bytes(ipsc[26:60])[:-1]
        reserved_2b = ipsc[60:62]
        call_type = CallType(int.from_bytes(ipsc[62:63], "little"))
        destination_radio_id = int.from_bytes(ipsc[63:67], "little")
        source_radio_id = int.from_bytes(ipsc[67:71], "little")
        reserved_1 = ipsc[71:72]
        ipsc = HyteraIPSC(
            sequence_number=sequence_number,
            call_type=call_type,
            frame_type=frame_type,
            packet_type=packet_type,
            slot_type=slot_type,
            timeslot=timeslot,
            color_code=color_code,
            destination_radio_id=destination_radio_id,
            source_radio_id=source_radio_id,
            payload=payload,
        )
        ipsc.first_header = first_header
        ipsc.second_header = second_header
        ipsc.reserved_3 = reserved_3
        ipsc.reserved_7a = reserved_7a
        ipsc.reserved_2a = reserved_2a
        ipsc.reserved_2b = reserved_2b
        ipsc.reserved_1 = reserved_1
        return ipsc

    @staticmethod
    def from_kaitai(ipsc: IpSiteConnectProtocol) -> "HyteraIPSC":
        def get_kaitai_val(attribute):
            return attribute if isinstance(attribute, int) else attribute.value

        # create instance by parsing distinct values
        _ipsc = HyteraIPSC(
            call_type=CallType(get_kaitai_val(ipsc.call_type)),
            frame_type=FrameType(get_kaitai_val(ipsc.frame_type)),
            packet_type=PacketType(get_kaitai_val(ipsc.packet_type)),
            slot_type=SlotType(get_kaitai_val(ipsc.slot_type)),
            timeslot=Timeslot(get_kaitai_val(ipsc.timeslot_raw)),
            sequence_number=ipsc.sequence_number,
            color_code=ipsc.color_code,
            destination_radio_id=ipsc.destination_radio_id,
            source_radio_id=ipsc.source_radio_id,
            payload=byteswap_bytes(ipsc.ipsc_payload)[:-1],
        )
        # assign values from original byte representation
        _ipsc.first_header = ipsc.source_port
        _ipsc.second_header = ipsc.fixed_header
        _ipsc.reserved_3 = ipsc.reserved_3
        _ipsc.reserved_7a = ipsc.reserved_7a
        _ipsc.reserved_2a = ipsc.reserved_2a
        _ipsc.reserved_2b = ipsc.reserved_2b
        _ipsc.reserved_1 = ipsc.reserved_1b

        return _ipsc

    def as_ipsc_bytes(self) -> bytes:
        return (
            self.first_header[0:2]
            + self.second_header[0:2]
            + self.sequence_number.to_bytes(1, byteorder="little")
            + self.reserved_3[0:3]
            + self.packet_type.value.to_bytes(1, byteorder="little")
            + self.reserved_7a[0:7]
            + self.timeslot.value.to_bytes(2, byteorder="little")
            + self.slot_type.value.to_bytes(2, byteorder="little")
            + half_byte_to_bytes(self.color_code)
            + self.frame_type.value.to_bytes(2, byteorder="little")
            + self.reserved_2a[0:2]
            + byteswap_bytes(
                self.payload
                if isinstance(self.payload, bytes)
                else (self.payload.as_bytes() + b"\x00")
            )
            + self.reserved_2b[0:2]
            + self.call_type.value.to_bytes(1, byteorder="little")
            + self.destination_radio_id.to_bytes(4, byteorder="little")
            + self.source_radio_id.to_bytes(4, byteorder="little")
            + self.reserved_1[0:1]
        )
