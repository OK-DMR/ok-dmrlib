from typing import Dict, List

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.transmission.timeslot import Timeslot
from okdmr.dmrlib.transmission.transmission_observer_interface import (
    TransmissionObserverInterface,
    WithObservers,
)


class Terminal(WithObservers):
    """
    Simulated terminal as DMR traffic target, it can transmit/receive traffic on separate timeslots and will produce events,
    possibly with data, extracted from given traffic, to provided observer(s)
    """

    def __init__(self, dmrid: int, observers: List[TransmissionObserverInterface] = ()):
        """

        :param dmrid:
        """
        assert (
            0 < dmrid <= 0xFFFFFF
        ), f"Address does not comfort to Air Interface (AI) Numbering and dialling plan, got {dmrid}"
        super().__init__(observers=observers)
        self.id: int = dmrid
        self.timeslots: Dict[int, Timeslot] = {
            1: Timeslot(timeslot=1, observers=[self]),
            2: Timeslot(timeslot=2, observers=[self]),
        }

    def process_incoming_burst(self, burst: Burst, timeslot: int) -> Burst:
        """
        Pass burst onto specific timeslot

        :param burst:
        :param timeslot:
        :return:
        """
        return self.timeslots[timeslot].process_burst(burst)

    def debug(self, printout: bool = True) -> str:
        status: str = f"[ID: {self.id}]\n"
        for ts in self.timeslots.values():
            status += "\t" + ts.debug(False) + "\n"

        if printout:
            print(status)
        return status
