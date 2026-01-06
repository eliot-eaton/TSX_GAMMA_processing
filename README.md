# TSX Supersite GAMMA Processing

A repository for downloading TerraSAR-X data from the EOC Geoservice, processing interferograms using GAMMA InSAR software, and preparing data for COMET-LiCSAR LiCSBAS time-series processing.

## Overview

This repository provides tools for:
1. **Downloading** TerraSAR-X satellite data from EOC (Earth Observation Center) Geoservice
2. **Processing** InSAR interferograms using GAMMA software
3. **Preparing** data for LiCSBAS time-series analysis

## Prerequisites

### Required Software

- **Python 3.7+** with pip
- **GAMMA Software** (commercial license required)
  - This software is **not open source** and requires a commercial license
  - See: https://www.gamma-rs.ch/
  - Set `GAMMA_HOME` environment variable to your GAMMA installation directory

### Python Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```

### EOC Geoservice Access

- Register for an account at the EOC Geoservice
- Obtain credentials for TerraSAR-X data access
- Configure credentials in `config/download_config.yaml`

## Repository Structure

```
TSX_supersite_GAMMA_processing/
├── src/
│   ├── download/           # TerraSAR-X data download scripts
│   ├── gamma_processing/   # GAMMA InSAR processing scripts
│   ├── licsbar_prep/      # LiCSBAS preparation scripts
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── examples/              # Example configuration files
├── data/                  # Data directories (created during processing)
│   ├── raw/              # Downloaded TerraSAR-X data
│   ├── processed/        # GAMMA processed products
│   └── output/           # Final outputs for LiCSBAS
└── README.md
```

## Usage

### 1. Download TerraSAR-X Data

Download data from EOC Geoservice for a specific area and time range:

```bash
# Using command line arguments
python src/download/tsx_downloader.py \
  --bbox 10.0 45.0 11.0 46.0 \
  --start 2020-01-01 \
  --end 2020-12-31 \
  --username YOUR_USERNAME \
  --password YOUR_PASSWORD \
  --output-dir data/raw

# Or using a configuration file
python src/download/tsx_downloader.py --config config/download_config.yaml
```

**Configuration**: Edit `config/download_config.yaml` with your:
- EOC credentials
- Area of interest (bounding box)
- Time range
- Product type (SSC, MGD, GEC, or EEC)

### 2. Process with GAMMA InSAR

Process interferometric pairs using GAMMA software:

```bash
# Set GAMMA_HOME environment variable
export GAMMA_HOME=/path/to/gamma

# Process an interferometric pair
python src/gamma_processing/insar_processor.py \
  --master data/raw/master_scene.tar.gz \
  --slave data/raw/slave_scene.tar.gz \
  --dem data/dem/dem.tif \
  --output pair_20200101_20200113 \
  --work-dir data/processed
```

**Configuration**: Edit `config/processing_config.yaml` to customize:
- Processing parameters
- Filtering options
- Unwrapping method
- Geocoding settings

**Note**: GAMMA software must be properly installed and licensed.

### 3. Prepare for LiCSBAS Time-Series Processing

Convert GAMMA products to LiCSBAS format:

```bash
# Prepare interferograms for LiCSBAS
python src/licsbar_prep/prepare_licsbar.py \
  --input data/processed \
  --output data/output/licsbar \
  --pairs examples/example_pairs.json

# Create LiCSBAS configuration template
python src/licsbar_prep/prepare_licsbar.py \
  --create-config \
  --output data/output/licsbar
```

This will create a directory structure compatible with LiCSBAS and prepare:
- Unwrapped interferograms
- Coherence maps
- Baseline information
- Configuration template

### 4. Run LiCSBAS Time-Series Analysis

After preparing the data, use LiCSBAS for time-series processing:

```bash
# LiCSBAS is a separate repository
# See: https://github.com/yumorishita/LiCSBAS

# Example LiCSBAS workflow
LiCSBAS01_get_geotiff.py -d data/output/licsbar/GEOCml10FRAME
LiCSBAS02_ml_prep.py -i GEOCml10FRAME -o TS_GEOCml10FRAME -n 10
# ... continue with LiCSBAS processing steps
```

## Configuration Files

### Download Configuration (`config/download_config.yaml`)
- EOC Geoservice credentials
- Area of interest (bounding box)
- Time range for data acquisition
- Product specifications

### Processing Configuration (`config/processing_config.yaml`)
- GAMMA installation path
- Processing parameters (coregistration, filtering, unwrapping)
- Pair selection criteria
- Geocoding options

### Pairs File (`examples/example_pairs.json`)
- List of interferometric pairs to process
- Baseline information (perpendicular and temporal)

## Important Notes

### GAMMA Software License

**GAMMA is commercial software and is NOT open source.** This repository provides:
- Python wrappers and utilities for GAMMA workflows
- Scripts to organize GAMMA processing
- Data preparation for downstream analysis

You must:
- Purchase a GAMMA license from Gamma Remote Sensing AG
- Install GAMMA software separately
- Accept GAMMA's license terms

The actual GAMMA processing commands are placeholders in this repository. Users with valid GAMMA licenses should adapt the scripts to call actual GAMMA commands.

### Data Access

TerraSAR-X data access requires:
- EOC Geoservice registration
- Proper credentials
- Acceptance of data terms and conditions

### Data Size

TerraSAR-X data files can be large (several GB per scene). Ensure adequate:
- Disk space for raw data, processing, and outputs
- Network bandwidth for downloads
- Processing time for interferogram generation

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## References

- **GAMMA Software**: https://www.gamma-rs.ch/
- **TerraSAR-X**: https://www.dlr.de/en/terrasar-x
- **EOC Geoservice**: https://geoservice.dlr.de/
- **LiCSBAS**: https://github.com/yumorishita/LiCSBAS
- **COMET-LiCS**: https://comet.nerc.ac.uk/comet-lics-portal/

## License

This repository contains scripts and utilities for organizing TerraSAR-X data processing workflows. 

**Note**: GAMMA software is commercial and requires a separate license. This repository does not include or distribute GAMMA software.

## Support

For issues related to:
- **This repository**: Open an issue on GitHub
- **GAMMA software**: Contact Gamma Remote Sensing AG
- **EOC data access**: Contact EOC Geoservice support
- **LiCSBAS**: See LiCSBAS repository

## Acknowledgments

This work supports research at Geohazard Supersites using TerraSAR-X satellite data for ground deformation monitoring.
