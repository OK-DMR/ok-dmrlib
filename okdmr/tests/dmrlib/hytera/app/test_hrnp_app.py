import asyncio
import sys
from threading import Thread
from time import sleep
from typing import List, Dict, Union

from okdmr.dmrlib.hytera.pdu.hrnp import HRNP, HRNPOpcodes
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RadioControlProtocol,
    RCPOpcode,
)
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HRNPApp(LoggingTrait):
    def __init__(self):
        from serial import Serial

        self.serial: Serial = Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=2)
        self.counter: int = 0
        self.buffer_in: bytes = b""
        self.source_id: int = 0x20
        self.buffer_out: List[bytes] = []
        self.is_running: bool = False

    def write(self, hrnp: HRNP) -> None:
        sleep(0.1)
        # modify
        hrnp.source = self.source_id
        if hrnp.opcode != HRNPOpcodes.DATA_ACK:
            hrnp.packet_number = self.counter
            self.counter += 1
        # log
        print(f"SEND: {hrnp.as_bytes().hex().upper()}")
        print(repr(hrnp))
        # assert
        assert (
            HRNP.from_bytes(hrnp.as_bytes()).as_bytes() == hrnp.as_bytes()
        ), f"not stable {repr(hrnp)} {hrnp.as_bytes().hex().upper()} vs {HRNP.from_bytes(hrnp.as_bytes()).as_bytes().hex().upper()}"
        # write out
        self.serial.write(hrnp.as_bytes())

    def close(self) -> None:
        self.write(HRNP(opcode=HRNPOpcodes.CLOSE))

    def connect(self) -> None:
        self.counter = 0
        self.write(HRNP(opcode=HRNPOpcodes.CONNECT))

    def parse_buffer_in(self, data: bytes) -> None:
        try:
            # clear buffer until we find expected HRNP header byte
            while self.buffer_in[0] != 0x7E:
                self.buffer_in = self.buffer_in[1:]
            # try parse HRNP from buffer_in
            hrnp = HRNP.from_bytes(self.buffer_in)
            print(f"RECV: {self.buffer_in.hex().upper()}")
            if not hrnp.as_bytes() == self.buffer_in:
                print(
                    f"RECV checksum {self.buffer_in[10:12].hex().upper()} not match {hrnp.checksum.hex().upper()}"
                )
            print(repr(hrnp))
            if hrnp.opcode == HRNPOpcodes.DATA and isinstance(
                hrnp.data, RadioControlProtocol
            ):
                if hrnp.data.opcode == RCPOpcode.UnknownService:
                    return
            len_hrnp = len(hrnp.as_bytes())
            if hrnp.opcode == HRNPOpcodes.DATA:
                data_ack = HRNP(
                    opcode=HRNPOpcodes.DATA_ACK, packet_number=hrnp.packet_number
                )
                self.write(hrnp=data_ack)
            self.buffer_in = self.buffer_in[len_hrnp:]
        except:
            pass  # print(sys.exc_info())

    async def read(self) -> None:
        self.connect()
        self.is_running = True
        while self.is_running:
            radio_in = self.serial.read()
            if len(radio_in):
                self.buffer_in += radio_in
                # print(
                #     f"read {len(radio_in)} bytes ({radio_in.hex()}): {self.buffer_in.hex()}"
                # )
                self.parse_buffer_in(radio_in)

    def get_radio_id(self) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.RadioIDAndRadioIPQueryRequest,
                    # radio ID
                    target=0x00,
                ),
            )
        )

    def get_radio_ip(self) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.RadioIDAndRadioIPQueryRequest,
                    # radio ip
                    target=0x01,
                ),
            )
        )

    def set_broadcast(self, enabled: bool = True) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.BroadcastMessageConfigurationRequest,
                    broadcast_type=0b111 if enabled else 0b000,
                ),
            )
        )

    def set_status(self, enabled: bool = True) -> None:
        raw = b"\x01"
        # 0x01: Broadcast Receive Status(0xB844)
        raw += b"\x01\x01"

        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.BroadcastStatusConfigurationRequest,
                    broadcast_config_raw=raw,
                ),
            )
        )

    def handle_menu(self, user_input: str) -> None:
        print()
        _options: Dict[str, callable] = {
            "send-hrnp": lambda user_in: self.write(
                HRNP.from_bytes(bytes.fromhex(user_in))
            ),
            "connect": lambda _: self.connect(),
            "close": lambda _: self.close(),
            "set-broadcast": lambda _: self.set_broadcast(True),
            "unset-broadcast": lambda _: self.set_broadcast(False),
            "set-status": lambda _: self.set_status(True),
            "unset-status": lambda _: self.set_status(False),
            "quit": lambda _: self.throw(_type=KeyboardInterrupt),
            "help": lambda _: print(
                f"Available commands:\n"
                + "".join(f">> {key}\n" for key in _options.keys())
            ),
            "radio-id": lambda _: self.get_radio_id(),
            "radio-ip": lambda _: self.get_radio_ip(),
        }
        _keyword = user_input.split(" ")[0]
        if _keyword not in _options.keys():
            if len(_keyword):
                print(f"Unknown command {_keyword}")
            _keyword = "help"

        _options[_keyword](user_input)

    def stop(self) -> None:
        self.is_running = False

    def throw(self, _type=BaseException) -> None:
        raise _type()


if __name__ == "__main__":
    app: HRNPApp = HRNPApp()
    app_thread: Thread = Thread(target=lambda: asyncio.run(app.read()))
    app_thread.start()
    # sleep(1)

    while True:
        try:
            print()
            app.handle_menu(input("input: "))
        except EOFError:
            break
        except KeyboardInterrupt:
            break

    print(f"graceful stop")
    app.stop()
    app_thread.join()
