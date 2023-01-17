import pytest
from bitarray import bitarray
from scipy.io import wavfile

from okdmr.dmrlib.tools.dsp_tool import DSPTool


@pytest.mark.skip
def test_with_file():
    file = "/home/smarek/Downloads/1R.wav"
    input_sample_rate, wavdata = wavfile.read(file)
    assert input_sample_rate in (48000, 96000), f"Unexpected sample rate"
    print(f"input_sample_rate:{input_sample_rate} data len {len(wavdata)}")
    bits: bitarray = bitarray()
    for bit0, bit1 in DSPTool.audio_stream_to_bits(
        wave=wavdata, sample_rate=input_sample_rate
    ):
        bits.extend([bit0, bit1])

    print(f"bits len: {len(bits)}")
    bytes_str: str = bits.tobytes().hex().upper()
    print(f"DFF57D {bytes_str.count('DFF57D')}")
    print(f"755FD7 {bytes_str.count('755FD7')}")
    print(f"FD5FD7 {bytes_str.count('FD5FD7')}")
    print(f"57F57D {bytes_str.count('57F57D')}")
    print(f"F7FD   {bytes_str.count('F7FD')}")
    print(f"7DFF   {bytes_str.count('7DFF')}")
    print(bytes_str[:500])


@pytest.mark.skip()
def test_symbols():
    symbols = "313333111331131131331131"
    bits: bitarray = bitarray()
    for _bits in DSPTool.symbols_to_bits(list(symbols)):
        bits += _bits
    print(bits.tobytes().hex().upper())
