import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Type, Optional, List

from okdmr.dmrlib.utils.bytes_interface import BytesInterface


class ProtocolTool:
    @staticmethod
    def _args(protocol: str) -> ArgumentParser:
        parser = ArgumentParser(
            description="Debug packet(s)", formatter_class=ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            "hex", type=str, nargs="+", help=f"Hex encoded messages of {protocol}"
        )
        return parser

    @staticmethod
    def _impl(
        protocol: str, impl: Type[BytesInterface], arguments: Optional[List[str]] = None
    ) -> None:
        args = ProtocolTool._args(protocol=protocol).parse_args(
            sys.argv[1:] if (not arguments or not len(arguments)) else arguments
        )
        for hex_msg in args.hex:
            print(hex_msg)
            try:
                pdu = impl.from_bytes(bytes.fromhex(hex_msg))
                print(repr(pdu))
            except Exception as e:
                print(e, file=sys.stderr)
