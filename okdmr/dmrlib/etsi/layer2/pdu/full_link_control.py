from typing import Union, Optional

from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer3.elements.position_error import PositionError
from okdmr.dmrlib.etsi.layer3.elements.service_options import ServiceOptions
from okdmr.dmrlib.etsi.layer3.elements.talker_alias_data_format import (
    TalkerAliasDataFormat,
)
from okdmr.dmrlib.utils.bits_interface import BitsInterface


class FullLinkControl(BitsInterface):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.1.6  Full Link Control (FULL LC) PDU
    ETSI TS 102 361-2 V2.4.1 (2017-10) - 7.1.1  Full Link Control PDUs
    """

    def __init__(
        self,
        protect_flag: Union[int, bool],
        flco: FLCOs,
        fid: FeatureSetIDs,
        # Table 7.1: Grp_V_Ch_Usr PDU content
        service_options: Optional[ServiceOptions] = None,
        group_address: int = 0,
        source_address: int = 0,
        # Table 7.2: UU_V_Ch_Usr PDU content
        target_address: int = 0,
        # Table 7.3: GPS Info PDU content
        position_error: Optional[PositionError] = None,
        longitude: int = 0,
        latitude: int = 0,
        # Table 7.4: Talker Alias header Info PDU content
        talker_alias_data_format: Optional[TalkerAliasDataFormat] = None,
        talker_alias_data_length: int = 0,
        talker_alias_data_msb: Union[int, bool] = 0,
        # without msb talker alias header data are 48bits (6bytes)
        talker_alias_data: bytes = b""
        # Table 7.5: Talker Alias block Info PDU content
        # talker alias blocks 1,2,3 use "talker_alias_data" field, since data are 56bits (7bytes)
    ):
        self.protect_flag: bool = protect_flag in (True, 1)
        self.full_link_control_opcode: FLCOs = flco
        self.feature_set_id: FeatureSetIDs = fid
        self.service_options: Optional[ServiceOptions] = service_options
        self.group_address: int = group_address
        self.source_address: int = source_address
        self.target_address: int = target_address
        self.position_error: Optional[PositionError] = position_error
        self.longitude: int = longitude
        self.latitude: int = latitude
        self.talker_alias_data_format: Optional[
            TalkerAliasDataFormat
        ] = talker_alias_data_format
        self.talker_alias_data_length: int = talker_alias_data_length
        self.talker_alias_data_msb: bool = talker_alias_data_msb in (True, 1)
        self.talker_alias_data: bytes = talker_alias_data
