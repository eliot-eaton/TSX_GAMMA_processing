#!/usr/bin/env python3
from tsx_if_proc_functions_dev import *

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
    config['rslc_dir'] = os.path.join(topdir, 'rslcs')
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


    print(bcolors.OKCYAN+"Dates provided are in correct format: Validation passed. Updated dateM:", dateM,bcolors.ENDC)
    print(bcolors.WARNING+f'{len(dates1)} Ifgms to be processed'+bcolors.ENDC)
    
    print('Writing to:',os.path.join(topdir, 'log_proc_master_slc.txt'))
    log_file_path = os.path.join(topdir, 'log_proc_master_slc.txt')
    sys.stdout = open(log_file_path, 'w')
    sys.stderr = sys.stdout
    try:
        if not os.path.exists(os.path.join(topdir,'slcs',f'{dateM}M')):
            proc_master_slc(config) # Process master SLC
            config = dem_to_master(config) # Generate look-up tables for DEM 
        
        else:
            config = dem_to_master(config) 
            print(f"Master SLC already exists for {dateM}. Skipping master SLC processing.")
    except Exception as e:
        print("Error in master SLC processing:", e)
        return
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    produce_lookvectors(config) # Produce look vectors



if __name__ == "__main__":
    main()

