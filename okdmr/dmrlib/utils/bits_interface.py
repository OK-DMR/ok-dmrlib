from bitarray import bitarray


class BitsInterface:
    @staticmethod
    def from_bits(bits: bitarray) -> "BitsInterface":
        """
        Deserialize from bitarray, while validating input
        :param bits:
        :return:
        """
        pass

    def as_bits(self) -> bitarray:
        """
        Serialize into bitarray
        :return:
        """
        pass
