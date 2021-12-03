class FiveBitChecksum:
    """
    ETSI TS 102 361-1 V2.5.1 (2017-10) - B.3.11 5-bit Checksum (CS) calculation
    """

    @staticmethod
    def calculate(data: bytes) -> int:
        """
        Takes 9 bytes of input and returns checksum
        :param data:
        :return: checksum value (number in inclusive range 0-30)
        """
        # adding null-bytes will not change the CRC output
        if len(data) < 9:
            data = (b"\x00" * (9 - len(data))) + data

        # leave the check in-place for payloads bigger than 9 bytes
        assert (
            len(data) == 9
        ), f"FiveBitChecksum generate expects 9 bytes of data, got {len(data)}"

        return (sum([data[i] for i in reversed(range(0, 9))]) & 0xFFFF) % 31

    @staticmethod
    def verify(data: bytes, checksum: int) -> bool:
        """
        Verifies the checksum (provided as separate argument) matches the data
        :param data:
        :param checksum:
        :return:
        """
        assert (
            0 <= checksum < 31
        ), "FiveBitChecksum checksum value must be in range 0-30 (inclusive)"
        return FiveBitChecksum.calculate(data) == checksum
