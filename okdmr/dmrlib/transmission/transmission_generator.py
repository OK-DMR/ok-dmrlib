from math import ceil
from typing import List, Union, Type, Tuple

from okdmr.dmrlib.etsi.crc.crc32 import CRC32
from okdmr.dmrlib.etsi.layer2.burst import Burst
from okdmr.dmrlib.etsi.layer2.elements.burst_types import BurstTypes
from okdmr.dmrlib.etsi.layer2.elements.csbk_opcodes import CsbkOpcodes
from okdmr.dmrlib.etsi.layer2.elements.data_types import DataTypes
from okdmr.dmrlib.etsi.layer2.elements.sync_patterns import SyncPatterns
from okdmr.dmrlib.etsi.layer2.pdu.csbk import CSBK
from okdmr.dmrlib.etsi.layer2.pdu.data_header import DataHeader
from okdmr.dmrlib.etsi.layer2.pdu.rate12_data import Rate12Data, Rate12DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate1_data import Rate1Data, Rate1DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.rate34_data import Rate34Data, Rate34DataTypes
from okdmr.dmrlib.etsi.layer2.pdu.slot_type import SlotType
from okdmr.dmrlib.utils.bytes_interface import BytesInterface


class TransmissionGenerator:
    """
    Utility class to generate data transmissions with given payload and encoding
    """

    @staticmethod
    def generate_csbk_preambles(
        source_address: int,
        target_address: int,
        target_address_is_individual: bool = True,
        num_of_preambles: int = 1,
        num_of_following_data_blocks: int = 1,
        colour_code: int = 1,
        sync_pattern: SyncPatterns = SyncPatterns.BsSourcedData,
    ) -> List[Burst]:
        bursts: List[Burst] = []
        slot_type: SlotType = SlotType(
            colour_code=colour_code, data_type=DataTypes.CSBK
        )
        final_count: int = num_of_preambles + num_of_following_data_blocks
        for i in reversed(range(num_of_following_data_blocks, final_count)):
            csbk_i = CSBK(
                source_address=source_address,
                target_address=target_address,
                blocks_to_follow=i,
                csbko=CsbkOpcodes.PreambleCSBK,
                target_address_is_individual=target_address_is_individual,
                # last_block True means CSBK or MBC Last Block
                last_block=True,
            )
            b_i = Burst(
                burst_type=BurstTypes.DataAndControl,
            )
            b_i.has_emb = False
            b_i.sync_or_embedded_signalling = sync_pattern
            b_i.slot_type = slot_type
            b_i.data = csbk_i
            bursts.append(b_i)

        return bursts

    @staticmethod
    def generate_full_data_transmission(
        packet_type: Union[Type[Rate1Data], Type[Rate12Data], Type[Rate34Data]],
        userdata: Union[bytes, BytesInterface],
        data_header: DataHeader,
        csbk_count: int = 3,
        colour_code: int = 1,
    ) -> List[Burst]:
        bursts: List[Burst] = []
        userdata: bytes = (
            userdata if isinstance(userdata, bytes) else userdata.as_bytes()
        )

        # (1) generate rate(1/2/3/4) data bursts
        data_bursts, pad_octet_count = TransmissionGenerator.generate_data_bursts(
            packet_type=packet_type,
            userdata=userdata,
            colour_code=colour_code,
            is_confirmed=data_header.is_response_requested,
        )
        # (2) generate header burst with appropriate pad_octet_count+blocks_to_follow
        assert (
            data_header.pad_octet_count == pad_octet_count
        ), f"POC expected {data_header.pad_octet_count} generated {pad_octet_count}"
        header_burst: Burst = TransmissionGenerator.generate_data_header_burst(
            data_header=data_header
        )
        # (3) generate csbk bursts
        csbks: List[Burst] = TransmissionGenerator.generate_csbk_preambles(
            source_address=data_header.llid_source,
            target_address=data_header.llid_destination,
            colour_code=colour_code,
            num_of_preambles=csbk_count,
            num_of_following_data_blocks=len(data_bursts) + 1,
        )

        # in correct order, first CSBKs
        bursts += csbks
        # data header
        bursts += [header_burst]
        # dmr data
        bursts += data_bursts

        return bursts

    @staticmethod
    def generate_data_bursts(
        packet_type: Union[Type[Rate1Data], Type[Rate12Data], Type[Rate34Data]],
        userdata: bytes,
        colour_code: int = 1,
        is_confirmed: bool = True,
    ) -> Tuple[List[Burst], int]:
        """

        @param packet_type:
        @param userdata:
        @param colour_code:
        @param is_confirmed:
        @return: (Bursts with data, Number of padding octets for data header)
        """
        bursts: List[Burst] = []

        # ETSI TS 102 361-1 V2.5.1 (2017-10)
        # -> Section 8.2.0 Datagram fragmentation and re-assembly
        # -> Table 8.1: Octets per data block
        octets_per_block, octets_per_last_block = {
            (Rate1Data, True): (22, 18),
            (Rate1Data, False): (24, 20),
            (Rate12Data, True): (10, 6),
            (Rate12Data, False): (12, 8),
            (Rate34Data, True): (16, 12),
            (Rate34Data, False): (18, 14),
        }.get((packet_type, is_confirmed))

        # helpers for this generic method
        slice_type, last_slice_type = {
            (Rate1Data, True): (
                Rate1DataTypes.Confirmed,
                Rate1DataTypes.ConfirmedLastBlock,
            ),
            (Rate1Data, False): (
                Rate1DataTypes.Unconfirmed,
                Rate1DataTypes.UnconfirmedLastBlock,
            ),
            (Rate12Data, True): (
                Rate12DataTypes.Confirmed,
                Rate12DataTypes.ConfirmedLastBlock,
            ),
            (Rate12Data, False): (
                Rate12DataTypes.Unconfirmed,
                Rate12DataTypes.UnconfirmedLastBlock,
            ),
            (Rate34Data, True): (
                Rate34DataTypes.Confirmed,
                Rate34DataTypes.ConfirmedLastBlock,
            ),
            (Rate34Data, False): (
                Rate34DataTypes.Unconfirmed,
                Rate34DataTypes.UnconfirmedLastBlock,
            ),
        }.get((packet_type, is_confirmed))

        # ETSI TS 102 361-1 V2.5.1 (2017-10)
        # -> Section 8.2.0 Datagram fragmentation and re-assembly
        # -> calculation of N_BlockMax
        num_bursts: int = ceil(
            1 + ((len(userdata) - octets_per_last_block) / octets_per_block)
        )
        data_octets: int = (num_bursts - 1) * octets_per_block + octets_per_last_block
        pad_octet_count: int = data_octets - len(userdata)
        # add padding
        userdata = userdata + (b"\x00" * pad_octet_count)
        userdata_crc32: bytes = CRC32.calculate(data=userdata).to_bytes(
            length=4, byteorder="little"
        )

        for i in range(0, num_bursts):
            userdata_slice: bytes = userdata[
                i * octets_per_block : i * octets_per_block + octets_per_block
            ]
            block_type = last_slice_type if i == (num_bursts - 1) else slice_type
            block = packet_type(
                packet_type=block_type, data=userdata_slice, crc32=userdata_crc32
            )
            # TODO better burst from contained data init
            burst = Burst(burst_type=BurstTypes.DataAndControl)
            burst.has_emb = False
            burst.data = block
            burst.slot_type = SlotType(
                colour_code=colour_code, data_type=packet_type.get_data_type()
            )
            burst.sync_or_embedded_signalling = SyncPatterns.BsSourcedData
            bursts.append(burst)

        return bursts, pad_octet_count

    @staticmethod
    def generate_data_header_burst(data_header: DataHeader) -> Burst:
        burst: Burst = Burst(burst_type=BurstTypes.DataAndControl)
        burst.data = data_header
        burst.sync_or_embedded_signalling = SyncPatterns.BsSourcedData
        burst.slot_type = SlotType(colour_code=5, data_type=DataTypes.DataHeader)
        burst.has_emb = False
        return burst
