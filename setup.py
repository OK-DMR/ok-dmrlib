#!/usr/bin/env python3
import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ok-dmrlib",
    description="Parse, assemble and handle DMR data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/OK-DMR/ok-dmrlib",
    author="Marek Sebera",
    author_email="marek.sebera@gmail.com",
    license="AGPL-3.0",
    version="0.5",
    packages=[
        "okdmr.dmrlib",
        "okdmr.dmrlib.transmission",
        "okdmr.dmrlib.utils",
        "okdmr.dmrlib.tools",
        "okdmr.dmrlib.etsi",
        "okdmr.dmrlib.etsi.crc",
        "okdmr.dmrlib.etsi.fec",
        "okdmr.dmrlib.etsi.layer2",
        "okdmr.dmrlib.etsi.layer2.elements",
        "okdmr.dmrlib.etsi.layer2.pdu",
        "okdmr.dmrlib.etsi.layer3",
        "okdmr.dmrlib.etsi.layer3.elements",
        "okdmr.dmrlib.etsi.layer3.pdu",
    ],
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "dmrlib-pcap-tool=okdmr.dmrlib.tools.pcap_tool:PcapTool.main"
        ],
    },
    keywords="dmr etsi ham mmdvm homebrew radio hytera motorola",
    python_requires="~=3.7",
    install_requires=[
        "dmr-kaitai>=0.7",
        "bitarray>=2.4.0",
        "numpy>=1.21.4",
        "scapy>=2.4.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Environment :: Console",
        "Topic :: Communications :: Ham Radio",
        "Operating System :: POSIX :: Linux",
        "Typing :: Typed",
        "Framework :: Pytest",
        "Intended Audience :: Telecommunications Industry",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
)
