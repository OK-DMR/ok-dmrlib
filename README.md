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

| Name                    | Encoding / Decoding | Description                                                                                                                | 
|-------------------------|:-------------------:|----------------------------------------------------------------------------------------------------------------------------|
| CSBK                    |          ✅          | Control Signalling Block, namely: BS Outbound Activation, Unit-Unit Request/Answer, Negative ACK, Preamble, Channel Timing |
| EMB                     |          ✅          | Embedded Signalling                                                                                                        |
| FULL&nbsp;LC            |          ✅          | Full Link Control, namely: Group Voice, Unit-Unit, Talker Alias (header + blocks1,2,3), GPSInfo, Terminator with LC        |
| SHORT&nbsp;LC           |          ✅          | Short Link Control, namely: Activity, Null                                                                                 |
| SLOT                    |          ✅          | Slot Type                                                                                                                  |
| SYNC                    |          ✅          | Synchronization patterns                                                                                                   |
| Data&nbsp;Header        |          ✅          | Confirmed/Unconfirmed, Response, Defined Short Data                                                                        |
| PI&nbsp;Header          |          ✅          | Privacy (PI) Header, without further understanding of transported data                                                     |
| Rate&nbsp;1&nbsp;Data   |          ✅          | Rate 1 data (confirmed and unconfirmed) and last block data (confirmed and unconfirmed)                                    |
| Rate&nbsp;1/2&nbsp;Data |          ✅          | Rate 1/2 data (confirmed and unconfirmed) and last block data (confirmed and unconfirmed)                                  |
| Rate&nbsp;3/4&nbsp;Data |          ✅          | Rate 3/4 data (confirmed and unconfirmed) and last block data (confirmed and unconfirmed)                                  |
| Full/Short Link Control |          ✅          | FLC/SLC PDUs                                                                                                               |
| UDP/IPv4                |          ✅          | UDP/IPv4 compressed header/packet                                                                                          |

### ETSI Information Elements

All listed elements are supported as standalone enum/class representation, which allows for decoding/encoding and
describing data (discovery):

Access Types (AT), CRC Mask, CSBKO (CSBK Opcode), DPF (Data Packet Format), DT (Data Type), FID (Feature Set ID), FLCO (
Full LC Opcode), LCSS (LC Start/Stop), PI (Pre-emption and power control indicator), SLCO (Short LC Opcode), SYNC (
Synchronization pattern), Activity ID, Additional Information Field, Answer/Response, CTO (Channel Timing Opcode), DI (
Dynamic Identifier), Position Error, Reason Code, Service Options, Talker Alias Data Format, Defined Data Format (DD),
Selective Automatic Repeat reQuest (SARQ),
Re-Synchronize Flag (S), Send sequence number (N(S)), SAP identifier (SAP), Supplementary Flag (SF), Unified Data
Transport Format (UDT Format), UDP Port Identifier (SPID/DPID), IP Address Identifier (SAID/DAID)

### Hytera

| Protocol Name                                        | Encoding / Decoding | 
|------------------------------------------------------|:-------------------:|
| Hytera Simple Transport Reliability Protocol (HSTRP) |          ✅          |
| Hytera Radio Network Protocol (HRNP)                 |          ✅          |
| Hytera DMR Application Protocol (HDAP)               |          ✅          |
| Radio Registration Service (RRS)                     |          ✅          |
| Location Protocol (LP)                               |          ✅          |
| Radio Control Protocol (RCP)                         |          ✅          |
| Text Message Protocol (TMP)                          |          ✅          |

- Not all opcodes in all protocols are implemented, however it will fail with descriptive message, which opcode is
  missing in particular operation (decoding, description, encoding)

### Motorola

| Protocol Name                             | Encoding / Decoding | 
|-------------------------------------------|:-------------------:|
| Location Request Response Protocol (LRRP) |          ✅          |
| Automatic Registration Service (ARS)      |          ✅          |
| Text Messaging Service (TMS)              |          ✅          |

- Motorola has MBXML (Motorola Binary XML) which is used to represent LRRP/ARRP documents, ok-dmrlib contains abstract
  MBXML implementation with various tools, LRRP implementation tested with both examples and real-world data
- LRRP is supported as `[bytes] <-> [mbxml document(s)] -> [xml representation]`, currently serialization of xml
  document to bytes is not supported
- There are some catches, when you want to serialize MBXML token with common name, look through the test_mbxml and
  test_lrrp modules, to see how to select specific (correct) token programatically

### Additional notes

- Almost every class/enum supports BitsInterface (de-serialization from on-air bits, serialization to transmission bits)
  , or for byte-aligned protocols (Hytera, Motorola) BytesInterface (with explicit endianness support)
- Every FEC/CRC implemented supports both calculation, verification and (if possible) also self-correction
- Working with Vocoder and Data/Control Bursts is supported, along with handling rates 1, 1/2 and 3/4
- CRCs interface classes may require appropriate CRC Mask to be provided when generating or verifying
- Through [dmr-kaitai](https://github.com/ok-dmr/dmr-kaitai) handling of ETSI, Hytera and MMDVM/Homebrew UDP data is
  supported
- To inspect on-wire traffic PcapTool (provided in cli as `dmrlib-pcap-tool` script) supports PCAP/PCAPNG files with
  various functions on describing bursts, port/data filtering, data extraction, ...
- Everything is tested, specifically now we have 95% pytest coverage for whole ok-dmrlib codebase
- Not everything is probably documented as it should be, but the usage should always be very clear, when you look at
  tests of particular component