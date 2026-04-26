#!/usr/bin/env python3
"""
Setup script for Antivírus Projeto.

Enables pip installation: pip install -e .
Enables distribution: python setup.py sdist bdist_wheel
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="antivirus-projeto",
    version="1.0.0",
    author="Nekas1980",
    author_email="",
    description="Educational antivirus scanning engine demonstrating cybersecurity basics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nekas1980/anti-virus-projeto",
    project_urls={
        "Bug Tracker": "https://github.com/Nekas1980/anti-virus-projeto/issues",
        "Source": "https://github.com/Nekas1980/anti-virus-projeto",
    },
    py_modules=["Virus_project", "report_generator", "scheduler", "virustotal_updater", "gui"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.9",
    install_requires=[
        "colorama>=0.4.4",
        "requests>=2.28.0",
    ],
    extras_require={
        "gui": ["customtkinter>=5.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "antivirus-scan=Virus_project:main",
            "antivirus-scheduler=scheduler:main",
            "antivirus-update=virustotal_updater:main",
        ],
    },
    include_package_data=True,
    keywords="antivirus malware security education cybersecurity",
    license="MIT",
)
