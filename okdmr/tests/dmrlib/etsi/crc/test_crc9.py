from typing import Tuple, List, Union

from bitarray.util import int2ba

from okdmr.dmrlib.etsi.crc.crc import BitCrcCalculator, Crc9
from okdmr.dmrlib.etsi.crc.crc9 import CRC9
from okdmr.dmrlib.etsi.layer2.elements.crc_masks import CrcMasks


def test_crc9():
    # fmt:off
    # data, serial number, expected crc9, appropriate mask
    data: List[Tuple[str, int, int, CrcMasks, Union[None, str]]] = [
        # 3/4 blocks confirmed (single continuous transmission from hytera ms)
        ("47004d00500054002e004a0047004100", 17, 459, CrcMasks.Rate34DataContinuation, None,),
        ("2e00570047005400500044002e004a00", 16, 138, CrcMasks.Rate34DataContinuation, None,),
        ("4a0047005400470050004d0047004a00", 15, 46, CrcMasks.Rate34DataContinuation, None,),
        ("41004a00470044002e004a0041002e00", 14, 63, CrcMasks.Rate34DataContinuation, None,),
        ("4a002e00540047004d00500057005400", 13, 427, CrcMasks.Rate34DataContinuation, None,),
        ("4a002e004d0041005700470044005000", 12, 174, CrcMasks.Rate34DataContinuation, None,),
        ("41004700540050005700470044005400", 11, 60, CrcMasks.Rate34DataContinuation, None,),
        ("2e004a004700570054004d0044002e00", 10, 193, CrcMasks.Rate34DataContinuation, None,),
        ("4a00570041004d004700440050005400", 9, 171, CrcMasks.Rate34DataContinuation, None,),
        ("47004a002e00410047004a0050005400", 8, 199, CrcMasks.Rate34DataContinuation, None,),
        ("540044004a00570041004d0050005400", 7, 251, CrcMasks.Rate34DataContinuation, None,),
        ("50004a002e00540047004a0050004100", 6, 448, CrcMasks.Rate34DataContinuation, None,),
        ("54004400410057004a004d0047005400", 5, 363, CrcMasks.Rate34DataContinuation, None,),
        ("470041002e00540047004a0050004d00", 4, 198, CrcMasks.Rate34DataContinuation, None,),
        ("470041002e005400470054002e004a00", 3, 375, CrcMasks.Rate34DataContinuation, None,),
        ("4100470054002e00410047002e005400", 2, 2, CrcMasks.Rate34DataContinuation, None,),
        ("4a00470044002e00540047004a002e00", 1, 65, CrcMasks.Rate34DataContinuation, None,),
        ("0100000101004d004d00470054002e00", 0, 409, CrcMasks.Rate34DataContinuation, None,),
        # 3/4 last data blocks
        # bcd sms
        ("0001410048004f004a000000", 0, 447, CrcMasks.Rate34DataContinuation, "a197ccb4"),
        # anytone hytera-format long sms
        ("000000000000000000000000", 2, 312, CrcMasks.Rate34DataContinuation, "f486aed8")
    ]
    # fmt:on

    for (databytes, serialno, expected_crc9, mask, crc32) in data:
        assert CRC9.check(
            data=bytes.fromhex(databytes),
            serial_number=serialno,
            crc9=expected_crc9,
            crc32=bytes.fromhex(crc32) if crc32 else None,
        ), f"CRC9 does not match in {(databytes, serialno, expected_crc9, mask, crc32)}"


def test_crc9_table():
    no_table: BitCrcCalculator = BitCrcCalculator(
        table_based=False, configuration=Crc9.ETSI_DMR
    )
    with_table: BitCrcCalculator = BitCrcCalculator(
        table_based=True, configuration=Crc9.ETSI_DMR
    )
    for idx in range(1 << 9, 1 << 10):
        test_data = int2ba(idx, length=10)
        assert no_table.calculate_checksum(test_data) == with_table.calculate_checksum(
            test_data
        )
