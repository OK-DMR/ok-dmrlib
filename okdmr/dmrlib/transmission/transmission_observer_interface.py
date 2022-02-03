from typing import List

from kaitaistruct import KaitaiStruct
from okdmr.kaitai.etsi.dmr_data_header import DmrDataHeader
from okdmr.kaitai.etsi.full_link_control import FullLinkControl

from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes


class TransmissionObserverInterface:
    def transmission_started(self, transmission_type: TransmissionTypes):
        """
        Get notified about new transmission (data or voice) being started with voice/data header

        @param transmission_type:
        @return:
        """
        pass

    def data_transmission_ended(
        self, transmission_header: DmrDataHeader, blocks: List[KaitaiStruct]
    ):
        """
        Get notified about completed (or ended) data transmission and get all blocks that made up that transmission,
        including CSBKs and all the raw DMR packets

        @param transmission_header:
        @param blocks:
        @return:
        """
        pass

    def voice_transmission_ended(
        self, voice_header: FullLinkControl, blocks: List[KaitaiStruct]
    ):
        """
        Get notified about ended voice transmission
        @param voice_header:
        @param blocks:
        @return:
        """
        pass
