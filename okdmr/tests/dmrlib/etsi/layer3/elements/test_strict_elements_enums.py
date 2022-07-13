from unittest import TestCase

from bitarray import bitarray

from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_packet_formats import DataPacketFormats
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer2.elements.fragment_sequence_number import (
    FragmentSequenceNumber,
)
from okdmr.dmrlib.etsi.layer2.elements.full_message_flag import FullMessageFlag
from okdmr.dmrlib.etsi.layer2.elements.resynchronize_flag import ResynchronizeFlag
from okdmr.dmrlib.etsi.layer2.elements.sarq import SARQ
from okdmr.dmrlib.etsi.layer2.elements.slcos import SLCOs
from okdmr.dmrlib.etsi.layer2.elements.supplementary_flag import SupplementaryFlag
from okdmr.dmrlib.etsi.layer2.elements.voice_bursts import VoiceBursts
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate1_data import Rate1DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34DataTypes
from okdmr.dmrlib.etsi.layer3.elements.activity_id import ActivityID
from okdmr.dmrlib.etsi.layer3.elements.additional_information_field import (
    AdditionalInformationField,
)
from okdmr.dmrlib.etsi.layer3.elements.answer_response import AnswerResponse
from okdmr.dmrlib.etsi.layer3.elements.channel_timing_opcode import ChannelTimingOpcode
from okdmr.dmrlib.etsi.layer3.elements.dynamic_identifier import DynamicIdentifier
from okdmr.dmrlib.etsi.layer3.elements.position_error import PositionError
from okdmr.dmrlib.etsi.layer3.elements.reason_code import ReasonCode
from okdmr.dmrlib.etsi.layer3.elements.source_type import SourceType
from okdmr.dmrlib.etsi.layer3.elements.talker_alias_data_format import (
    TalkerAliasDataFormat,
)
from okdmr.dmrlib.etsi.layer3.elements.udt_option_flag import UDTOptionFlag


class RaisingElements(TestCase):
    def test_raising_elements(self):
        with self.assertRaises(ValueError):
            AdditionalInformationField(0b10)
        with self.assertRaises(ValueError):
            AnswerResponse(0b00000000)
        with self.assertRaises(ValueError):
            ChannelTimingOpcode(0b111)
        with self.assertRaises(ValueError):
            DynamicIdentifier(0b110)
        with self.assertRaises(ValueError):
            ReasonCode(0b01010101)
        with self.assertRaises(ValueError):
            SourceType(0b10)
        with self.assertRaises(ValueError):
            CsbkOpcodes(0b001001)
        with self.assertRaises(ValueError):
            TalkerAliasDataFormat(0b100)
        with self.assertRaises(ValueError):
            PositionError(0b1000)
        with self.assertRaises(ValueError):
            ActivityID(0b10000)
        with self.assertRaises(ValueError):
            FLCOs(0b001001)
        with self.assertRaises(ValueError):
            FullMessageFlag(0b10)
        with self.assertRaises(ValueError):
            ResynchronizeFlag(0b10)
        with self.assertRaises(ValueError):
            SARQ(0b10)
        with self.assertRaises(AssertionError):
            SLCOs(0b10000)
        with self.assertRaises(ValueError):
            SupplementaryFlag(0b10)
        with self.assertRaises(ValueError):
            UDTOptionFlag(0b10)
        with self.assertRaises(AssertionError):
            ChannelTimingOpcode.from_bits(bitarray("1"))
        with self.assertRaises(ValueError):
            Rate12DataTypes(-1)
        with self.assertRaises(ValueError):
            Rate34DataTypes(-1)
        with self.assertRaises(ValueError):
            Rate1DataTypes(-1)
        with self.assertRaises(ValueError):
            # unknown CSBKO test
            CSBK.from_bits(
                bitarray(
                    "100010010001000000000000000010001111110100100011001101111111110111110000001000001110011010001011"
                )
            )
        with self.assertRaises(AssertionError):
            FragmentSequenceNumber(0b10101)
        with self.assertRaises(AssertionError):
            VoiceBursts(5)
        with self.assertRaises(NotImplementedError):
            DataHeader(dpf=DataPacketFormats.ProprietaryDataPacket).as_bits()
        with self.assertRaises(NotImplementedError):
            DataHeader.from_bits(
                bits=bitarray([0] * 4)
                + DataPacketFormats.ProprietaryDataPacket.as_bits()
            )
