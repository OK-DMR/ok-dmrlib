from bitarray import bitarray
from bitarray.util import int2ba
from crc import CrcCalculator, Configuration

from okdmr.dmrlib.utils.bits_bytes import bytes_to_bits


class CRC9:
    CALC: CrcCalculator = CrcCalculator(
        configuration=Configuration(
            width=9,
            polynomial=0x59,  # without msb bit
            init_value=0x00,
            reverse_input=False,
            reverse_output=True,
            final_xor_value=0x00,
        ),
        table_based=True,
    )

    @staticmethod
    def check(
        data: bytes,
        serial_number: int,
        crc9: int,
        crc32: bytes = None,
        mask: int = 0x00,
    ) -> bool:
        source_data: bitarray = bytes_to_bits(data, endian="little")
        if crc32 is not None:
            assert len(crc32) == 4, "32-bit CRC must be exactly 4-bytes long"
            source_data += bytes_to_bits(crc32, endian="big")
        else:
            dbsnba = int2ba(serial_number, length=7, endian="little", signed=False)
            # dbsnba.reverse()
            source_data += dbsnba

        # source_data.reverse()

        for sde in ("little", "big"):
            for polynom in (0x59,):
                for rev_in in (True, False):
                    for rev_out in (True, False):
                        for xor_val in (0x00,):

                            bfdata: bitarray = bytes_to_bits(data, endian=sde)
                            bfdata += int2ba(serial_number, length=7, endian=sde)

                            _calc = CrcCalculator(
                                configuration=Configuration(
                                    width=9,
                                    polynomial=polynom,
                                    init_value=0x00,
                                    reverse_input=rev_in,
                                    reverse_output=rev_out,
                                    final_xor_value=xor_val,
                                ),
                                table_based=True,
                            )

                            if _calc.verify_checksum(
                                data=bfdata.tobytes(), expected_checksum=crc9 ^ mask
                            ):
                                print(
                                    polynom,
                                    "rev_in",
                                    rev_in,
                                    "rev_out",
                                    rev_out,
                                    xor_val,
                                )
                                print("FOUND A sn %d" % serial_number)
                                # return True

                            if _calc.verify_checksum(
                                data=bfdata.tobytes(), expected_checksum=crc9
                            ):
                                print(
                                    polynom,
                                    "rev_in",
                                    rev_in,
                                    "rev_out",
                                    rev_out,
                                    xor_val,
                                )
                                print("FOUND B sn %d" % serial_number)
                                # return True

        return _calc.verify_checksum(data=source_data, expected_checksum=crc9)

    @staticmethod
    def calculate(data: bitarray) -> int:
        return CRC9.CALC.calculate_checksum(data=data.tobytes())
