import asyncio
import struct
from asyncio import transports, Queue, DatagramProtocol
from binascii import hexlify, a2b_hex
from dataclasses import dataclass
from hashlib import sha256
from socket import socket
from typing import Optional, Callable, Tuple

from okdmr.dmrlib.utils.logging_trait import LoggingTrait


@dataclass
class MMDVMClientConfiguration:
    upstream_addr: Tuple[str, int]
    """ (ip address as string, port usually 62031) """
    repeater_id: int
    """ repeater_id  """
    callsign: str
    """ callsign string eg. OK4DMR """
    rx_freq: int = 0
    """ freq in Hz, 9 numbers """
    tx_freq: int = 0
    """ freq in Hz, 9 numbers """
    tx_power: int = 0
    """ 00 - 99 """
    color_code: int = 1
    """ 01 - 15 """
    latitude: str = ""
    """ example 51.500843 """
    longitude: str = ""
    """ example -0.126443 """
    height: int = 0
    """ 0-999 antenna height above ground in meters """
    location: str = ""
    """ at most 20 chars """
    description: str = ""
    """ at most 20 chars """
    url: str = ""
    """ at most 124 chars """
    software_id: str = ""
    """ at most 40 chars """
    package_id: str = ""
    """ at most 40 chars """


class MMDVMClientProtocol(DatagramProtocol, LoggingTrait):
    CON_NEW: int = 1
    CON_LOGIN_REQUEST_SENT: int = 2
    CON_LOGIN_RESPONSE_SENT: int = 3
    CON_LOGIN_SUCCESSFULL: int = 4
    CON_AUTHENTICATION_FAILED: int = 5

    def __init__(
        self,
        config: MMDVMClientConfiguration,
        connection_lost_callback: Callable,
        queue_outgoing: Queue,
        queue_incoming: Queue,
    ) -> None:
        self.config: MMDVMClientConfiguration = config
        self.transport: Optional[transports.DatagramTransport] = None
        self.connection_lost_callback = connection_lost_callback
        self.connection_status = self.CON_NEW
        self.queue_outgoing = queue_outgoing
        self.queue_incoming = queue_incoming

    async def periodic_maintenance(self) -> None:
        while not asyncio.get_running_loop().is_closed():
            await asyncio.sleep(5)
            if self.connection_status == self.CON_NEW:
                self.send_login_request()
            elif self.connection_status == self.CON_LOGIN_REQUEST_SENT:
                self.send_login_request()
            elif self.connection_status == self.CON_LOGIN_SUCCESSFULL:
                self.send_ping()
            elif self.connection_status == self.CON_AUTHENTICATION_FAILED:
                self.connection_status = self.CON_NEW
                self.send_login_request()

    async def send_mmdvm_from_queue(self) -> None:
        while not asyncio.get_running_loop().is_closed():
            packet: bytes = await self.queue_outgoing.get()
            if self.transport and not self.transport.is_closing():
                self.transport.sendto(packet)
                mmdvm: Mmdvm = Mmdvm.from_bytes(packet)
                self.log_debug(
                    common_log_format(
                        proto="HHB->MMDVM",
                        from_ip_port=(),
                        to_ip_port=(),
                        use_color=True,
                        packet_data=mmdvm.command_data,
                        dmrdata_hash=get_dmr_data_hash(mmdvm.command_data.dmr_data)
                        if isinstance(mmdvm.command_data, Mmdvm.TypeDmrData)
                        else "",
                    )
                )
            else:
                if not self.transport:
                    self.log_info(
                        f"Not sending packet, waiting for Hytera repeater to connect first"
                    )
                elif self.transport and self.transport.is_closing():
                    self.log_info(
                        f"Not sending packet due to MMDVM socket closing/being closed"
                    )

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.log_debug("MMDVM socket connected")
        if not self.transport or self.transport.is_closing():
            self.log_debug("Setting transport")
            self.transport = transport
            if self.connection_status is not self.CON_LOGIN_SUCCESSFULL:
                self.send_login_request()
        else:
            self.log_debug("ignoring new transport")
            hb_local_socket = transport.get_extra_info("socket")
            if isinstance(hb_local_socket, socket):
                self.log_warning(
                    f"Ignoring new transport {hb_local_socket.getsockname()}"
                )

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.log_debug("MMDVM socket closed")
        self.connection_status = self.CON_NEW
        if exc:
            self.log_exception(exc)
        self.connection_lost_callback()

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        packet = Mmdvm.from_bytes(data)
        is_handled: bool = False
        if isinstance(packet.command_data, Mmdvm.TypeMasterNotAccept):
            if self.connection_status == self.CON_LOGIN_REQUEST_SENT:
                self.connection_status = self.CON_NEW
                self.log_error("Master did not accept our login request")
                is_handled = True
            elif self.connection_status == self.CON_LOGIN_RESPONSE_SENT:
                self.connection_status = self.CON_NEW
                self.log_error("Master did not accept our password challenge response")
                is_handled = True
            elif self.connection_status == self.CON_LOGIN_SUCCESSFULL:
                self.connection_status = self.CON_NEW
                self.log_info("Connection timed-out or was interrupted, do login again")
                self.send_login_request()
                is_handled = True
        elif isinstance(packet.command_data, Mmdvm.TypeMasterRepeaterAck):
            if self.connection_status == self.CON_LOGIN_REQUEST_SENT:
                self.log_info("Sending Login Response")
                self.send_login_response(packet.command_data.repeater_id_or_challenge)
                is_handled = True
            elif self.connection_status == self.CON_LOGIN_RESPONSE_SENT:
                self.log_info("Master Login Accept")
                self.connection_status = self.CON_LOGIN_SUCCESSFULL
                self.send_configuration()
                is_handled = True
            elif self.connection_status == self.CON_LOGIN_SUCCESSFULL:
                self.log_info("Master accepted our configuration")
                is_handled = True
        elif isinstance(packet.command_data, Mmdvm.TypeMasterPong):
            self.log_debug("Master PONG received")
            is_handled = True
            pass
        elif isinstance(packet.command_data, Mmdvm.TypeMasterClosing):
            self.log_info("Master Closing connection")
            self.connection_status = self.CON_NEW
            is_handled = True
        elif isinstance(packet.command_data, Mmdvm.TypeDmrData):
            self.queue_incoming.put_nowait(packet)
            is_handled = True
        if not is_handled:
            self.log_error(
                f"UNHANDLED {packet.__class__.__name__} {packet.command_data.__class__.__name__} {hexlify(data)} status {self.connection_status}"
            )

    def send_login_request(self) -> None:
        self.log_info("Sending Login Request")
        self.connection_status = self.CON_LOGIN_REQUEST_SENT
        self.queue_outgoing.put_nowait(
            struct.pack(">4sI", b"RPTL", self.settings.get_repeater_dmrid())
        )

    def send_login_response(self, challenge: int) -> None:
        self.log_info("Sending Login Response (Challenge response)")
        self.connection_status = self.CON_LOGIN_RESPONSE_SENT
        challenge_response = struct.pack(
            ">4sI32s",
            b"RPTK",
            self.settings.get_repeater_dmrid(),
            a2b_hex(
                sha256(
                    b"".join(
                        [
                            challenge.to_bytes(length=4, byteorder="big"),
                            self.settings.hb_password.encode(),
                        ]
                    )
                ).hexdigest()
            ),
        )
        self.queue_outgoing.put_nowait(challenge_response)

    def send_configuration(self) -> None:
        self.log_info(f"Sending self configuration to master")
        packet = struct.pack(
            ">4sI8s9s9s2s2s8s9s3s20s19s1s124s40s40s",
            b"RPTC",
            self.settings.get_repeater_dmrid(),
            self.settings.get_repeater_callsign()[0:8].ljust(8).encode(),
            self.settings.get_repeater_rx_freq()[0:9].rjust(9, "0").encode(),
            self.settings.get_repeater_tx_freq()[0:9].rjust(9, "0").encode(),
            str(self.settings.hb_tx_power & 0xFFFF).rjust(2, "0").encode(),
            str(self.settings.hb_color_code & 0xF).rjust(2, "0").encode(),
            self.settings.hb_latitude[0:8].rjust(8, "0").encode(),
            self.settings.hb_longitude[0:9].rjust(9, "0").encode(),
            str(min(max(self.settings.hb_antenna_height, 0), 999))[0:3]
            .rjust(3, "0")
            .encode(),
            self.settings.hb_location[0:20].ljust(20).encode(),
            self.settings.hb_description[0:19].ljust(19).encode(),
            self.settings.hb_timeslots[0:1].encode(),
            self.settings.hb_url[0:124].ljust(124).encode(),
            self.settings.hb_software_id[0:40].ljust(40).encode(),
            self.settings.hb_package_id[0:40].ljust(40).encode(),
        )

        self.queue_outgoing.put_nowait(packet)

        config: Mmdvm = Mmdvm.from_bytes(packet)
        log_mmdvm_configuration(logger=self.get_logger(), packet=config)

    def send_ping(self) -> None:
        self.log_debug("Sending PING")
        packet = struct.pack(">7sI", b"RPTPING", self.settings.get_repeater_dmrid())
        self.queue_outgoing.put_nowait(packet)

    def send_closing(self) -> None:
        self.log_info("Closing MMDVM connection")
        packet = struct.pack(">5sI", b"RPTCL", self.settings.get_repeater_dmrid())
        self.queue_outgoing.put_nowait(packet)

    def disconnect(self) -> None:
        if self.transport and not self.transport.is_closing():
            self.send_closing()
