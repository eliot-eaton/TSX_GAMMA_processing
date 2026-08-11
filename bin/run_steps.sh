#!/bin/bash
dev_tsx_step1_dim_to_slc.py  config_proc.json
dev_tsx_step2_master_dem.py config_proc.json
dev_tsx_step3_slc_to_rslc.py config_proc.json
dev_tsx_step4_if_step5_unw.py config_proc.json
