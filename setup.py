#!/usr/bin/env python3
import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ok-dmrlib",
    description="Parse, assemble and handle DMR protocols",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/OK-DMR/ok-dmrlib",
    author="Marek Sebera",
    author_email="marek.sebera@gmail.com",
    license="AGPL-3.0",
    version="0.1",
    packages=[
        "okdmr.dmrlib",
        "okdmr.dmrlib.coding",
    ],
    zip_safe=True,
    scripts=[],
    keywords="dmr etsi ham mmdvm homebrew radio hytera motorola",
    python_requires="~=3.9",
    install_requires=["dmr-kaitai>=0.6", "bitarray>=2.3.4"],
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
