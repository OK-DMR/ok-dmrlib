import enum
from typing import Any

from bitarray import bitarray
from bitarray.util import int2ba, ba2int

from okdmr.dmrlib.utils.bits_interface import BitsInterface


@enum.unique
class CsbkOpcodes(BitsInterface, enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.3.32 Control Signalling BlocK Opcode (CSBKO)
    ETSI TS 102 361-4 V1.10.1 (2019-08) - B.1   CSBK/MBC/UDT Opcode List
    """

    # Tier II
    UnitToUnitVoiceServiceRequest = 0b000100
    """UU_V_Req"""
    UnitToUnitVoiceServiceAnswerResponse = 0b000101
    """UU_Ans_Rsp"""
    ChannelTimingCSBK = 0b000111
    """CT_CSBK"""
    NegativeAcknowledgementResponse = 0b100110
    """NACK_Rsp"""
    BSOutboundActivation = 0b111000
    """BS_Dwn_Act"""
    PreambleCSBK = 0b111101
    """Pre_CSBK"""

    # Tier III
    # [+] Channel Grant
    PrivateVoiceChannelGrant = 0b110000
    """PV_GRANT"""
    TalkgroupVoiceChannelGrant = 0b110001
    """TV_GRANT"""
    PrivateBroadcastVoiceChannelGrant = 0b110010
    """BTV_GRANT"""
    PrivateDataChannelGrantSingleItem = 0b110011
    """PD_GRANT"""
    TalkgroupDataChannelGrantSingleItem = 0b110100
    """TD_GRANT"""
    DuplexPrivateVoiceChannelGrant = 0b110101
    """PV_GRANT_DX"""
    DuplexPrivateDataChannelGrant = 0b110110
    """PD_GRANT_DX"""
    PrivateDataChannelGrantMultiItem = 0b110111
    """PD_GRANT_MI"""
    # TODO: solve conflict TD_GRANT_MI and BS_Dwn_Act
    # TalkgroupDataChannelGrantMultiItem = 0b111000
    # """TD_GRANT_MI"""
    # [-] Channel Grant

    MovePDUs = 0b111001
    """C_MOVE"""

    AlohaPDUsForRandomAccessProtocol = 0b011001
    """C_ALOHA"""

    # [+] Announcements
    AnnouncementPDUsWithoutResponse = 0b101000
    """
    C_BCAST
    
    Announcement PDUs that shall not demand a response.
    Announce/Withdraw TSCC
    Specify call Timers
    Vote now advice
    Announce local time
    Broadcast Mass Registration
    Announce a logical physical channel relationship
    Announce adjacent site information
    """
    Clear = 0b101110
    """P_CLEAR"""
    Protect = 0b101111
    """P_PROTECT"""
    # [-] Announcements
    Ahoy = 0b011100
    """
    C_AHOY / P_AHOY
    Ahoy - enquiry from the TSCC that demands a response from MS
    """
    # [+] Acknowledgements
    AcknowledgementResponseOutboundTSCC = 0b100000
    """C_ACKD"""
    AcknowledgementResponseInboundTSCC = 0b100001
    """C_ACKU"""
    AcknowledgementResponseOutboundPayload = 0b100010
    """P_ACKD"""
    AcknowledgementResponseInboundPayload = 0b100011
    """P_ACKU"""
    # [-] Acknowledgements
    # [+] UDT header
    UnifiedDataTransportOutboundHeader = 0b011010
    """C_UDTHD"""
    UnifiedDataTransportInboundHeader = 0b011011
    """C_UDTHU"""
    UnifiedDataTransportForDGNAOutboundHeader = 0b100100
    """C_DGNAHD"""
    UnifiedDataTransportForDGNAInboundHeader = 0b100101
    """C_DGNAHU"""
    # [-] UDT header

    RandomAccessServiceRequest = 0b011111
    """C_RAND"""
    AckvitationPDU = 0b011110
    """C_ACKVIT"""
    Maintenance = 0b101010
    """P_MAINT"""

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise ValueError(f"CsbkOpcodes value {value} is undefined")

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=6)

    @staticmethod
    def from_bits(bits: bitarray) -> "CsbkOpcodes":
        return CsbkOpcodes(ba2int(bits[0:6]))
