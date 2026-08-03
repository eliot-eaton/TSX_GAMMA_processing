#!/usr/bin/env python3
import os
from tsx_if_proc_functions_dev import *
import argparse
import glob
import shutil

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script to process TSX or TDX slcs to IF.")
    # Add arguments
    parser.add_argument('config_file', type=str, help='config file')
    args = parser.parse_args()
    # Directory organisations 
    topdir = os.getcwd()

    print(f"Processing in {topdir}")
    
    # Load the config file
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    config['topdir'] = topdir
    config['slc_dir'] = os.path.join(topdir, 'slcs')
    config['dim_dir'] = os.path.join(topdir,'*')
    config['og_dem_dir'] = os.path.join(topdir,'..','dem')
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

    

    print('Number of unique dates to process: ',len(unique_dates))
    
    # Sort unique_dates in chronological order
    unique_dates = sorted(unique_dates, key=lambda x: datetime.strptime(x, "%Y%m%d"))

    dest_dir = os.path.join(topdir, "LiCSBAS", "GEOC")
    
    # Ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    pg.data2geotiff(f"./slcs/{dateM}M/P.dem_par",f"./slcs/{dateM}M/{dateM}.geo.mli", 2, f"./LiCSBAS/GEOC/{dateM}.geo.mli.tif")
    # Check if baselines file exists, if not create it
    if os.path.exists(os.path.join(topdir,'baselines')):
        print('baselines file exists')
    else:
        for date in unique_dates:
            baseline_relative_to_master(date,config)


    # Define source patterns and destination directory
    patterns = [
        "slcs/*M/*M.hgt.geotiff.tif",
        "geo/*M.geo.E.tif",
        "geo/*M.geo.U.tif",
        "geo/*M.geo.N.tif",
        f'{os.path.join(topdir,"baselines")}'
    ]

    # Copy files matching each pattern to destination
    for pattern in patterns:
        for src_file in glob.glob(os.path.join(topdir, pattern)):
            # If it's a hgt.geotiff.tif, rename to geo.hgt.tif
            if src_file.endswith("hgt.geotiff.tif"):
                # Replace .hgt.geotiff.tif with .geo.hgt.tif
                base = os.path.basename(src_file)
                new_name = base.replace(".hgt.geotiff.tif", ".geo.hgt.tif")
                dest_path = os.path.join(dest_dir, new_name)
                shutil.copy(src_file, dest_path)
                print(f"Copied {src_file} to {dest_path}")
            else:
                shutil.copy(src_file, dest_dir)
                print(f"Copied {src_file} to {dest_dir}")
    
    # Use multiprocessing to run output_tifs for all unique dates
    # Redirect all output printed to the screen to a text file called log_output_licsbas
    print('Writing to:',os.path.join(topdir, 'log_output_licsbas.txt'))
    log_file_path = os.path.join(topdir, 'log_output_licsbas.txt')
    sys.stdout = open(log_file_path, 'w')
    sys.stderr = sys.stdout
    try:
        with Pool(6) as pool:
            results = pool.starmap(output_licsbas_tifs, [(date1, date2, config) for date1, date2 in zip(dates1, dates2)])
            # close pool to prevent new tasks and wait for all current tasks to finish
            pool.close()
            pool.join()
    except Exception as e:
        print("Error in output tif processing:", e)
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Create configuration for step 6_1 (cropping)
    crop_config = {
        "lat_max": 3.179134,
        "lon_min": 98.382771,
        "lat_min": 3.159834,
        "lon_max": 98.400920,
        "input_dir": os.path.join(topdir, 'LiCSBAS', 'GEOC'),
        "output_dir": os.path.join(topdir, 'LiCSBAS_crop', 'GEOC'),
        "date_min": "20500101",
        "date_max": "20000101"
    }

    # Write crop configuration to JSON file
    crop_config_file = os.path.join(topdir, 'step6_1_crop_config.json')
    if not os.path.exists(crop_config_file):
        with open(crop_config_file, 'w') as f:
            json.dump(crop_config, f, indent=4)
        print(f"Created crop configuration file: {crop_config_file}")
    else:
        print(f"Crop configuration file already exists: {crop_config_file}")




if __name__ == "__main__":
    main()

