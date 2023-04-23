import asyncio
import logging
import sys
import traceback
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from asyncio import DatagramProtocol, AbstractEventLoop
from dataclasses import dataclass
from socket import AddressFamily
from threading import Thread
from typing import Dict, Optional

from okdmr.dmrlib.protocols.hytera.rrs_datagram_protocol import RRSDatagramProtocol
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


@dataclass
class HRNPClientConfiguration:
    """
    No defaults should be set in this dataclass
    """

    # custom
    repeater_ip: str
    # cps
    rrs1: int
    rrs2: int
    gps1: int
    gps2: int
    tel1: int
    tel2: int
    tms1: int
    tms2: int
    rcc1: int
    rcc2: int
    rvs1: int
    rvs2: int
    e2e1: int
    e2e2: int
    sdmp1: int
    sdmp2: int


class HRNPClient(LoggingTrait):
    def __init__(self, config: HRNPClientConfiguration) -> None:
        self.log_info(f"HRNP Client staring, config: {repr(config)}")
        self.is_running: bool = False
        self.config: HRNPClientConfiguration = config
        self.services: Dict[int, DatagramProtocol] = {}
        """ dict port -> protocol handle """
        self.loop: Optional[AbstractEventLoop] = None

    def stop(self) -> None:
        self.is_running = False

    async def go(self) -> None:
        self.is_running = True

        rrs1proto = RRSDatagramProtocol(self.config.rrs1)
        rrs2proto = RRSDatagramProtocol(self.config.rrs2)
        # Radio Registration Service handler
        (
            self.services[self.config.rrs1],
            _,
        ) = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: rrs1proto,
            local_addr=("0.0.0.0", self.config.rrs1),
            remote_addr=(self.config.repeater_ip, self.config.rrs1),
            reuse_port=True,
            family=AddressFamily.AF_INET,
        )
        (
            self.services[self.config.rrs2],
            _,
        ) = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: rrs2proto,
            local_addr=("0.0.0.0", self.config.rrs2),
            remote_addr=(self.config.repeater_ip, self.config.rrs2),
            reuse_port=True,
            family=AddressFamily.AF_INET,
        )

        await asyncio.get_event_loop().create_task(rrs1proto.periodic_maintenance())
        await asyncio.get_event_loop().create_task(rrs2proto.periodic_maintenance())

    @staticmethod
    def args() -> ArgumentParser:
        args: ArgumentParser = ArgumentParser(
            description="HRNP Connect", formatter_class=ArgumentDefaultsHelpFormatter
        )

        args.add_argument("repeater_ip", type=str, help="Repeater IP address")
        # args.add_argument("--1", type=int, default=30_00, help=" TS1")
        # args.add_argument("--2", type=int, default=30_00, help=" TS2")
        args.add_argument(
            "--rrs1", type=int, default=30_001, help="Radio Registration Service TS1"
        )
        args.add_argument(
            "--rrs2", type=int, default=30_002, help="Radio Registration Service TS2"
        )
        args.add_argument(
            "--gps1", type=int, default=30_003, help="Radio GPS Service TS1"
        )
        args.add_argument(
            "--gps2", type=int, default=30_004, help="Radio GPS Service TS2"
        )
        args.add_argument(
            "--tel1", type=int, default=30_005, help="Radio Telemetry TS1"
        )
        args.add_argument(
            "--tel2", type=int, default=30_006, help="Radio Telemetry TS2"
        )
        args.add_argument(
            "--tms1", type=int, default=30_007, help="Text Messaging Service TS1"
        )
        args.add_argument(
            "--tms2", type=int, default=30_008, help="Text Messaging Service TS2"
        )
        args.add_argument(
            "--rcc1", type=int, default=30_009, help="Radio Call Control TS1"
        )
        args.add_argument(
            "--rcc2", type=int, default=30_010, help="Radio Call Control TS2"
        )
        args.add_argument(
            "--rvs1", type=int, default=30_012, help="Radio Voice Service TS1"
        )
        args.add_argument(
            "--rvs2", type=int, default=30_014, help="Radio Voice Service TS2"
        )
        args.add_argument(
            "--e2e1", type=int, default=30_017, help="E2E Encrypted Data TS1"
        )
        args.add_argument(
            "--e2e2", type=int, default=30_018, help="E2E Encrypted Data TS2"
        )
        args.add_argument(
            "--sdmp1",
            type=int,
            default=30_17,
            help="Self-Defined Message Protocol (SDMP) TS1",
        )
        args.add_argument(
            "--sdmp2",
            type=int,
            default=30_18,
            help="Self-Defined Message Protocol (SDMP) TS2",
        )
        return args

    @staticmethod
    def run() -> None:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] [%(levelname)s] [{ %(message)s }]",
            datefmt="%X",
        )
        mainlog = logging.getLogger("hrnp-connect-entry")
        app_thread = None
        app = None
        try:
            parsed = HRNPClient.args().parse_args(sys.argv[1:])
            config = HRNPClientConfiguration(**vars(parsed))
            app = HRNPClient(config=config)
            app_thread = Thread(target=lambda: asyncio.run(app.go(), debug=True))
            app_thread.start()
            mainlog.info("Thread started")
            app_thread.join()
        except Exception:
            traceback.print_last(file=sys.stderr)
        finally:
            app.stop()
