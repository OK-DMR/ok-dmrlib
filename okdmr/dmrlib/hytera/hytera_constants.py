from okdmr.kaitai.hytera.ip_site_connect_protocol import IpSiteConnectProtocol

IPSC_KAITAI_VOICE_SLOTS = (
    IpSiteConnectProtocol.SlotTypes.slot_type_privacy_indicator,
    IpSiteConnectProtocol.SlotTypes.slot_type_voice_lc_header,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_a,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_b,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_c,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_d,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_e,
    IpSiteConnectProtocol.SlotTypes.slot_type_data_f,
)
