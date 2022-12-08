import asyncio
import sys
from time import sleep
from typing import List

from okdmr.dmrlib.hytera.pdu.hrnp import HRNP, HRNPOpcodes
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RadioControlProtocol,
    RCPOpcode,
)
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HRNPApp(LoggingTrait):
    def __init__(self):
        from serial import Serial

        self.serial: Serial = Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=2)
        self.counter: int = 0
        self.buffer_in: bytes = b""
        self.source_id: int = 0x20
        self.buffer_out: List[bytes] = []

    def write(self, hrnp: HRNP) -> None:
        sleep(0.1)
        # modify
        hrnp.source = self.source_id
        if hrnp.opcode != HRNPOpcodes.DATA_ACK:
            hrnp.packet_number = self.counter
            self.counter += 1
        # log
        print(f"write {hrnp.as_bytes().hex()}")
        print(repr(hrnp))
        # write out
        self.serial.write(hrnp.as_bytes())

    def connect(self) -> None:
        hrnp = HRNP.from_bytes(bytes.fromhex("7e0400fe20100000000c60e1"))
        self.write(hrnp)

    def try_print_hrnp(self, data: bytes) -> None:
        try:
            while self.buffer_in[0] != 0x7E:
                self.buffer_in = self.buffer_in[1:]
            hrnp = HRNP.from_bytes(self.buffer_in)
            if hrnp.opcode == HRNPOpcodes.DATA and isinstance(
                hrnp.data, RadioControlProtocol
            ):
                if hrnp.data.opcode == RCPOpcode.UnknownService:
                    return
            print(f"receive {repr(hrnp)}")
            len_hrnp = len(hrnp.as_bytes())
            if hrnp.opcode == HRNPOpcodes.DATA:
                data_ack = HRNP(
                    opcode=HRNPOpcodes.DATA_ACK, packet_number=hrnp.packet_number
                )
                self.write(hrnp=data_ack)
            self.buffer_in = self.buffer_in[len_hrnp:]
            print(f"buffer after {self.buffer_in.hex()}")
            if hrnp.opcode == HRNPOpcodes.ACCEPT:
                hrno = HRNP(
                    opcode=HRNPOpcodes.DATA,
                    data=RadioControlProtocol(
                        opcode=RCPOpcode.BroadcastMessageConfigurationRequest
                    ),
                )
                self.write(hrno)
        except:
            pass  # print(sys.exc_info())

    async def read(self) -> None:
        self.connect()
        while True:
            radio_in = self.serial.read()
            if len(radio_in):
                print(f"from radio: {radio_in.hex()}")
                self.buffer_in += radio_in
                if len(self.buffer_in):
                    print(f"buffer {self.buffer_in.hex()}")
                self.try_print_hrnp(radio_in)


if __name__ == "__main__":
    app: HRNPApp = HRNPApp()
    asyncio.run(app.read())
    while True:
        userinput = input("input: ")
        try:
            app.serial.write(bytes.fromhex(userinput.strip()))
        except:
            print(sys.exc_info())
