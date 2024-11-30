from asyncio import Queue
from typing import Callable

import pytest

from okdmr.dmrlib.protocols.mmdvm.mmdvm_client_protocol import (
    MMDVMClientProtocol,
    MMDVMClientConfiguration,
)


@pytest.mark.asyncio
async def test_mmdvm_client():
    mock_config: MMDVMClientConfiguration = MMDVMClientConfiguration(
        # fill only required vars
        repeater_id=2309901,
        upstream_addr=("127.0.0.1", 62031),
        callsign="OK0DMR TEST",
    )
    q_in: Queue = Queue()
    q_out: Queue = Queue()
    cb_conn_lost: Callable[[], None] = lambda: print("Connection lost")
    c: MMDVMClientProtocol = MMDVMClientProtocol(
        config=mock_config,
        queue_incoming=q_in,
        queue_outgoing=q_out,
        connection_lost_callback=cb_conn_lost,
    )
