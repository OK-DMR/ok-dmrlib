from typing import Union, Optional

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from okdmr.dmrlib.etsi.layer2.elements.feature_set_ids import FeatureSetIDs
from okdmr.dmrlib.etsi.layer2.elements.flcos import FLCOs
from okdmr.dmrlib.etsi.layer3.elements.position_error import PositionError
from okdmr.dmrlib.etsi.layer3.elements.service_options import ServiceOptions
from okdmr.dmrlib.etsi.layer3.elements.talker_alias_data_format import (
    TalkerAliasDataFormat,
)
from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits
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
        crc: bitarray,
        # Table 7.1: Grp_V_Ch_Usr PDU content
        service_options: Optional[ServiceOptions] = None,
        group_address: int = 0,
        source_address: int = 0,
        # Table 7.2: UU_V_Ch_Usr PDU content
        target_address: int = 0,
        # Table 7.3: GPS Info PDU content
        position_error: Optional[PositionError] = None,
        longitude: float = 0,
        latitude: float = 0,
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
        self.crc: bitarray = crc
        self.service_options: Optional[ServiceOptions] = service_options
        self.group_address: int = group_address
        self.source_address: int = source_address
        self.target_address: int = target_address
        self.position_error: Optional[PositionError] = position_error
        self.longitude: float = longitude
        self.latitude: float = latitude
        self.talker_alias_data_format: Optional[
            TalkerAliasDataFormat
        ] = talker_alias_data_format
        self.talker_alias_data_length: int = talker_alias_data_length
        self.talker_alias_data_msb: bool = talker_alias_data_msb in (True, 1)
        self.talker_alias_data: bytes = talker_alias_data

    def __repr__(self) -> str:
        descr: str = (
            f"[FLCO: {self.full_link_control_opcode}] [FID:{self.feature_set_id}] "
        )

        if self.full_link_control_opcode == FLCOs.UnitToUnitVoiceChannelUser:
            return descr + (
                f"[SOURCE: {self.source_address}] [TARGET: {self.target_address}] {repr(self.service_options)}"
            )
        elif self.full_link_control_opcode == FLCOs.GroupVoiceChannelUser:
            return descr + (
                f"[SOURCE: {self.source_address}] [GROUP: {self.group_address}] {repr(self.service_options)}"
            )
        elif self.full_link_control_opcode == FLCOs.GPSInfo:
            return descr + (
                f"[{self.position_error}] [LAT: {self.latitude}] [LON: {self.longitude}]"
            )
        elif self.full_link_control_opcode == FLCOs.TalkerAliasHeader:
            return descr + (
                f"[{self.talker_alias_data_format}] [Talker Alias Data Length: {self.talker_alias_data_length}] [{self.talker_alias_data.decode('ascii')}]"
            )
        elif self.full_link_control_opcode in (
            FLCOs.TalkerAliasBlock1,
            FLCOs.TalkerAliasBlock2,
            FLCOs.TalkerAliasBlock3,
        ):
            return descr + (
                f"[{self.talker_alias_data.hex()}] [utf16le: {self.talker_alias_data.decode('ascii')}]"
            )

        raise KeyError(f"FullLinkControl.__repr__ does not support " + descr)

    @staticmethod
    def from_bits(bits: bitarray) -> "FullLinkControl":
        assert len(bits) in (
            96,
            77,
        ), f"Unexpected Full LC bits length, expected 96 (reed-solomon) or 77 (5-bit checksum), got {len(bits)}"
        flco: FLCOs = FLCOs.from_bits(bits[2:8])
        pf: int = bits[0]
        fid: FeatureSetIDs = FeatureSetIDs.from_bits(bits[8:16])
        crc: bitarray = bits[72:96] if len(bits) >= 96 else bits[72:77]
        if flco == FLCOs.UnitToUnitVoiceChannelUser:
            return FullLinkControl(
                protect_flag=pf,
                fid=fid,
                crc=crc,
                flco=flco,
                service_options=ServiceOptions.from_bits(bits[16:24]),
                target_address=ba2int(bits[24:48]),
                source_address=ba2int(bits[48:72]),
            )
        elif flco == FLCOs.GroupVoiceChannelUser:
            return FullLinkControl(
                protect_flag=pf,
                fid=fid,
                crc=crc,
                flco=flco,
                service_options=ServiceOptions.from_bits(bits[16:24]),
                group_address=ba2int(bits[24:48]),
                source_address=ba2int(bits[48:72]),
            )
        elif flco == FLCOs.GPSInfo:
            return FullLinkControl(
                protect_flag=pf,
                fid=fid,
                crc=crc,
                flco=flco,
                position_error=PositionError.from_bits(bits[20:23]),
                longitude=(360 / 2**25) * ba2int(bits[23:48], signed=True),
                latitude=(180 / 2**24) * ba2int(bits[48:72], signed=True),
            )
        elif flco == FLCOs.TalkerAliasHeader:
            return FullLinkControl(
                protect_flag=pf,
                fid=fid,
                crc=crc,
                flco=flco,
                talker_alias_data_format=TalkerAliasDataFormat.from_bits(bits[16:18]),
                talker_alias_data_length=ba2int(bits[18:23]),
                talker_alias_data_msb=bits[23],
                talker_alias_data=bits[24:72].tobytes(),
            )
        elif flco in (
            FLCOs.TalkerAliasBlock1,
            FLCOs.TalkerAliasBlock2,
            FLCOs.TalkerAliasBlock3,
        ):
            return FullLinkControl(
                protect_flag=pf,
                fid=fid,
                crc=crc,
                flco=flco,
                talker_alias_data=bits[16:72].tobytes(),
            )

        raise KeyError(f"Not-implemented FLCO {flco}")

    def as_bits(self) -> bitarray:
        common: bitarray = (
            bitarray([self.protect_flag, 0])
            + self.full_link_control_opcode.as_bits()
            + self.feature_set_id.as_bits()
        )

        if self.full_link_control_opcode == FLCOs.UnitToUnitVoiceChannelUser:
            common += (
                self.service_options.as_bits()
                + int2ba(self.target_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.full_link_control_opcode == FLCOs.GroupVoiceChannelUser:
            common += (
                self.service_options.as_bits()
                + int2ba(self.group_address, length=24)
                + int2ba(self.source_address, length=24)
            )
        elif self.full_link_control_opcode == FLCOs.GPSInfo:
            common += (
                bitarray([0] * 4)
                + self.position_error.as_bits()
                + int2ba(int(self.longitude / (360 / 2**25)), length=25, signed=True)
                + int2ba(int(self.latitude / (180 / 2**24)), length=24, signed=True)
            )
        elif self.full_link_control_opcode == FLCOs.TalkerAliasHeader:
            common += (
                self.talker_alias_data_format.as_bits()
                + int2ba(self.talker_alias_data_length, length=5)
                + bitarray([self.talker_alias_data_msb])
                + bytes_to_bits(self.talker_alias_data)
            )
        elif self.full_link_control_opcode in (
            FLCOs.TalkerAliasBlock1,
            FLCOs.TalkerAliasBlock2,
            FLCOs.TalkerAliasBlock3,
        ):
            common += bytes_to_bits(self.talker_alias_data)
        else:
            raise KeyError(
                f"as_bits unimplemented FLCO {self.full_link_control_opcode}"
            )

        return common + self.crc
