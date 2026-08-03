# TSX_supersite_GAMMA_processing

Processing Scripts for TerraSAR-X / TanDEM-X interferometric processing with **GAMMA** used for SBAS InSAR during Volcanology PhD .

## Important dependency

This repository depends on the **commercial GAMMA software** (including `py_gamma`).
Without a valid GAMMA installation and license, these scripts will not run.

## Repository layout

- `dev_tsx_step1_dim_to_slc.py` — build SLCs from input products
- `dev_tsx_step2_master_dem.py` — set master and prepare DEM products
- `dev_tsx_step3_slc_to_rslc.py` — coregister to RSLC
- `dev_tsx_step4_if_step5_unw.py` — create interferograms (step 4) and unwrap (step 5)
- `dev_tsx_step6_output_to_licsbas.py` — export outputs for LiCSBAS
- `dev_tsx_pixel_offset_tracking.py` — optional pixel offset workflow
- `tsx_if_proc_functions_dev.py` — shared processing functions
- `SLC_coreg.py` — coregistration helper
- `find_unw_seed.py` — helper for unwrap seed selection
- `check_complete_ifgm_dirs.sh` — check/remove incomplete IFG folders
- `uncompress_tar_gz_then_delete.sh` — unpack `*.tar.gz` into `dims/`
- `config_proc.json` — processing config template

## Setup

### 1) Python environment

Install Python packages used by the scripts (example):

```bash
pip install numpy pandas matplotlib
```

### 2) Make scripts executable

```bash
chmod +x ./bin/*.py
chmod +x ./bin/*.sh
```

### 3) Add GAMMA to your environment (`PATH` and `PYTHONPATH`)

Set these according to your GAMMA installation location:

```bash
export GAMMA_HOME=/path/to/GAMMA
export PATH="$GAMMA_HOME/bin:$PATH"
export PYTHONPATH="$GAMMA_HOME/python:$PYTHONPATH"
```

If `py_gamma` is installed in a different directory, append that directory to `PYTHONPATH` instead.

To persist, place the exports in your shell profile (for example `~/.bashrc`) and reload it.

## Basic usage

Run each step from your processing working directory (where data folders are located), passing the config file:

```bash
dev_tsx_step1_dim_to_slc.py config_proc.json
dev_tsx_step2_master_dem.py config_proc.json
dev_tsx_step3_slc_to_rslc.py config_proc.json
dev_tsx_step4_if_step5_unw.py config_proc.json
dev_tsx_step6_output_to_licsbas.py config_proc.json
```

## `config_proc.json`

The `config_proc.json` file controls interferometric processing, including multilooking, DEM sampling, date selection, cropping, unwrapping, and output generation.

### Example configuration

```json
{
  "rlks": 6,
  "azlks": 3,
  "dem": "wolf_cop30",
  "demlat": 8,
  "demlon": 8,
  "npat_r": 1,
  "npat_az": 1,
  "r_init": 2000,
  "az_init": 2000,
  "dateM": "20251102",
  "n_days": 22,
  "dateS": "20221101",
  "dateE": "20221230",
  "orbit_dir_file": "asc_or_desc_dates.txt",
  "min_n_days": 1,
  "crop_az": false,
  "min_lat": "-0.5",
  "max_lat": "-0.17",
  "cleanup": true,
  "proc_slc_to_rslc": true,
  "proc_if": true,
  "proc_unw": true,
  "minimal_output": true,
  "bperp_threshold": 400,
  "rslc_dates": false
}
```

### Parameter reference

| Parameter          |             Type | Description                                                                                                                                           |
| ------------------ | ---------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rlks`             |          Integer | Number of looks applied in the range direction.                                                                                                       |
| `azlks`            |          Integer | Number of looks applied in the azimuth direction.                                                                                                     |
| `dem`              |           String | Name of the DEM used during processing. For example, `wolf_cop30` refers to a DEM expected at a path such as `./working_dir/../dem/*/wolf_cop30.dem`. |
| `demlat`           |          Integer | DEM oversampling factor in the latitude direction.                                                                                                    |
| `demlon`           |          Integer | DEM oversampling factor in the longitude direction.                                                                                                   |
| `npat_r`           |          Integer | Processing patch parameter in the range direction.                                                                                                    |
| `npat_az`          |          Integer | Processing patch parameter in the azimuth direction.                                                                                                  |
| `r_init`           |          Integer | Initial range coordinate used as the seed location for phase unwrapping.                                                                              |
| `az_init`          |          Integer | Initial azimuth coordinate used as the seed location for phase unwrapping.                                                                            |
| `dateM`            |           String | Master or reference acquisition date, in `YYYYMMDD` format.                                                                                           |
| `n_days`           |          Integer | Maximum temporal separation, in days, between acquisitions used to generate interferograms.                                                           |
| `dateS`            |           String | Start of the acquisition-date range, in `YYYYMMDD` format. Only acquisitions on or after this date are used.                                          |
| `dateE`            |           String | End of the acquisition-date range, in `YYYYMMDD` format. Only acquisitions on or before this date are used.                                           |
| `orbit_dir_file`   |           String | File containing acquisition dates grouped or identified by orbit direction, such as ascending or descending.                                          |
| `min_n_days`       |          Integer | Minimum temporal separation, in days, between acquisitions used to generate interferograms.                                                           |
| `crop_az`          |          Boolean | Enables or disables cropping in the azimuth direction.                                                                                                |
| `min_lat`          | String or Number | Minimum latitude used when spatial cropping is enabled.                                                                                               |
| `max_lat`          | String or Number | Maximum latitude used when spatial cropping is enabled.                                                                                               |
| `cleanup`          |          Boolean | Removes intermediate files and avoids generating non-essential outputs to reduce disk usage.                                                          |
| `proc_slc_to_rslc` |          Boolean | Enables processing from SLC products to registered SLC products.                                                                                      |
| `proc_if`          |          Boolean | Enables interferogram generation.                                                                                                                     |
| `proc_unw`         |          Boolean | Enables phase unwrapping.                                                                                                                             |
| `minimal_output`   |          Boolean | Produces only the minimum required set of output files.                                                                                               |
| `bperp_threshold`  |           Number | Maximum allowed perpendicular baseline for an interferometric pair.                                                                                   |
| `rslc_dates`       |          Boolean | Uses available RSLC dates when the original SLC files have been deleted to save disk space.                                                           |

### Date format

All date parameters must use the following format:

```text
YYYYMMDD
```

For example, `20221101` represents 1 November 2022.

### Important checks

* `min_n_days` should be less than or equal to `n_days`.
* `dateS` should be earlier than or equal to `dateE`.
* The master date specified by `dateM` should normally correspond to an available acquisition and should be consistent with the selected processing period.
* Set `crop_az` to `true` before relying on `min_lat` and `max_lat` for cropping.
* For consistency, consider storing `min_lat` and `max_lat` as JSON numbers rather than strings:

```json
"min_lat": -0.5,
"max_lat": -0.17
```
