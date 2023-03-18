import sys
from argparse import ArgumentParser

from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HRNPClient(LoggingTrait):
    @staticmethod
    def args() -> ArgumentParser:
        args: ArgumentParser = ArgumentParser(
            description="HRNP Connect",
        )

        args.add_argument("repeater_ip", type=str, help="Repeater IP address")
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
        # args.add_argument("--1", type=int, default=30_00, help=" TS1")
        # args.add_argument("--2", type=int, default=30_00, help=" TS2")
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
        parsed = HRNPClient.args().parse_args(sys.argv[1:])
        print(parsed)
