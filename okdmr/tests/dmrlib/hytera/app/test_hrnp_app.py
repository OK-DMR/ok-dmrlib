import asyncio
import traceback
from threading import Thread
from time import sleep
from typing import List, Dict

from okdmr.dmrlib.hytera.pdu.hrnp import HRNP, HRNPOpcodes
from okdmr.dmrlib.hytera.pdu.location_protocol import (
    LocationProtocol,
    LocationProtocolSpecificService,
)
from okdmr.dmrlib.hytera.pdu.radio_control_protocol import (
    RadioControlProtocol,
    RCPOpcode,
    RadioIpIdTarget,
)
from okdmr.dmrlib.hytera.pdu.radio_ip import RadioIP
from okdmr.dmrlib.hytera.pdu.text_message_protocol import (
    TextMessageProtocol,
    TMPService,
)
from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class HRNPApp(LoggingTrait):
    def __init__(self):
        from serial import Serial

        self.serial: Serial = Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=0)
        self.counter_hrnp: int = 0
        self.counter_tmp_sdsmp: int = 0
        self.buffer_in: bytes = b""
        self.source_id: int = 0x20
        self.self_radio_id: int = 0
        self.self_radio_ip: RadioIP = RadioIP(radio_id=1)
        self.buffer_out: List[bytes] = []
        self.is_running: bool = False

    def write(self, hrnp: HRNP) -> None:
        sleep(0.1)
        # modify
        hrnp.source = self.source_id
        if hrnp.opcode != HRNPOpcodes.DATA_ACK:
            hrnp.packet_number = self.counter_hrnp
            self.counter_hrnp = (self.counter_hrnp + 1) % 0xFFFF
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
        self.counter_hrnp = 0
        self.write(HRNP(opcode=HRNPOpcodes.CONNECT))

    def parse_buffer_in(self) -> None:
        try:
            print(f"parse_buffer_in {self.buffer_in.hex()}")
            if not len(self.buffer_in):
                return
            # clear buffer until we find expected HRNP header byte
            while self.buffer_in[0] != 0x7E:
                self.buffer_in = self.buffer_in[1:]
            # min length requirement
            if len(self.buffer_in) < 12:
                return
            hrnp_len: int = int.from_bytes(self.buffer_in[8:10], byteorder="big")
            if len(self.buffer_in) < hrnp_len:
                return
            # try parse HRNP from buffer_in
            hrnp = HRNP.from_bytes(self.buffer_in)
            print(f"received : {self.buffer_in.hex().upper()}")
            print(repr(hrnp))
            if hrnp.opcode == HRNPOpcodes.DATA and isinstance(
                hrnp.data, RadioControlProtocol
            ):
                if hrnp.data.opcode == RCPOpcode.UnknownService:
                    # do not confirm invalid / unknown packets
                    return
                if hrnp.data.opcode == RCPOpcode.RadioIDAndRadioIPQueryReply:
                    if hrnp.data.radio_ip_id_target == RadioIpIdTarget.RADIO_IP:
                        self.self_radio_ip = RadioIP.from_bytes(hrnp.data.raw_value)
                        print(f"set radio_ip {repr(self.self_radio_ip)}")
                    elif hrnp.data.radio_ip_id_target == RadioIpIdTarget.RADIO_ID:
                        self.self_radio_id = int.from_bytes(
                            hrnp.data.raw_value, signed=False, byteorder="little"
                        )
                        print(f"set radio_id {self.self_radio_id}")

            len_hrnp = len(hrnp.as_bytes())
            if hrnp.opcode == HRNPOpcodes.DATA:
                data_ack = HRNP(
                    opcode=HRNPOpcodes.DATA_ACK, packet_number=hrnp.packet_number
                )
                self.write(hrnp=data_ack)

            self.buffer_in = self.buffer_in[len_hrnp:]
        except:
            traceback.print_last()

    async def read(self) -> None:
        self.connect()
        self.is_running = True
        while self.is_running:
            radio_in = self.serial.read()
            if len(radio_in):
                self.buffer_in += radio_in
                # print(f"read {self.buffer_in.hex().upper()}")
                self.parse_buffer_in()

    def get_radio_id(self) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.RadioIDAndRadioIPQueryRequest,
                    # radio ID
                    target=RadioIpIdTarget.RADIO_ID,
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
                    target=RadioIpIdTarget.RADIO_IP,
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
        raw = b"\x02"
        status = b"\x01" if enabled else b"\x00"
        # 0x00: Broadcast Transmit Status(0xB843)
        raw += b"\x00" + status
        # 0x01: Broadcast Receive Status(0xB844)
        raw += b"\x01" + status

        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.BroadcastStatusConfigurationRequest,
                    broadcast_config_raw=raw,
                ),
            )
        )

    def send_location_request(self) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=LocationProtocol(
                    opcode=LocationProtocolSpecificService.StandardRequest,
                    request_id=1,
                    radio_ip=RadioIP(radio_id=1001, subnet=10),
                ),
            )
        )

    def send_short_data(self, user_in: str, group: bool = False) -> None:
        if user_in.strip() in ("sgsd", "spsd"):
            print("Send short data help:")
            print("sgsd - Send Group Short Data")
            print("spsd - Send Private Short Data")
            print("usage: sgsd TARGET_ID HEX-BYTES-PAYLOAD")
            return

        (_cmd, _target_id, _hex_payload) = user_in.split(" ")
        print(f"_cmd {_cmd} target {_target_id} hex {_hex_payload}")

        self.counter_tmp_sdsmp += 1
        print(f"{_target_id} as int {int(_target_id)}")
        pkt = HRNP(
            opcode=HRNPOpcodes.DATA,
            data=TextMessageProtocol(
                opcode=(
                    TMPService.GroupShortData if group else TMPService.PrivateShortData
                ),
                source_ip=self.self_radio_ip,
                destination_ip=RadioIP(subnet=0, radio_id=int(_target_id)),
                short_data=bytes.fromhex(_hex_payload),
                is_confirmed=False,
                is_reliable=False,
                request_id=self.counter_tmp_sdsmp,
            ),
        )
        self.write(pkt)

    def set_zone_channel(self, user_in: str) -> None:
        try:
            (_cmd, _zone, _channel) = user_in.split(" ")
            self.write(
                HRNP(
                    opcode=HRNPOpcodes.DATA,
                    data=RadioControlProtocol(
                        opcode=RCPOpcode.ZoneAndChannelOperationRequest,
                        raw_payload=b"\x00"
                        + int(_zone).to_bytes(length=2, byteorder="little")
                        + int(_channel).to_bytes(length=2, byteorder="little"),
                    ),
                )
            )
        except:
            print(f"usage set-zone-channel [ZONE-NUM] [CHANNEL-NUM]")

    def get_zone_channel(self) -> None:
        self.write(
            HRNP(
                opcode=HRNPOpcodes.DATA,
                data=RadioControlProtocol(
                    opcode=RCPOpcode.ZoneAndChannelOperationRequest,
                    raw_payload=b"\x01\x00\x00\x00\x00",
                ),
            )
        )

    def handle_menu(self, user_input: str) -> None:
        print()
        _options: Dict[str, callable] = {
            "send-hrnp": lambda user_in: self.write(
                HRNP.from_bytes(bytes.fromhex(str(user_in).split(" ")[1]))
            ),
            "connect": lambda _: self.connect(),
            "close": lambda _: self.close(),
            "set-broadcast": lambda _: self.set_broadcast(True),
            "unset-broadcast": lambda _: self.set_broadcast(False),
            "set-status": lambda _: self.set_status(True),
            "unset-status": lambda _: self.set_status(False),
            "quit": lambda _: self.throw(_type=KeyboardInterrupt),
            "location": lambda _: self.send_location_request(),
            "help": lambda _: print(
                f"Available commands:\n"
                + "".join(f">> {key}\n" for key in _options.keys())
            ),
            "radio-id": lambda _: self.get_radio_id(),
            "radio-ip": lambda _: self.get_radio_ip(),
            "sgsd": lambda user_in: self.send_short_data(group=True, user_in=user_in),
            "spsd": lambda user_in: self.send_short_data(user_in=user_in),
            "set-zc": lambda user_in: self.set_zone_channel(user_in=user_in),
            "get-zc": lambda _: self.get_zone_channel(),
        }
        _keyword = user_input.split(" ")[0]
        if _keyword not in _options.keys():
            if len(_keyword):
                print(f"Unknown command {_keyword}")
            _keyword = "help"

        try:
            _options[_keyword](user_input)
        except:
            print(f"Menu Handler {_keyword} failed")
            traceback.print_last()

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
