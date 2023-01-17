from typing import Iterator, Literal, Tuple, List, Dict

import numpy
from bitarray import bitarray
from okdmr.dmrlib.utils.logging_trait import LoggingTrait
from scipy.signal import resample, convolve


class DSPTool(LoggingTrait):
    """
    Handles WAV input (mono, usually 48.000/1 or 96.000/1) and outputs
    TDMA Frames (TDMA Bursts for each timeslot, optionally CACH bursts or RC bursts)
    """

    SAMPLES_PER_SYMBOL_48K = 10
    DEFAULT_SAMPLE_RATE = 48000
    # fmt:off
    # @formatter:off
    RRCOS_FILTER = [
        +0.0273676736, +0.0190682959, +0.0070661879, -0.0075385898, -0.0231737159, -0.0379433607, -0.0498333862,
        -0.0569528373, -0.0577853377, -0.0514204905, -0.0377352004, -0.0174982391, +0.0076217868, +0.0351552125,
        +0.0620353691, +0.0848941519, +0.1004237235, +0.1057694293, +0.0989127431, +0.0790009892, +0.0465831968,
        +0.0037187043, -0.0460635022, -0.0979622825, -0.1462501260, -0.1847425896, -0.2073523972, -0.2086782295,
        -0.1845719273, -0.1326270847, -0.0525370892, +0.0537187153, +0.1818868577, +0.3256572849, +0.4770745929,
        +0.6271117870, +0.7663588857, +0.8857664963, +0.9773779594, +1.0349835419, +1.0546365475, +1.0349835419,
        +0.9773779594, +0.8857664963, +0.7663588857, +0.6271117870, +0.4770745929, +0.3256572849, +0.1818868577,
        +0.0537187153, -0.0525370892, -0.1326270847, -0.1845719273, -0.2086782295, -0.2073523972, -0.1847425896,
        -0.1462501260, -0.0979622825, -0.0460635022, +0.0037187043, +0.0465831968, +0.0790009892, +0.0989127431,
        +0.1057694293, +0.1004237235, +0.0848941519, +0.0620353691, +0.0351552125, +0.0076217868, -0.0174982391,
        -0.0377352004, -0.0514204905, -0.0577853377, -0.0569528373, -0.0498333862, -0.0379433607, -0.0231737159,
        -0.0075385898, +0.0070661879, +0.0190682959, +0.0273676736,
    ]
    """Square Raised Root Cosine Filter"""
    # fmt:on
    # @formatter:on
    DIGITIZED_TO_SYMBOL = {1: +3, 2: +1, 3: -1, 4: -3}
    """Table 10.3: Dibit symbol mapping to 4FSK deviation"""
    SYMBOLS: Dict[str, bitarray] = {
        "3": bitarray("01"),
        "1": bitarray("00"),
        "-1": bitarray("10"),
        "-3": bitarray("11"),
    }

    @staticmethod
    def get_scaled_samples_per_symbol(sample_rate: Literal[48000, 96000]) -> int:
        return (
            DSPTool.SAMPLES_PER_SYMBOL_48K
            if sample_rate == 48000
            else 2 * DSPTool.SAMPLES_PER_SYMBOL_48K
        )

    @staticmethod
    def get_best_phase_offset(
        wave: Iterator[int], sample_rate: Literal[48000, 96000] = DEFAULT_SAMPLE_RATE
    ) -> numpy.ndarray:
        samples_per_symbol: int = DSPTool.get_scaled_samples_per_symbol(
            sample_rate=sample_rate
        )
        return numpy.argmax(
            [
                numpy.std(wave[offset::samples_per_symbol])
                for offset in range(0, samples_per_symbol)
            ]
        )

    @staticmethod
    def filtered_list_to_symbols(
        wave: Iterator[int], sample_rate: Literal[48000, 96000]
    ):
        samples_per_symbol = DSPTool.get_scaled_samples_per_symbol(
            sample_rate=sample_rate
        )
        offset = DSPTool.get_best_phase_offset(wave=wave, sample_rate=sample_rate)
        sampled = wave[offset::samples_per_symbol]

        # Generate bins to sort samples
        middle = (numpy.quantile(sampled, 0.05) + numpy.quantile(sampled, 0.95)) / 2
        bins = [
            numpy.min(sampled) - 1,
            (numpy.min(sampled) + middle) / 2,
            middle,
            (numpy.max(sampled) + middle) / 2,
            numpy.max(sampled) + 1,
        ]

        return DSPTool.digitize(sampled, bins)

    @staticmethod
    def audio_stream_to_symbols(
        wave: Iterator[int], sample_rate: Literal[48000, 96000]
    ) -> Iterator[int]:
        resampled = resample(
            wave, int((DSPTool.DEFAULT_SAMPLE_RATE / sample_rate) * len(wave))
        )
        filtered = convolve(resampled, DSPTool.RRCOS_FILTER, mode="same")

        for _x in numpy.array_split(
            filtered, len(filtered) // DSPTool.DEFAULT_SAMPLE_RATE
        ):
            for symbol in DSPTool.filtered_list_to_symbols(
                wave=_x, sample_rate=sample_rate
            ):
                yield symbol["symbol"]

    @staticmethod
    def symbols_to_bits(symbols: List[str]) -> bitarray:
        keys = DSPTool.SYMBOLS.keys()
        for symbol in symbols:
            if symbol in keys:
                yield DSPTool.SYMBOLS.get(symbol)

    @staticmethod
    def audio_stream_to_bits(
        wave: Iterator[int], sample_rate: Literal[48000, 96000]
    ) -> Tuple[int, int]:
        for x in DSPTool.audio_stream_to_symbols(wave=wave, sample_rate=sample_rate):
            # Table 10.3: Dibit symbol mapping to 4FSK deviation
            bit0, bit1 = {3: (0, 1), 1: (0, 0), -1: (1, 0), -3: (1, 1)}.get(x)
            yield bit0, bit1

    @staticmethod
    def digitize(arr, bins):
        """Digitize an array of samples: turn them into symbols. But also add the certainity (how close it is to the middle of the bin). This helps to evaluate signal quality"""
        middles = [x + ((y - x) / 2) for (x, y) in zip(bins, bins[1:])]
        half_bin_width = (bins[1] - bins[0]) / 2

        # Bin the samples and convert them to a bitstream

        # numpy.digitize will assign the number of the bin
        # This map maps bin numbers to dibits
        # See ETSI TS 102 361-1 Table 10.3

        return numpy.array(
            [
                {
                    "symbol": DSPTool.DIGITIZED_TO_SYMBOL[_bin],
                    "certainity": 1
                    - (abs(middles[_bin - 1] - element) / half_bin_width),
                }
                for (_bin, element) in zip(numpy.digitize(arr, bins, right=True), arr)
            ]
        )
