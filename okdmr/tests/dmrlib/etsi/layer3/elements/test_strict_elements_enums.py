from unittest import TestCase

from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer3.elements.additional_information_field import (
    AdditionalInformationField,
)
from okdmr.dmrlib.etsi.layer3.elements.answer_response import AnswerResponse
from okdmr.dmrlib.etsi.layer3.elements.channel_timing_opcode import ChannelTimingOpcode
from okdmr.dmrlib.etsi.layer3.elements.dynamic_identifier import DynamicIdentifier
from okdmr.dmrlib.etsi.layer3.elements.reason_code import ReasonCode
from okdmr.dmrlib.etsi.layer3.elements.source_type import SourceType


class RaisingEnums(TestCase):
    def test_AdditionalInformationField(self):
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
            CsbkOpcodes(0b001000)
