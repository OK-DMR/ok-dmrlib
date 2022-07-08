from typing import Dict

from okdmr.dmrlib.motorola.mbxml import (
    MBXMLDocument,
    MBXMLDocumentIdentifier,
    MBXMLTokenType,
    MBXMLToken,
)


class ARRP(MBXMLDocument):
    """
    Placeholder for Accessories Request/Response Protocol
    """

    @staticmethod
    def get_configuration(
        doc_type: MBXMLDocumentIdentifier,
    ) -> Dict[MBXMLTokenType, Dict[int, MBXMLToken]]:
        pass
