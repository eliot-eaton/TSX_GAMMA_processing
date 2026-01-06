# Workflow Documentation

This document describes the typical workflow for processing TerraSAR-X data using this repository.

## Complete Processing Workflow

### Step 1: Setup Environment

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install GAMMA software (requires commercial license):
   - Obtain license from https://www.gamma-rs.ch/
   - Install GAMMA software
   - Set environment variable:
```bash
export GAMMA_HOME=/path/to/gamma/installation
```

3. Register for EOC Geoservice access:
   - Create account at EOC Geoservice
   - Obtain credentials for TerraSAR-X data

### Step 2: Configure Processing

1. Edit download configuration (`config/download_config.yaml`):
   - Add your EOC credentials
   - Define area of interest (bounding box)
   - Set time range for data acquisition
   - Choose product type (SSC recommended for InSAR)

2. Edit processing configuration (`config/processing_config.yaml`):
   - Set GAMMA_HOME path
   - Configure processing parameters
   - Adjust filtering and unwrapping settings
   - Set pair selection criteria

### Step 3: Download TerraSAR-X Data

Download data for your area and time period:

```bash
python src/download/tsx_downloader.py \
  --config config/download_config.yaml
```

Or using command-line arguments:

```bash
python src/download/tsx_downloader.py \
  --bbox 10.0 45.0 11.0 46.0 \
  --start 2020-01-01 \
  --end 2020-12-31 \
  --username YOUR_USERNAME \
  --password YOUR_PASSWORD \
  --output-dir data/raw
```

Downloaded data will be saved in `data/raw/`.

### Step 4: Process with GAMMA InSAR

Process interferometric pairs:

```bash
# Process a single pair
python src/gamma_processing/insar_processor.py \
  --master data/raw/TSX1_SAR__SSC_20200101.tar.gz \
  --slave data/raw/TSX1_SAR__SSC_20200113.tar.gz \
  --dem data/dem/dem.tif \
  --output pair_20200101_20200113 \
  --work-dir data/processed
```

The processing includes:
1. Import TerraSAR-X data to GAMMA format
2. Coregister slave to master
3. Generate interferogram
4. Filter interferogram
5. Unwrap phase
6. Geocode results

Processed products will be in `data/processed/`.

### Step 5: Prepare for LiCSBAS

Convert GAMMA products to LiCSBAS format:

```bash
# First, create pairs list (JSON format)
# See examples/example_pairs.json for format

# Prepare interferograms
python src/licsbar_prep/prepare_licsbar.py \
  --input data/processed \
  --output data/output/licsbar \
  --pairs examples/example_pairs.json

# Generate LiCSBAS configuration template
python src/licsbar_prep/prepare_licsbar.py \
  --create-config \
  --output data/output/licsbar
```

This creates:
- `GEOCml10FRAME/` directory with interferograms
- Baseline file for LiCSBAS
- Configuration template

### Step 6: Run LiCSBAS Time-Series Analysis

Use LiCSBAS for time-series processing:

```bash
# Clone LiCSBAS repository
git clone https://github.com/yumorishita/LiCSBAS.git

# Add LiCSBAS to PATH
export PATH=$PATH:/path/to/LiCSBAS/bin

# Run LiCSBAS workflow
cd data/output/licsbar

# Step 1: Prepare GeoTIFF data
LiCSBAS01_get_geotiff.py -d GEOCml10FRAME

# Step 2: Multi-look and prepare
LiCSBAS02_ml_prep.py -i GEOCml10FRAME -o TS_GEOCml10FRAME -n 10

# Continue with remaining LiCSBAS steps...
# See LiCSBAS documentation for complete workflow
```

## Data Organization

After processing, your directory structure will look like:

```
TSX_supersite_GAMMA_processing/
├── data/
│   ├── raw/                    # Downloaded TerraSAR-X data
│   │   └── TSX1_SAR__*.tar.gz
│   ├── processed/              # GAMMA processed products
│   │   ├── *.slc              # Single Look Complex
│   │   ├── *.int              # Interferograms
│   │   ├── *.cc               # Coherence
│   │   ├── *.unw              # Unwrapped phase
│   │   └── *.geo.tif          # Geocoded products
│   └── output/
│       └── licsbar/           # LiCSBAS-ready data
│           ├── GEOCml10FRAME/ # Interferograms for LiCSBAS
│           └── TS_GEOCml10FRAME/ # Time-series results
```

## Troubleshooting

### GAMMA not found
- Ensure GAMMA is installed
- Set `GAMMA_HOME` environment variable
- Verify GAMMA license is valid

### Download failures
- Check EOC credentials
- Verify internet connection
- Check data availability for your area/time

### Processing errors
- Check DEM coverage matches your area
- Verify input data quality
- Review GAMMA log files
- Ensure sufficient disk space

### LiCSBAS preparation issues
- Verify GAMMA products exist
- Check pairs.json format
- Ensure proper georeferencing

## Tips for Best Results

1. **Baseline Selection**: 
   - Keep perpendicular baselines < 300m
   - Use temporal baselines of 11-12 days for TerraSAR-X

2. **DEM Quality**:
   - Use high-quality DEM (SRTM 30m or better)
   - Ensure DEM covers entire area of interest

3. **Coherence**:
   - Higher coherence in urban areas
   - Lower in vegetated areas
   - Consider seasonal variations

4. **Processing Resources**:
   - GAMMA processing is CPU-intensive
   - Ensure adequate disk space (>100GB recommended)
   - Consider parallel processing for multiple pairs

## References

- GAMMA Software Manual: https://www.gamma-rs.ch/
- LiCSBAS Documentation: https://github.com/yumorishita/LiCSBAS
- TerraSAR-X Product Guide: https://www.dlr.de/
