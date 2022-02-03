import sys
from typing import List

from okdmr.kaitai.homebrew.mmdvm2020 import Mmdvm2020

from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_type import BurstType
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns


def test_burst_info(capsys):
    bursts: List[str] = [
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d5244192807220000090028072290864b516baded847205ae0062959308849047f7d5dd57dfd9537a101efe3ed4206e153827e70139",
        # [BsSourcedData] [CC 5] [DATA TYPE CSBK] [FEC 0f2b VERIFIED]
        "444d52440223383b2338630006690f632e40c70153df0a83b7a8282c2509625014fdff57d75df5dcadde429028c87ae3341e24191c003c",
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d5244492807220000090028072290864b516beab8e5564609e61dc5eaa8e55647f7d5dd57dfd709e61dd5eaa8e5564709e73cc5013a",
        # [MsSourcedVoice] [CC 0] [DATA TYPE Reserved]
        "444d52449128072200000900280722907cd1c462d8bac5704529d00ed0c8aac57047f7d5dd57dfd529d00fd1c8aac570452bd11fd10130",
        # [EmbeddedData] [CC 1] [DATA TYPE Reserved] [PI 0] [LCSS 3] [EMB Parity 0091 VERIFIED]
        "444d52440320baef0000090020baef8100000001b9e881526173002a6bb9e8815261303000a0391173002a6bb9e881526173002a6b3334",
    ]
    for burst_hex in bursts:
        mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(burst_hex))
        assert isinstance(mmdvm.command_data, Mmdvm2020.TypeDmrData)
        burst: Burst = Burst.from_mmdvm(mmdvm=mmdvm.command_data)
        if burst.has_emb:
            assert burst.emb.emb_parity
            assert burst.sync_or_embedded_signalling == SyncPatterns.EmbeddedSignalling
            assert burst.data_type == DataTypes.Reserved
        elif burst.has_slot_type:
            assert burst.slot_type.fec_parity_ok
            assert isinstance(burst.data_type, DataTypes)

        burst.set_sequence_no(128)
        assert burst.sequence_no == 128

        burst.set_stream_no(b"\xFF\xAA")
        assert burst.stream_no == b"\xFF\xAA"

        noprintdebug: str = repr(burst)
        assert len(noprintdebug) > 0

        printdebug: str = burst.debug(printout=True)
        assert len(printdebug) > 0
        out, err = capsys.readouterr()
        assert len(out) > 0
        assert len(err) < 1


if __name__ == "__main__":
    ks_mmdvm: Mmdvm2020 = Mmdvm2020.from_bytes(bytes.fromhex(sys.argv[1]))
    assert isinstance(ks_mmdvm.command_data, Mmdvm2020.TypeDmrData)
    m_burst_info: Burst = Burst.from_mmdvm(mmdvm=ks_mmdvm.command_data)
    m_burst_info.debug(printout=True)
