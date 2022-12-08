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
    version="0.7",
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
        "okdmr.dmrlib.motorola",
        "okdmr.dmrlib.hytera",
        "okdmr.dmrlib.hytera.pdu",
    ],
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "dmrlib-pcap-tool=okdmr.dmrlib.tools.pcap_tool:PcapTool.main",
            "dmrlib-hytera-hstrp=okdmr.dmrlib.tools.hytera_tool:HyteraTool.hstrp",
            "dmrlib-hytera-hdap=okdmr.dmrlib.tools.hytera_tool:HyteraTool.hdap",
            "dmrlib-hytera-hrnp=okdmr.dmrlib.tools.hytera_tool:HyteraTool.hrnp",
            "dmrlib-hytera-lp=okdmr.dmrlib.tools.hytera_tool:HyteraTool.lp",
            "dmrlib-hytera-rcp=okdmr.dmrlib.tools.hytera_tool:HyteraTool.rcp",
            "dmrlib-hytera-rrs=okdmr.dmrlib.tools.hytera_tool:HyteraTool.rrs",
            "dmrlib-hytera-tmp=okdmr.dmrlib.tools.hytera_tool:HyteraTool.tmp",
            "dmrlib-dmr-burst=okdmr.dmrlib.tools.dmrlib_tool:DmrlibTool.burst",
        ],
    },
    keywords="dmr etsi ham mmdvm homebrew radio hytera motorola",
    python_requires=">=3.8",
    install_requires=[
        "dmr-kaitai>=1.0",
        "bitarray>=2.6.0",
        "numpy>=1.23.4",
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
        "Programming Language :: Python :: 3.8",
    ],
)
