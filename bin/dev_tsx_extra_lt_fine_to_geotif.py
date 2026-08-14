#!/usr/bin/env python3
from tsx_if_proc_functions_dev import *
import argparse

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script to process TSX or TDX slcs to IF.")
    # Add arguments
    parser.add_argument('config_file', type=str, help='config file')
    parser.add_argument('adf_unw_file', type=str, nargs='?',help='config file')
    args = parser.parse_args()
    # Directory organisations 
    topdir = os.getcwd()

    print(f"Processing in {topdir}")
    
    # Load the config file
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    if args.adf_unw_file:
         # print in blue, 
        print(bcolors.OKBLUE + f'Using ADF and UNW config' + bcolors.ENDC)
        with open(args.adf_unw_file, 'r') as f:
            adf_unw_config = json.load(f)
        config.update(adf_unw_config)
    
    config['topdir'] = topdir
    config['slc_dir'] = os.path.join(topdir, 'slcs')
    config['dim_dir'] = os.path.join(topdir,'*')
    config['og_dem_dir'] = os.path.join(topdir,'..','dem')
    config['rslc_dir'] = os.path.join(topdir, 'rslc')
    dateM = config['dateM']
    ndays = config['n_days']
    min_n_days = config['min_n_days']
    date_min = config['dateS']
    date_max = config['dateE']
    cleanup = config['cleanup']
    # Call the function to validate and possibly update dateM
    #try:
   
    dem_par = os.path.join(topdir, 'slcs', f'{dateM}M', 'P.dem_par')
    lt_fine_file = os.path.join(topdir, 'slcs', f'{dateM}M', f'{dateM}M.lt_fine')
    dem_bin = os.path.join(topdir, 'slcs', f'{dateM}M', 'P.dem')
    ls_map_file = os.path.join(topdir, 'geo', 'ls_map')

    pg.data2geotiff(dem_par, lt_fine_file, 4, os.path.join(topdir, 'slcs', f'{dateM}M', f'{dateM}M.lt_fine.geo.tif'))

    pg.data2geotiff(dem_par, dem_bin, 2, os.path.join(topdir, 'slcs', f'{dateM}M', f'P.dem.geo.tif'))
                
    pg.data2geotiff(dem_par, ls_map_file, 2,ls_map_file+'.geo.tif')
             



if __name__ == "__main__":
    main()

