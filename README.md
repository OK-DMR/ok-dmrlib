# OK-DMR Lib

[![.github/workflows/sanity.yml](https://img.shields.io/github/workflow/status/OK-DMR/ok-dmrlib/Sanity?style=flat-square)](https://github.com/OK-DMR/ok-dmrlib/actions)
[![Code Style: Python Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/OK-DMR/ok-dmrlib?style=flat-square)](https://github.com/OK-DMR/ok-dmrlib/blob/master/LICENSE)
[![Last released version](https://img.shields.io/pypi/v/ok-dmrlib?style=flat-square)](https://pypi.org/project/ok-dmrlib/)
[![PyPI downloads](https://img.shields.io/pypi/dd/ok-dmrlib?style=flat-square)](https://libraries.io/pypi/ok-dmrlib)
[![Python versions](https://img.shields.io/pypi/pyversions/ok-dmrlib?style=flat-square)](https://pypi.org/project/ok-dmrlib/)
[![Wheel](https://img.shields.io/pypi/wheel/ok-dmrlib?style=flat-square)](https://pypi.org/project/ok-dmrlib/#files)
[![Codecov](https://img.shields.io/codecov/c/github/ok-dmr/ok-dmrlib?style=flat-square)](https://app.codecov.io/gh/OK-DMR/ok-dmrlib)

This package provides way to parse and assemble various DMR ETSI protocols and functions, in pure Python implementation

## Supported features

### FEC (Forward Error Correction)

| Algorithm                                           | Encoding | Decoding / Verification |
|-----------------------------------------------------|:--------:|:-----------------------:|
| Hamming (7,4,3)                                     |    ✅     |            ✅            |
| Hamming (13,9,3)                                    |    ✅     |            ✅            |
| Hamming (15,11,3)                                   |    ✅     |            ✅            |
| Hamming (16,11,3)                                   |    ✅     |            ✅            |
| Hamming (17,12,3)                                   |    ✅     |            ✅            |
| Golay (20,8,7)                                      |    ✅     |            ✅            |
| Quadratic Residue (16,7,6)                          |    ✅     |            ✅            |
| Reed-Solomon (12,9,4)                               |    ✅     |            ✅            |
| Rate 3/4 Trellis                                    |    ✅     |            ✅            |
| Block Product Turbo Code (196,96)                   |    ✅     |            ✅            |
| Variable length BPTC (BPTC 128,72)                  |    ✅     |            ✅            |
| Variable length BPTC (BPTC 68,28) for CACH/Short LC |    ✅     |            ✅            |
| Variable length BTPC (BPTC 32,11) for Single-Burst  |    ✅     |            ✅            |

### CRC (Cyclic Redundancy Check) and Checksums

| Name                  | Generate | Verify |
|-----------------------|:--------:|:------:|
| 5-bit checksum        |    ✅     |   ✅    |
| CRC-8 (8-bit CRC)     |    ✅     |   ✅    |
| CRC-9                 |    ✅     |   ✅    |
| CRC-CCIT (CRC16-CCIT) |    ✅     |   ✅    |
| CRC-32 (32-bit CRC)   |    ✅     |   ✅    |

### ETSI PDUs (Protocol Data Units)

| Name          | Encoding / Decoding | Description                                                                                                                | 
|---------------|:-------------------:|----------------------------------------------------------------------------------------------------------------------------|
| CSBK          |          ✅          | Control Signalling Block, namely: BS Outbound Activation, Unit-Unit Request/Answer, Negative ACK, Preamble, Channel Timing |
| EMB           |          ✅          | Embedded Signalling                                                                                                        |
| FULL LC       |          ✅          | Full Link Control, namely: Group Voice, Unit-Unit, Talker Alias (header + blocks1,2,3), GPSInfo, Terminator with LC        |
| SHORT LC      |          ✅          | Short Link Control, namely: Activity, Null                                                                                 |
| SLOT          |          ✅          | Slot Type                                                                                                                  |
| SYNC          |          ✅          | Synchronization patterns                                                                                                   |
| Data Header   |          ✅          | Confirmed/Unconfirmed, Response, Defined Short Data                                                                        |
| PI Header     |          ✅          | Privacy (PI) Header, without further understanding of transported data                                                     |
| Rate 1/2 Data |          ✅          | Rate 1/2 data (confirmed and unconfirmed) and last block data (confirmed and unconfirmed)                                  |
| Rate 3/4 Data |          ✅          | Rate 3/4 data (confirmed and unconfirmed) and last block data (confirmed and unconfirmed)                                  |

### ETSI Information Elements

All listed elements are supported as standalone enum/class representation, which allows for decoding/encoding and
describing data (discovery):

Access Types (AT), CRC Mask, CSBKO (CSBK Opcode), DPF (Data Packet Format), DT (Data Type), FID (Feature Set ID), FLCO (
Full LC Opcode), LCSS (LC Start/Stop), PI (Pre-emption and power control indicator), SLCO (Short LC Opcode), SYNC (
Synchronization pattern), Activity ID, Additional Information Field, Answer/Response, CTO (Channel Timing Opcode), DI (
Dynamic Identifier), Position Error, Reason Code, Service Options, Talker Alias Data Format, Defined Data Format (DD), Selective Automatic Repeat reQuest (SARQ),
Re-Synchronize Flag (S), Send sequence number (N(S)), SAP identifier (SAP), Supplementary Flag (SF), Unified Data Transport Format (UDT Format)


### Additional notes

- Almost every class/enum supports BitsInterface (de-serialization from on-air bits, serialization to transmission bits)
- Every FEC/CRC implemented supports both calculation, verification and (if possible) also self-correction
- Working with Vocoder and Data/Control Bursts is supported, along with handling rates 1, 1/2 and 3/4
- CRCs interface classes may require appropriate CRC Mask to be provided when generating or verifying
- Through [dmr-kaitai](https://github.com/ok-dmr/dmr-kaitai) handling of ETSI, Hytera and MMDVM/Homebrew UDP data is supported 
- To inspect on-wire traffic PcapTool (provided in cli as `dmrlib-pcap-tool` script) supports PCAP/PCAPNG files with
  various functions on describing bursts, port/data filtering, data extraction, ...
- Everything is tested, specifically now we have 95% pytest coverage for whole ok-dmrlib codebase