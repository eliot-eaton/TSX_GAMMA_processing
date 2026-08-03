# TSX_supersite_GAMMA_processing

Scripts for TerraSAR-X / TanDEM-X interferometric processing with **GAMMA**.

## Important dependency

This repository depends on the **commercial GAMMA software** (including `py_gamma`).
Without a valid GAMMA installation and license, these scripts will not run.

## Repository layout

- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step1_dim_to_slc.py` — build SLCs from input products
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step2_master_dem.py` — set master and prepare DEM products
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step3_slc_to_rslc.py` — coregister to RSLC
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step4_if_step5_unw.py` — create interferograms (step 4) and unwrap (step 5)
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step6_output_to_licsbas.py` — export outputs for LiCSBAS
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_pixel_offset_tracking.py` — optional pixel offset workflow
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/tsx_if_proc_functions_dev.py` — shared processing functions
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/SLC_coreg.py` — coregistration helper
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/find_unw_seed.py` — helper for unwrap seed selection
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/check_complete_ifgm_dirs.sh` — check/remove incomplete IFG folders
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/uncompress_tar_gz_then_delete.sh` — unpack `*.tar.gz` into `dims/`
- `/home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json` — processing config template

## Setup

### 1) Python environment

Install Python packages used by the scripts (example):

```bash
pip install numpy pandas matplotlib
```

### 2) Make scripts executable

```bash
chmod +x /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/*.py
chmod +x /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/*.sh
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
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step1_dim_to_slc.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step2_master_dem.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step3_slc_to_rslc.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step4_if_step5_unw.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_step6_output_to_licsbas.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
```

Optional:

```bash
python /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/dev_tsx_pixel_offset_tracking.py /home/runner/work/TSX_supersite_GAMMA_processing/TSX_supersite_GAMMA_processing/bin/config_proc.json
```

## Are any scripts missing?

I checked script references in this repository and the listed processing/utility scripts are present.

Notes:
- There is no separate `step5` file because step 5 is handled inside `dev_tsx_step4_if_step5_unw.py`.
- There are commented references in code to an external `geocoding.py` path; this is not an active runtime dependency in the current scripts.
