import sys
from copy import copy
from typing import Union, Callable

from okdmr.dmrlib.tools.dmrlib_tool import DmrlibTool


def single_hytera_proto_test(
    capsys, payload: Union[str, bytes], proto: Callable
) -> None:
    payload: str = payload if isinstance(payload, str) else payload.hex()
    sys.argv = ["dmrlib-dmr-mock", payload]
    proto()
    captured = capsys.readouterr()
    assert len(captured.out)
    assert not len(captured.err)


def test_hytera_tool(capsys) -> None:
    argv_backup = copy(sys.argv)

    single_hytera_proto_test(
        capsys,
        # [BsSourcedData] [DataTypes.CSBK] [CC: 5]
        # 	[CsbkOpcodes.PreambleCSBK] [LB: 1] [PF: 0] [FeatureSetIDs.StandardizedFID] [TARGET IS INDIVIDUAL] [FOLLOWED BY DATA] [BTF: 29] [DST ADDR: 2308195] [SRC ADDR: 2308155
        payload="53df0a83b7a8282c2509625014fdff57d75df5dcadde429028c87ae3341e24191c",
        proto=DmrlibTool.burst,
    )

    single_hytera_proto_test(
        capsys,
        # [IPv4 id: 512] [IP src: IPAddressIdentifier.RadioNetwork] [IP dst: IPAddressIdentifier.Reserved] [UDP src: UDPPortIdentifier.ManufacturerSpecific (120)] [UDP dst: UDPPortIdentifier.ManufacturerSpecific (120)]  [DATA: 0980be001000000001000000010a00000101020304cd03000000004172f253]
        payload="02000278780980BE001000000001000000010A00000101020304CD03000000004172F253",
        proto=DmrlibTool.ipudp,
    )

    single_hytera_proto_test(
        capsys,
        # [DataPacketFormats.DataPacketUnconfirmed] [SAPIdentifier.UDP_IP_compression] [TARGET IS GROUP] [PAD OCTETS: 4] [SOURCE: 1001] [DESTINATION: 1] [FullMessageFlag.FirstTryToCompletePacket] [BTF: 3] [FSN: Unconfirmed data single fragment]
        payload="82340000010003E98300CF77",
        proto=DmrlibTool.header,
    )

    sys.argv = argv_backup


def test_throwing_pdu(capsys):
    argv_backup = copy(sys.argv)

    sys.argv = ["dmrlib-mock-throwing", "ABCDEF"]
    DmrlibTool.ipudp()

    captured = capsys.readouterr()
    # de-serialization error appears here
    assert len(captured.err)
    assert "got 24 instead" in captured.err
    # raw input appears here
    assert len(captured.out)
    assert "ABCDEF" in captured.out

    sys.argv = argv_backup
