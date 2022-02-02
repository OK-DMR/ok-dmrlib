import enum


@enum.unique
class SyncTypes(enum.Enum):
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - 9.1.1 Synchronization (SYNC) PDU - Table 9.2: SYNC patterns
    """

    BsSourcedVoice = 0x755FD7DF75F7
    BsSourcedData = 0xDFF57D75DF5D
    MsSourcedVoice = 0x7F7D5DD57DFD
    MsSourcedData = 0xD5D7F77FD757
    MsSourcedRcSync = 0x77D55F7DFD77
    Tdma1Voice = 0x5D577F7757FF
    Tdma1Data = 0xF7FDD5DDFD55
    Tdma2Voice = 0x7DFFD5F55D5F
    Tdma2Data = 0xD7557F5FF7F5
    Reserved = 0xDD7FF5D757DD
    EmbeddedData = -1

    @classmethod
    def _missing_(cls, value: object):
        return SyncTypes.EmbeddedData
