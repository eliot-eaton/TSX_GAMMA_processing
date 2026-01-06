"""
Setup script for TSX Supersite GAMMA Processing
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="tsx-supersite-gamma-processing",
    version="0.1.0",
    author="TSX Supersite Team",
    description="Tools for downloading TerraSAR-X data and processing with GAMMA InSAR software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eliot-eaton/TSX_supersite_GAMMA_processing",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'tsx-download=download.tsx_downloader:main',
            'tsx-process=gamma_processing.insar_processor:main',
            'tsx-prepare-licsbar=licsbar_prep.prepare_licsbar:main',
        ],
    },
    include_package_data=True,
)
