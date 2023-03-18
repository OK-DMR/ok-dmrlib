import logging
import os
from asyncio import (
    get_running_loop,
    AbstractEventLoop,
    new_event_loop,
)
from signal import SIGINT, SIGTERM
from typing import Union, Tuple, Any, Optional, Dict, Type

from okdmr.dmrlib.hytera.pdu.hstrp import HSTRP, HSTRPPacketType
from okdmr.dmrlib.hytera.pdu.radio_registration_service import (
    RRSRadioState,
    RadioRegistrationService,
    RRSTypes,
    RRSResult,
)
from okdmr.dmrlib.protocols.hytera.hrnp_datagram_protocol import HSTRPDatagramProtocol
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class RCPLayer(HSTRPDatagramProtocol):
    def __init__(self, port: int) -> None:
        super().__init__(port=port)
        self.radios: Dict[int, HSTRP] = {}

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        was_handled, pdu = super().datagram_received(data=data, addr=addr)
        if not pdu:
            return was_handled, pdu

        if not was_handled:
            self.log_warning(f"\nRCP did not handle {data.hex()}")
            self.log_warning(repr(pdu))

        return was_handled, pdu


class LPLayer(HSTRPDatagramProtocol):
    def __init__(self, port: int) -> None:
        super().__init__(port=port)

    def datagram_received(
        self, data: bytes, addr: Tuple[Union[str, Any], int]
    ) -> Tuple[bool, Optional[HSTRP]]:
        was_handled, pdu = super().datagram_received(data=data, addr=addr)
        if not pdu:
            return was_handled, pdu

        if not was_handled:
            self.log_warning(f"\nLP did not handle {data.hex()}")
            self.log_warning(repr(pdu))

        return was_handled, pdu


class RRSLayer(HSTRPDatagramProtocol):
    def __init__(self, port: int):
        super().__init__(port=port)
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


class RRSApp(LoggingTrait):
    DEF_PORT_SLOT1: int = 30_001
    DEF_PORT_SLOT2: int = 30_002
    EXTRA_PORTS: Dict[int, Type[HSTRPDatagramProtocol]] = {
        # mobile
        3_002: RRSLayer,
        3_003: LPLayer,
        5_016: HSTRPDatagramProtocol,
        3_005: RCPLayer,
        3_006: HSTRPDatagramProtocol,
        3_007: HSTRPDatagramProtocol,
        3_009: HSTRPDatagramProtocol,
        # GPS
        30_003: LPLayer,
        30_004: LPLayer,
        # telemetry
        30_005: HSTRPDatagramProtocol,
        30_006: HSTRPDatagramProtocol,
        # tms
        30_007: HSTRPDatagramProtocol,
        30_008: HSTRPDatagramProtocol,
        # radio control
        30_009: RCPLayer,
        30_010: RCPLayer,
        # voice service
        30_012: None,
        30_014: None,
        # analog call control
        30_015: HSTRPDatagramProtocol,
        30_016: HSTRPDatagramProtocol,
        # e2e
        30_017: HSTRPDatagramProtocol,
        30_018: HSTRPDatagramProtocol,
        # sdmp
        3_017: HSTRPDatagramProtocol,
        3_018: HSTRPDatagramProtocol,
    }

    def __init__(
        self,
        ip: str = "192.168.22.13",
        slot1_port: int = DEF_PORT_SLOT1,
        slot2_port: int = DEF_PORT_SLOT2,
    ):
        self.loop: Optional[AbstractEventLoop] = None
        self.ip: str = ip
        self.port_slot1: int = slot1_port
        self.port_slot2: int = slot2_port
        self.slot1: RRSLayer = RRSLayer(port=self.port_slot1)
        self.slot2: RRSLayer = RRSLayer(port=self.port_slot2)
        self.extras: Dict[int, HSTRPDatagramProtocol] = {}

    async def go(self) -> None:
        self.log_info("RRSApp.go")
        self.loop = get_running_loop()

        await self.loop.create_datagram_endpoint(
            lambda: self.slot1, local_addr=(self.ip, self.port_slot1)
        )
        await self.loop.create_datagram_endpoint(
            lambda: self.slot2, local_addr=(self.ip, self.port_slot2)
        )
        for extra_port, handler in self.EXTRA_PORTS.items():
            if not handler:
                continue
            self.extras[extra_port] = handler(port=extra_port)
            await self.loop.create_datagram_endpoint(
                lambda: self.extras[extra_port], local_addr=(self.ip, extra_port)
            )
            self.log_info(
                f"Opened UDP port {extra_port} with handler {handler.__name__}"
            )

    def stop(self) -> None:
        self.log_info("stop at signal handler")
        self.loop.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app: RRSApp = RRSApp()
    loop = new_event_loop()

    if os.name != "nt":
        for signal in [SIGINT, SIGTERM]:
            loop.add_signal_handler(signal, app.stop)

    loop.run_until_complete(future=app.go())
    loop.run_forever()
