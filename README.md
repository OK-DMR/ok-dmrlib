# OK-DMR Lib

![.github/workflows/sanity.yml](https://img.shields.io/github/workflow/status/OK-DMR/ok-dmrlib/Sanity?style=flat-square)
![Code Style: Python Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)
![License](https://img.shields.io/github/license/OK-DMR/ok-dmrlib?style=flat-square)
![Last released version](https://img.shields.io/pypi/v/ok-dmrlib?style=flat-square)
![PyPI downloads](https://img.shields.io/pypi/v/ok-dmrlib?style=flat-square)

This package provides way to parse and assemble various DMR ETSI protocols and functions, in pure Python implementation

## Supported features

### FEC (Forward Error Correction)

| Algorithm                  | Encoding | Decoding / Verification |
|----------------------------|:--------:|:-----------------------:|
| Hamming (7,4,3)            |    ✅     |            ✅            |
| Hamming (13,9,3)           |    ✅     |            ✅            |
| Hamming (15,11,3)          |    ✅     |            ✅            |
| Hamming (16,11,3)          |    ✅     |            ✅            |
| Hamming (17,12,3)          |    ✅     |            ✅            |
| Golay (20,8,7)             |    ✅     |            ✅            |
| Quadratic Residue (16,7,6) |    ✅     |            ✅            |
| Reed-Solomon (12,9,4)      |    ✅     |            ✅            |

### Coding

| Coding                            |  Encoding  |  Decoding  |
|-----------------------------------|:----------:|:----------:|
| Rate 3/4 Trellis                  |     ✅      |     ✅      |
| Block Product Turbo Code (196,96) |     ✅      |     ✅      |

### CRC (Cyclic Redundancy Check) and Checksums

| Name                  | Generate | Verify |
|-----------------------|:--------:|:------:|
| 5-bit checksum        |    ✅     |   ✅    |
| CRC-9                 |    ✅     |   ✅    |
| CRC-CCIT (CRC16-CCIT) |    ✅     |   ✅    |
| CRC-32 (32-bit CRC)   |    ✅     |   ✅    |