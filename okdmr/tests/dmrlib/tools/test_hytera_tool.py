import sys
from copy import copy
from typing import Union, Callable

from okdmr.dmrlib.tools.hytera_tool import HyteraTool


def single_hytera_proto_test(
    capsys, payload: Union[str, bytes], proto: Callable
) -> None:
    payload: str = payload if isinstance(payload, str) else payload.hex()
    sys.argv = ["dmrlib-hytera-mock", payload]
    proto()
    captured = capsys.readouterr()
    assert len(captured.out)
    assert not len(captured.err)


def test_hytera_tool(capsys) -> None:
    argv_backup = copy(sys.argv)

    single_hytera_proto_test(
        capsys,
        payload="324200200001830400066b0e04010111000300040a2337facd03",
        proto=HyteraTool.hstrp,
    )
    single_hytera_proto_test(
        capsys, payload="7e0400fe20100000000c60e1", proto=HyteraTool.hrnp
    )
    single_hytera_proto_test(
        capsys, payload="02040005006400000001c403", proto=HyteraTool.hdap
    )
    single_hytera_proto_test(
        capsys,
        payload="08a0020032000000010a2110dd0000413138333634383236313031354e343731382e383035314530313835342e34333837302e313132310b03",
        proto=HyteraTool.lp,
    )
    single_hytera_proto_test(
        capsys, payload="024108050000d20400000e03", proto=HyteraTool.rcp
    )
    single_hytera_proto_test(
        capsys, payload="11000100040a2337facf03", proto=HyteraTool.rrs
    )
    single_hytera_proto_test(
        capsys, payload="0980a2000D000000010a01b2070a030000003103", proto=HyteraTool.tmp
    )

    sys.argv = argv_backup
