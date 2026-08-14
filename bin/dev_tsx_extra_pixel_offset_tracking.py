#!/usr/bin/env python3
import multiprocessing
from tsx_if_proc_functions_dev import *
import argparse
def worker(args):
    date1, date2, config = args
    try:
        pixel_offset_tracking(date1, date2, config)
        return (date1, date2, True)
    except Exception as e:
        print(f"Failed {date1}, {date2}: {e}")
        return (date1, date2, False)
def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script to process TSX or TDX slcs to pixel offset tracking.")
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


    # Sort unique_dates in chronological order
    unique_dates = sorted(unique_dates, key=lambda x: datetime.strptime(x, "%Y%m%d"))

    
   
    processed_pairs = []
    to_be_processed = list(zip(dates1, dates2))
    
    print('Finished processing dim to slc to rslc')

    print('Writing to:',os.path.join(topdir, 'log_proc_pixel_offset_tracking.txt'))
    # Redirect all output printed to the screen to a text file called log_proc_pixel_offset_tracking.txt
  

    args_list = [(d1, d2, config) for d1, d2 in zip(dates1, dates2)]
    processed_pairs = []
    to_be_processed = list(zip(dates1, dates2))

    with multiprocessing.Pool() as pool:
        results = pool.map(worker, args_list)

    for date1, date2, success in results:
        if success:
            processed_pairs.append((date1, date2))
        if (date1, date2) in to_be_processed:
            to_be_processed.remove((date1, date2))



if __name__ == "__main__":
    main()