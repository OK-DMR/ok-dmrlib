from typing import List
from unittest import TestCase

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.fragment_sequence_number import (
    FragmentSequenceNumber,
)
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.sap_identifier import SAPIdentifier
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.transmission.transmission_generator import TransmissionGenerator
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
)
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.transmission.transmission_watcher import TransmissionWatcher
from okdmr.dmrlib.utils.bits_interface import BitsInterface

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


def test_header():
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
    burst: Burst = Burst(burst_type=BurstTypes.DataAndControl)
    burst.data = header
    burst.sync_or_embedded_signalling = SyncPatterns.BsSourcedData
    burst.slot_type = SlotType(colour_code=5, data_type=DataTypes.DataHeader)
    burst.has_emb = False
    assert SMS_BURST[16] == burst.as_bits().tobytes().hex()


def test_sms():
    for i in range(0, len(SMS_BURST)):
        b = Burst.from_bytes(
            data=bytes.fromhex(SMS_BURST[i]), burst_type=BurstTypes.DataAndControl
        )
        print(repr(b))


class TestWatcher(TestCase, TransmissionObserverInterface):
    # pep8 ignored since the name is defined in unittest
    # noinspection PyPep8Naming
    def __init__(self, methodName: str):
        super().__init__(methodName=methodName)
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

    def test_watcher(self):
        watcher: TransmissionWatcher = TransmissionWatcher()
        # check observer added
        watcher.add_observer(observer=self)
        assert len(watcher.observers) == 1
        # check duplicate not added
        watcher.add_observer(observer=self)
        assert len(watcher.observers) == 1
        watcher.set_debug_voice_bytes(do_debug=True)

        for i in range(0, len(SMS_BURST)):
            o: str = SMS_BURST[i]
            b = Burst.from_bytes(
                data=bytes.fromhex(o), burst_type=BurstTypes.DataAndControl
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
