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

    sys.argv = argv_backup
