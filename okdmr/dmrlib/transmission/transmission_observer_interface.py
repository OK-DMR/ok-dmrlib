import traceback
from typing import List

from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.full_link_control import FullLinkControl
from okdmr.dmrlib.transmission.transmission_types import TransmissionTypes
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class TransmissionObserverInterface:
    def transmission_started(self, transmission_type: TransmissionTypes):
        """
        Get notified about new transmission (data or voice) being started with voice/data header

        @param transmission_type:
        @return:
        """
        pass

    def data_transmission_ended(
        self, transmission_header: DataHeader, blocks: List[BitsInterface]
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
        self, voice_header: FullLinkControl, blocks: List[BitsInterface]
    ):
        """
        Get notified about ended voice transmission
        @param voice_header:
        @param blocks:
        @return:
        """
        pass


class WithObservers(TransmissionObserverInterface):
    def __init__(self, observers: List[TransmissionObserverInterface] = ()):
        self.observers: List[TransmissionObserverInterface] = list(observers)

    def add_observer(self, observer: TransmissionObserverInterface) -> "WithObservers":
        """
        Add observer, if not already added
        """
        if observer not in self.observers:
            self.observers.append(observer)
        return self

    def remove_observer(
        self, observer: TransmissionObserverInterface
    ) -> "WithObservers":
        """
        Remove observer
        """
        self.observers.remove(observer)
        return self

    def voice_transmission_ended(
        self, voice_header: FullLinkControl, blocks: List[BitsInterface]
    ):
        for observer in self.observers:
            # noinspection PyBroadException
            try:
                observer.voice_transmission_ended(
                    voice_header=voice_header, blocks=blocks
                )
            except:
                traceback.print_exc()

    def data_transmission_ended(
        self, transmission_header: DataHeader, blocks: List[BitsInterface]
    ):
        for observer in self.observers:
            # noinspection PyBroadException
            try:
                observer.data_transmission_ended(
                    transmission_header=transmission_header, blocks=blocks
                )
            except:
                traceback.print_exc()

    def transmission_started(self, transmission_type: TransmissionTypes):
        for observer in self.observers:
            # noinspection PyBroadException
            try:
                observer.transmission_started(transmission_type=transmission_type)
            except:
                traceback.print_exc()
