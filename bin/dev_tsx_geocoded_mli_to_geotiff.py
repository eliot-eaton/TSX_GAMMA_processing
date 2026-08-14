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
    print('Writing to:',os.path.join(topdir, 'log_construct_dates.txt'))
    log_file_path = os.path.join(topdir, 'log_construct_dates.txt')
    sys.stdout = open(log_file_path, 'w')
    sys.stderr = sys.stdout
    try:

        dates1,dates2=construct_date1_date2_combinations(config,ndays,date_min,date_max)
   
        unique_dates = list(set(dates1 + dates2)) # Create a list of unique dates
        if len(unique_dates) == 0:
            print("No unique dates found. Exiting.")
            sys.exit(1)
        dateM = validate_dates(dateM, dates1, dates2)
    except Exception as e:
        print("Error in date construction:", e)
        return
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


    # Sort unique_dates in chronological order
    unique_dates = sorted(unique_dates, key=lambda x: datetime.strptime(x, "%Y%m%d"))

    dem_par = pg.ParFile(os.path.join(topdir, 'slcs', f'{dateM}M', 'P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    
   

    for date in unique_dates:
        print(f"Processing date: {date}")
        rslc_dir = os.path.join(topdir, 'rslc')

        rslc_date_dir = os.path.join(rslc_dir, date)
        rmli_geo_file = os.path.join(rslc_date_dir, f'{date}_geocode.mli')
        pg.data2geotiff(dem_par, rmli_geo_file, 2, os.path.join(rslc_date_dir, f'{date}_geocode.mli.tif'))
        




if __name__ == "__main__":
    main()

