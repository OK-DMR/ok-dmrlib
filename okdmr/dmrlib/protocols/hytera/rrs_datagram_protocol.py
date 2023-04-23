from typing import Tuple, Union, Any, Optional, Dict

from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType
from okdmr.dmrlib.hytera.pdu.radio_registration_service import (
    RRSRadioState,
    RadioRegistrationService,
    RRSTypes,
    RRSResult,
)
from okdmr.dmrlib.protocols.hytera.hstrp_datagram_protocol import HSTRPDatagramProtocol


class RRSDatagramProtocol(HSTRPDatagramProtocol):
    def __init__(self, port: int, be_active_peer: bool = False):
        super().__init__(port=port, be_active_peer=be_active_peer)
        self.registry: Dict[str, RRSRadioState] = {}

    def rrs_confirm(self, pdu: HSTRP, addr: Tuple[Union[str, Any], int]):
        assert isinstance(pdu.payload, RadioRegistrationService)
        rrs = RadioRegistrationService(
            opcode=RRSTypes.RadioRegistrationAnswer,
            radio_ip=pdu.payload.radio_ip,
            result=RRSResult.Success,
            renew_time_seconds=60 * 5,
        )
        hstrp = HSTRP(
            pkt_type=HSTRPPacketType(
                have_options=True,
            ),
            payload=rrs,
            sn=self.hstrp_increment_sn(),
        )
        self.transport.sendto(data=hstrp.as_bytes(), addr=addr)

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        was_handled, pdu = super().datagram_received(data=data, addr=addr)
        if not pdu:
            return was_handled, pdu

        rrs: RadioRegistrationService = (
            pdu.payload if isinstance(pdu.payload, RadioRegistrationService) else None
        )
        if not rrs:
            return was_handled, pdu

        if rrs.opcode == RRSTypes.RadioRegistrationRequest:
            was_handled = True
            self.registry[rrs.radio_ip.as_ip()] = RRSRadioState.Online
            self.rrs_confirm(pdu, addr)
            self.log_info(f"Radio {rrs.radio_ip.radio_id} is {rrs.radio_state.name}")
        elif rrs.opcode == RRSTypes.RadioGoingOffline:
            was_handled = True
            self.registry[rrs.radio_ip.as_ip()] = RRSRadioState.Offline
            self.log_info(f"Radio {rrs.radio_ip.radio_id} went Offline")

        if not was_handled:
            self.log_warning(f"\nRRS did not handle {data.hex()}")
            self.log_warning(repr(pdu))

        return was_handled, pdu
