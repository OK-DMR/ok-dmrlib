import logging
from typing import List

import pytest
from bitarray import bitarray
from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol
from scapy.layers.inet import IP, UDP
from scapy.packet import Raw

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.elements.fragment_sequence_number import (
    FragmentSequenceNumber,
)
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data, Rate12DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.etsi.layer3.pdu.udp_ipv4_compressed_header import (
    UDPIPv4CompressedHeader,
)
from okdmr.dmrlib.motorola.text_messaging_service import TextMessagingService
from okdmr.dmrlib.transmission.transmission_generator import TransmissionGenerator
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
    WithObservers,
)
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.transmission.transmission_watcher import TransmissionWatcher
from okdmr.dmrlib.utils.bits_bytes import bits_to_bytes, bytes_to_bits
from okdmr.dmrlib.utils.bits_interface import BitsInterface
from scapy.config import conf

conf.use_pcap = True

SMS_BURST: List[str] = [
    "55e105fbbde427040a68305294fdff57d75df5dcae42369824097da3bedb329255",
    "5585057bbcfc273c0e0938f094fdff57d75df5dcae8a163824c97d63b65b281251",
    "55c505f9bde025240c38b4b094fdff57d75df5dcaefa360864297ec3b39b211267",
    "45a10577bcf026340c69bcf294fdff57d75df5dcae2e579865b978c1b39f299a42",
    "45e105f5bdec242c0e5830b294fdff57d75df5dcae5e77a825597b61b65f209a74",
    "45850575bcf424140a39381094fdff57d75df5dcae96570825997ba1bedf3a1a70",
    "45c505f7bde8260c0808b45094fdff57d75df5dcaee6773865797801bb1f331a46",
    "45c4053dbcfc263c0839b0d294fdff57d75df5dcaeb216a8e5d97881b75b331a65",
    "458405bfbde024240a083c9294fdff57d75df5dcaec23698a5397b21b29b3a1a53",
    "45e0053fbcf8241c0e69343094fdff57d75df5dcae0a1638a5f97be1ba1b209a57",
    "45a005bdbde426040c58b87094fdff57d75df5dcae7a3608e5197841bfdb299a61",
    "45a7053fbd6c26240e19b4d294fdff57d75df5dcaeb25690e7987aa1bb1f381257",
    "45e705bdbc70243c0c28389294fdff57d75df5dcaec276a0a7787901bedf311261",
    "4583053dbd6824040849303094fdff57d75df5dcae0a5600a7b879c1b65f2b9265",
    "45c305bfbc74261c0a78bc7094fdff57d75df5dcae7a7630e7587a61b39f229253",
    "45c20575bd60262c0a49b8f294fdff57d75df5dcae2e17a067f87ae1bfdb229270",
    # header
    "7abc3520240678e3a3436a8b55bdff57d75df5d55ed179b2304122624d0589a7bc",
    # rate 1/2 unconfirmed data
    "430d22106233407c00b0219a55ddff57d75df5d6f1492a46d43d20c20b8291214b",
    # rate 1/2 unconfirmed data last fragment
    "008a00da01b401400330180015ddff57d75df5d6f104025802700ae0250010001e",
]


def test_single_csbk_preamble():
    orig: bytes = bytes.fromhex(SMS_BURST[0])

    csbk: CSBK = CSBK(
        target_address_is_individual=True,
        source_address=2308094,
        target_address=2308092,
        csbko=CsbkOpcodes.PreambleCSBK,
        blocks_to_follow=18,
    )
    burst: Burst = Burst(burst_type=BurstTypes.DataAndControl)
    burst.data = csbk
    burst.sync_or_embedded_signalling = SyncPatterns.BsSourcedData
    burst.has_slot_type = True
    burst.has_emb = False
    burst.slot_type = SlotType(colour_code=5, data_type=DataTypes.CSBK)

    assert burst.as_bits().tobytes() == orig


def test_all_preambles():
    generated_preambles: List[Burst] = TransmissionGenerator.generate_csbk_preambles(
        source_address=2308094,
        target_address=2308092,
        num_of_preambles=16,
        colour_code=5,
        num_of_following_data_blocks=3,
    )

    for i in range(0, 16):
        gen_hex: str = generated_preambles[i].as_bits().tobytes().hex()
        expected_hex: str = SMS_BURST[i]
        assert gen_hex == expected_hex, f"burst {i} is different"


def test_header(do_return: bool = False):
    header: DataHeader = DataHeader(
        dpf=DataPacketFormats.DataPacketUnconfirmed,
        sap_identifier=SAPIdentifier.UDP_IP_compression,
        is_response_requested=False,
        pad_octet_count=10,
        llid_destination=2308092,
        llid_source=2308094,
        blocks_to_follow=2,
        fragment_sequence_number=FragmentSequenceNumber.SINGLE_UNCONFIRMED_FRAGMENT_VALUE,
        full_message_flag=FullMessageFlag.FirstTryToCompletePacket,
    )
    burst: Burst = TransmissionGenerator.generate_data_header_burst(header)
    assert SMS_BURST[16] == burst.as_bits().tobytes().hex()
    return header if do_return else None


def test_construct_rate12():
    from okdmr.tests.dmrlib.etsi.layer3.pdu.test_udp_ipv4_compressed_header import (
        test_reconstruct,
    )

    payload: UDPIPv4CompressedHeader = test_reconstruct(do_return=True)
    header: DataHeader = test_header(do_return=True)

    full_transmission: List[
        Burst
    ] = TransmissionGenerator.generate_full_data_transmission(
        data_header=header,
        userdata=payload,
        packet_type=Rate12Data,
        csbk_count=16,
        colour_code=5,
    )

    assert len(full_transmission) == len(
        SMS_BURST
    ), f"expected {len(SMS_BURST)} bursts, got {len(full_transmission)}"
    for i in range(0, len(SMS_BURST)):
        assert (
            full_transmission[i].as_bytes().hex().lower() == SMS_BURST[i].lower()
        ), f"burst {i} mismatch"


def test_sms():
    rawdata: bytes = b""
    cut_padding_bytes: int = 0
    touch_num_blocks: int = 0
    expect_num_blocks: int = 0

    for i in range(0, len(SMS_BURST)):
        b = Burst.from_bytes(
            data=bytes.fromhex(SMS_BURST[i]), burst_type=BurstTypes.DataAndControl
        )
        if isinstance(b.data, DataHeader):
            cut_padding_bytes = b.data.pad_octet_count
            expect_num_blocks = b.data.blocks_to_follow
        elif isinstance(b.data, Rate12Data):
            touch_num_blocks += 1
            rawdata += (
                b.data.data
                if touch_num_blocks == 1
                else b.data.convert(Rate12DataTypes.UnconfirmedLastBlock).data
            )
            if touch_num_blocks == expect_num_blocks:
                b.data = b.data.convert(Rate12DataTypes.UnconfirmedLastBlock)
            print(bytes.fromhex(SMS_BURST[i]).hex())
            print(repr(b.data))

    assert expect_num_blocks == touch_num_blocks

    uip_bytes: bytes = rawdata[: len(rawdata) - cut_padding_bytes]
    uip = UDPIPv4CompressedHeader.from_bytes(uip_bytes)
    uip_data_bytes: bytes = bits_to_bytes(uip.user_data)
    tms: TextMessagingService = TextMessagingService.from_bytes(uip_data_bytes)
    assert tms.as_bytes() == uip_data_bytes


def test_process_burst(caplog):
    caplog.clear()
    caplog.set_level(logging.DEBUG)

    tw: TransmissionWatcher = TransmissionWatcher()
    assert tw.process_burst(Burst()) is None

    # check no error logs produced while procesing
    for record in caplog.records:
        assert record.levelno != logging.ERROR


def test_voice_bytes(caplog):
    caplog.clear()
    caplog.set_level(logging.DEBUG)
    ipsc_in: bytes = bytes.fromhex(
        "5a5a5a5a2003000041000501020000002222777755550000807325ef402209df1b7f9caf6575e774fd55f77d795f9f41364a68ca604641ec96a400b3402201006f000000fa372300"
    )
    ip_pkt: IP = IP() / UDP() / Raw(ipsc_in)
    tw: TransmissionWatcher = TransmissionWatcher()
    tw.set_debug_voice_bytes(do_debug=True)
    tw.process_packet(data=ipsc_in, packet=ip_pkt)

    search_in = " ".join(caplog.messages)

    assert "[FROM 2308090]" in search_in
    assert "[TO 111]" in search_in
    # first 9 bytes of vocoder data
    assert "[239, 37, 34, 64, 223, 9, 127, 27, 175]" in search_in
    # second 9 bytes
    assert "[156, 117, 101, 116, 233, 65, 159, 74, 54]" in search_in
    # last 9 bytes of vocoder data
    assert "[202, 104, 70, 96, 236, 65, 164, 150, 179]" in search_in

    # test error log on too high loglevel
    # caplog.clear()
    caplog.set_level(logging.INFO)
    tw.set_debug_voice_bytes(do_debug=True)
    tw.process_packet(data=ipsc_in, packet=ip_pkt)

    print(caplog.messages)


def test_voice_transmission(capsys):
    voice_pkts: List[str] = [
        # voice lc header
        "5a5a5a5a610400004100050102000000222211115555000040b970078009fc078821205220655d5457ff5dd7d8f57854d004d03e003e012a036500f3800901006f000000fc372300",
        # burst A
        "5a5a5a5a6204000041000501020000002222777755550000401a4abacd1c74706c3af98a7a2957affd55f77d735f8e1e002cd30912a74156e68600c0cd1c01006f000000fc372300",
        # burst B
        "5a5a5a5a63040000410005010200000022228888555500004031369242a379718a59ca2ad74055daa020f030f3f889fe8a6c99d641c55111ae3b000a42a301006f000000fc372300",
        # burst C
        "5a5a5a5a64040000410005010200000022229999555500004003ce9167a6a153e49cf648c7997505a06060a0a0667e356eca60c823c0d0234000008267a601006f000000fc372300",
        # burst D
        "5a5a5a5a6504000041000501020000002222aaaa555500004007858e30e61d73a2dfce6481d4557591607042a5c60e53cea2968c11c71833e4df004430e601006f000000fc372300",
        # burst E
        "5a5a5a5a6604000041000501020000002222bbbb55550000401568bb16c47955c40abc8ce05e15362341b35290312a9400c829076d9b5157e290008416c401006f000000fc372300",
        # burst F
        "5a5a5a5a6704000041000501020000002222cccc55550000401325b026a21c13ca5ee10cc5467522c10964d1c13fde50a2ae37b024a23c33ee59000826a201006f000000fc372300",
        # terminator with LC
        "5a5a5a5ab00400004300050102000000222222225555000040b91f0754094c07f021505280659d5457ff5dd7dff56c01e807b03940320122037c00c0540901006f000000fc372300",
    ]
    tw: TransmissionWatcher = TransmissionWatcher()
    for voice_pkt in voice_pkts:
        tw.process_burst(
            Burst.from_hytera_ipsc(
                IpSiteConnectProtocol.from_bytes(bytes.fromhex(voice_pkt))
            )
        )

    for terminal_id, terminal in tw.terminals.items():
        for ts_num, ts in terminal.timeslots.items():
            ts.transmission.end_voice_transmission()


class TestWatcher(TransmissionObserverInterface):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.transmission_ended: bool = False
        self.started: int = 0
        self.ended: int = 0

    def transmission_started(self, transmission_type: TransmissionTypes):
        self.started += 1
        assert transmission_type == (
            TransmissionTypes.DataTransmission
            if not self.transmission_ended
            else TransmissionTypes.Idle
        )

    def data_transmission_ended(
        self, transmission_header: DataHeader, blocks: List[BitsInterface]
    ):
        self.ended += 1
        assert len(blocks) == 19
        assert (
            transmission_header.data_packet_format
            == DataPacketFormats.DataPacketUnconfirmed
        )
        self.transmission_ended = True

    def test_watcher(self, capsys):
        watcher: TransmissionWatcher = TransmissionWatcher()
        # check observer added
        watcher.add_observer(observer=self)
        assert len(watcher.observers) == 1
        # check duplicate not added
        watcher.add_observer(observer=self)
        assert len(watcher.observers) == 1
        watcher.set_debug_voice_bytes(do_debug=True)

        for orig_burst in SMS_BURST:
            b = Burst.from_bytes(
                data=bytes.fromhex(orig_burst), burst_type=BurstTypes.DataAndControl
            )
            # emulate on-air
            b.target_radio_id = 111
            b.timeslot = 1
            # process in watcher
            watcher.process_burst(burst=b)

        # check observers are cleared correctly
        watcher.remove_observer(observer=self)
        assert len(watcher.observers) == 0

        assert self.started == 1
        assert self.ended == 1

        for terminal_id, terminal in watcher.terminals.items():
            # returns
            assert len(terminal.debug(printout=False))
            # prints
            capsys.readouterr()
            terminal.debug(printout=True)
            assert len(capsys.readouterr().out)

            for ts_no, ts in terminal.timeslots.items():
                assert len(ts.debug(printout=False))
                capsys.readouterr()
                ts.debug(printout=True)
                assert len(capsys.readouterr().out)

        watcher.end_all_transmissions()


class TestTransmissionObserverInterface(TransmissionObserverInterface):
    def voice_transmission_ended(
        self, voice_header: FullLinkControl, blocks: List[BitsInterface]
    ):
        """
        Just for test_raising_observer
        """
        raise ModuleNotFoundError()

    def data_transmission_ended(
        self, transmission_header: DataHeader, blocks: List[BitsInterface]
    ):
        """
        Just for test_raising_observer
        """
        raise ModuleNotFoundError()

    def transmission_started(self, transmission_type: TransmissionTypes):
        """
        Just for test_raising_observer
        """
        raise ModuleNotFoundError()

    def test_add_observer(self) -> None:
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            WithObservers(observers=[]).add_observer(observer=None)

    def test_raising_observer(self, caplog) -> None:
        WithObservers(observers=[self]).voice_transmission_ended(
            blocks=[],
            voice_header=FullLinkControl(
                protect_flag=0,
                flco=FLCOs.UnitToUnitVoiceChannelUser,
                fid=FeatureSetIDs.StandardizedFID,
                crc=bitarray(),
            ),
        )
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].exc_info[0] == ModuleNotFoundError
        caplog.clear()

        WithObservers(observers=[self]).data_transmission_ended(
            transmission_header=DataHeader(
                dpf=DataPacketFormats.DataPacketUnconfirmed,
                sap_identifier=SAPIdentifier.UDP_IP_compression,
                full_message_flag=FullMessageFlag.FirstTryToCompletePacket,
            ),
            blocks=[],
        )
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].exc_info[0] == ModuleNotFoundError
        caplog.clear()

        WithObservers(observers=[self]).transmission_started(
            transmission_type=TransmissionTypes.Idle
        )
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].exc_info[0] == ModuleNotFoundError
        caplog.clear()
