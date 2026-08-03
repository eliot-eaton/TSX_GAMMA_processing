#!/usr/bin/env python3
from tsx_if_proc_functions_dev import *
import argparse

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


    # Sort unique_dates in chronological order
    unique_dates = sorted(unique_dates, key=lambda x: datetime.strptime(x, "%Y%m%d"))

    
   
    processed_pairs = []
    to_be_processed = list(zip(dates1, dates2))
    
    print('Finished processing dim to slc to rslc')

    print('Writing to:',os.path.join(topdir, 'log_proc_if_unw.txt'))
    # Redirect all output printed to the screen to a text file called log_proc_if_unw.txt
   
    for date1, date2 in zip(dates1, dates2):
     
        if config['proc_if']:
            unw_q = proc_if(date1, date2, config)
        if config['proc_unw']:
            if unw_q: 
                proc_unw(date1, date2, config)
    
        processed_pairs.append((date1, date2))
        to_be_processed.remove((date1, date2))
        print(f"Processed {date1} and {date2}. Remaining pairs: {len(to_be_processed)}")





if __name__ == "__main__":
    main()

