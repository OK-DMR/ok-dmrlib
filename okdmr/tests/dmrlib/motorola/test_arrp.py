from okdmr.dmrlib.motorola.arrp import ARRP
from okdmr.dmrlib.motorola.mbxml import MBXMLDocumentIdentifier


def test_arrp():
    assert (
        len(
            ARRP.get_configuration(
                MBXMLDocumentIdentifier.ARRP_ImmediateInformationRequest
            )
        )
        == 0
    )
