#!/usr/bin/env python3
from glob import glob

from logging import config
import os 
from datetime import datetime
import pdb 
import sys
import itertools
#from networkx import config
import numpy as np
from multiprocessing import Pool
import argparse
import re 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from datetime import timedelta
import json
import matplotlib.dates as mdates
from contextlib import redirect_stdout
import shutil
import subprocess
try:
    import py_gamma as pg
except ImportError:
    print("py_gamma module not found. Please install it to use this script.")
    sys.exit(1)
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def within_90_degrees(angle1, angle2):
    diff = abs(angle1 - angle2) % 360
    return diff <= 90 or diff >= 270



def find_available_date_files(top_dir,dateM,date1,date2):
    
    date_list = []
    
    for file in glob(os.path.join(top_dir,'*','*','TSX-1*','T?X*')):
       
        file_split =  file.split('/')[-1].split('_')
        date_str = file_split[-1][:8]
        date_list.append(date_str)
        #print(bcolors.OKGREEN+file+bcolors.ENDC)
    

    for date_i in [dateM,date1,date2]:
        if date_i not in date_list:
            print(bcolors.WARNING+f'{date_i} not found in date list'+bcolors.ENDC)
            sys.exit()	
       
    return date_list


def check_dates(date1_str, date2_str, date_min_str, date_max_str):
    # Define the date format
    date_format = "%Y%m%d"
    
    try:
        # Convert date strings to datetime objects
        date1 = datetime.strptime(date1_str, date_format)
        date2 = datetime.strptime(date2_str, date_format)
        date_min = datetime.strptime(date_min_str, date_format)
        date_max = datetime.strptime(date_max_str, date_format)
        
        # Perform the checks
        is_date1_not_equal_date2 = date1 != date2
        is_date1_before_date2 = date1 < date2
        is_date1_in_range = date_min < date1 < date_max
        is_date2_in_range = date_min < date2 < date_max 
        # Create a dictionary to store the results of the checks
        check_results = {
            "date1": date1_str,
            "date2": date2_str,
            "is_date1_not_equal_date2": is_date1_not_equal_date2,
            "is_date1_before_date2": is_date1_before_date2,
            "is_date1_in_range": is_date1_in_range,
            "is_date2_in_range": is_date2_in_range
        }

        # Write the results to a text file
        with open("date_checks.txt", "a") as file:
            file.write(f"{check_results}\n")
        
        if is_date1_before_date2 and is_date1_in_range and is_date2_in_range and is_date1_not_equal_date2:
            return True
        else:
            return False
            
    except ValueError as e:
        # Handle invalid date formats
        print(f"Error: {e}")
        return False

def construct_s1_date_combinations(config,n_days,date_min,date_max):



    date_list = []
    topdir = config['topdir']

    slc_dir = config['slc_dir']
    min_n_days = config['min_n_days']
    safe_dir = os.path.join(topdir,'safes')

    # how to search for yyyymmddT in filename 

    

    if not os.path.exists(os.path.join(topdir,'safes')):
        print('Using SLCs to find dates')
        search_list = glob(os.path.join(slc_dir,'*'))
        date_list = [os.path.split(file)[-1] for file in search_list]
        date_list = [date for date in date_list if 'M' not in date]
    else:
        print('Using SAFES to find dates')
        safe_folders = [f for f in os.listdir(safe_dir) if f.endswith('.SAFE') and os.path.isdir(os.path.join(safe_dir, f))]
        date_list=[]
        for folder in safe_folders:
            # Extract dates in the format YYYYMMDD from the folder name
            date_match = re.search(r'_(\d{8})T', folder)
            if date_match:
                date = date_match.group(1)
                date_list.append(date)
    

    #print(date_list)    
    # Initialize lists to store paired dates
    dates1 = []
    dates2 = []
    
    # Sort the date list
    date_array_sorted = sorted(date_list, key=lambda x: datetime.strptime(x, '%Y%m%d'))
    
    # Use itertools.combinations to generate all possible pairs
    combinations = itertools.combinations(date_array_sorted, 2)
    # Ensure each pair is ordered from earliest to latest
    date_pairs = [(min(date1, date2), max(date1, date2)) for date1, date2 in combinations]
    date_pairs = sorted(date_pairs, key=lambda x: datetime.strptime(x[0], '%Y%m%d'))
    for date1, date2 in date_pairs:
        
        if check_dates(date1, date2, date_min, date_max):
            print(f"Checking  pair {date1} - {date2}")
            date1_dt = datetime.strptime(date1, '%Y%m%d')
            date2_dt = datetime.strptime(date2, '%Y%m%d')
    
            # Calculate the difference in days between the two dates
            delta = abs((date2_dt - date1_dt).days)
            if min_n_days <= delta <= n_days:
                dates1.append(date1)
                dates2.append(date2)

            else:
                print(f"Skipping pair {date1} - {date2}")
        
    date_array = np.array(date_list)
    # remove repeated dates
    date_array = np.unique(date_array)
    # sort date array min to max
    date_array_sorted = np.sort(date_array)
    
        
    # Use itertools.combinations to generate all possible pairs
    combinations = itertools.combinations(date_array_sorted, 2)
    # Ensure each pair is ordered from earliest to latest
    date_pairs = [(min(date1, date2), max(date1, date2)) for date1, date2 in combinations]
    date_pairs = sorted(date_pairs, key=lambda x: datetime.strptime(x[0], '%Y%m%d'))
    for date1, date2 in date_pairs:
        
        if check_dates(date1, date2, date_min, date_max):
            print(f"Checking  pair {date1} - {date2}")
            date1_dt = datetime.strptime(date1, '%Y%m%d')
            date2_dt = datetime.strptime(date2, '%Y%m%d')
    
            # Calculate the difference in days between the two dates
            delta = abs((date2_dt - date1_dt).days)
            if min_n_days <= delta <= n_days:
                dates1.append(date1)
                dates2.append(date2)

            else:
                print(f"Skipping pair {date1} - {date2}")

    return dates1,dates2
 
  
def construct_date1_date2_combinations(config,n_days,date_min,date_max,step1=False):
    date_list = []
    topdir = config['topdir']
    slc_dir = config['slc_dir']
    min_n_days = config['min_n_days']

    no_important_date = True
    if "important_date" in config:
        important_date = config["important_date"]
        no_important_date = False

    if 'rslc_dates' in config:
        rslc_dates = config['rslc_dates'] 
    else:
        rslc_dates = False
    # how to search for yyyymmddT in filename 

    # check if config['rlc_for_dates'] is true, y names.

    if rslc_dates == True:
          
        print('Using RSLCS to find dates')
        search_list = glob(os.path.join(topdir,'rslc','*'))
        date_list = [os.path.split(file)[-1] for file in search_list]
        date_list = [date for date in date_list if 'M' not in date]
    else:
        if not os.path.exists(os.path.join(topdir,'dims')):
            
            
            print('Using SLCs to find dates')
            search_list = glob(os.path.join(slc_dir,'*'))
            date_list = [os.path.split(file)[-1] for file in search_list]
            date_list = [date for date in date_list if 'M' not in date]
        else:
            print('Using Dims to find dates')
            search_list = glob(os.path.join(topdir,'*','*','TSX-1*','T?X*'))
            
            for file in search_list:
                file_split =  file.split('/')[-1].split('_')
                #print(file)
                date_str = file_split[-1][:8]
                if  date_str in date_list:
                    print(bcolors.WARNING+f'{date_str} is repeated'+bcolors.ENDC)
                    print(file)
                
            
                # Check date tar has corresponding dim 
                try:
                    dim_path_check = glob(os.path.join(topdir,'*','*','TSX-1*',f'T?X*{date_str}*','*xml'))[0]
                except Exception as e:
                    dim_path_check = ''
                    # Code that runs if an exception occurs
                    print(f"An error occurred: {e}")
                    print(bcolors.WARNING+f'Warning: {date_str} no corresponding DIM'+bcolors.ENDC)
                finally:
                    if os.path.exists(dim_path_check):
                        date_list.append(date_str)
                
    date_array = np.array(date_list)
    # remove repeated dates
    date_array = np.unique(date_array)
    # sort date array min to max
    date_array_sorted = np.sort(date_array)
    date_array_sorted = np.sort(date_array)
    
    

 
    # Check if date_list contains repeats
    # If it does, print a warning and exit the program
    # Otherwise, print the list of dates
    if len(date_list) != len(set(date_list)):
        print(bcolors.WARNING+"Warning: The date list contains repeated dates."+bcolors.ENDC)
        #find repeated dates and print the file path to repeated date 
        for date in set(date_list):
            if date_list.count(date) > 1:
                print(f"Repeated date: {date}")

    else:
        print(bcolors.OKGREEN+"The date list is:"+bcolors.ENDC)
        print(date_list) 
    

    if step1 and len(date_array_sorted) ==1:
        print(bcolors.WARNING+"Warning: Less than 2 unique dates found. Please check your data."+bcolors.ENDC)
        dates1 = list(date_array_sorted)
        dates2 = []
        return dates1,dates2
    #print(date_list)    
    # Initialize lists to store paired dates
    dates1 = []
    dates2 = []
    
    # Use itertools.combinations to generate all possible pairs
    combinations = itertools.combinations(date_array_sorted, 2)
    # Ensure each pair is ordered from earliest to latest
    date_pairs = [(min(date1, date2), max(date1, date2)) for date1, date2 in combinations]
    date_pairs = sorted(date_pairs, key=lambda x: datetime.strptime(x[0], '%Y%m%d'))
    for date1, date2 in date_pairs:
        
        # if no_important_date == false, then check if dates span the important date 
        if no_important_date == False:
         
            important_date_dt = datetime.strptime(important_date, '%Y%m%d')
            date1_dt = datetime.strptime(date1, '%Y%m%d')
            date2_dt = datetime.strptime(date2, '%Y%m%d')
            if not (date1_dt < important_date_dt < date2_dt):
                print(f"Skipping pair {date1} - {date2} as it does not span important date {important_date}")
                continue

        if check_dates(date1, date2, date_min, date_max):
            print(f"Checking  pair {date1} - {date2}")
            date1_dt = datetime.strptime(date1, '%Y%m%d')
            date2_dt = datetime.strptime(date2, '%Y%m%d')
    
            # Calculate the difference in days between the two dates
            delta = abs((date2_dt - date1_dt).days)
            if min_n_days <= delta <= n_days:
                dates1.append(date1)
                dates2.append(date2)

            else:
                print(f"Skipping pair {date1} - {date2}")
        

       
    return dates1,dates2



def validate_dates(dateM, date1, date2):
    # Validate dateM: it must be either an 8-digit string or a list of length 1 containing an 8-digit string.
    if isinstance(dateM, list):
        if len(dateM) == 1 and isinstance(dateM[0], str) and len(dateM[0]) == 8 and dateM[0].isdigit():
            dateM = dateM[0]  # Convert list of length 1 to an 8-digit string
        else:
            raise ValueError("dateM must be a list of length 1 containing an 8-digit string or an 8-digit string.")
    elif isinstance(dateM, str):
        if not (len(dateM) == 8 and dateM.isdigit()):
            raise ValueError("dateM must be an 8-digit string.")
    else:
        raise TypeError("dateM must be either a string or a list of length 1.")

    # Validate that date1 and date2 are lists of equal length and each element is an 8-digit string.
    if not (isinstance(date1, list) and isinstance(date2, list)):
        raise TypeError("date1 and date2 must both be lists.")

    if len(date1) != len(date2):
        raise ValueError("date1 and date2 must be of equal length.")

    for d1, d2 in zip(date1, date2):
        if not (isinstance(d1, str) and isinstance(d2, str) and len(d1) == 8 and len(d2) == 8 and d1.isdigit() and d2.isdigit()):
            raise ValueError("Each element of date1 and date2 must be an 8-digit string.")

    # Return the validated and possibly modified dateM
    return dateM





def safe_to_slc(date,config):
    print('in dim_to_slc')
    slc_dir = config['slc_dir']
    dim_dir = config['dim_dir']
    topdir = config['topdir']
    dateM = config['dateM']
    rlks, azlks = config["rlks"], config["azlks"], 
    os.chdir(topdir)

    # check if file has been processed previously and the file is in same orbit direction as master 
    

        
    if os.path.exists(os.path.join(slc_dir,date)):
        print(bcolors.WARNING + f"Skipping {date} as SLC directory already exists"+bcolors.ENDC)
        return
    else:
        os.makedirs(os.path.join(slc_dir,date))
    # find safe file
    safe_file = glob(os.path.join(topdir,'safes',f'*{date}*'))[0]
    if not os.path.exists(safe_file):
        print(bcolors.FAIL + f"ERROR: {date} safe file not found"+bcolors.ENDC)
        return
    else:
        print(bcolors.OKGREEN + f"Found safe file: {safe_file}"+bcolors.ENDC)

    active_beams=[]
    for b in range(1,4):
        GeoTIFF_pattern = f"{safe_file}/measurement/s1?-iw{b}-slc-vv*.tiff"
        annotation_XML_pattern = f'{safe_file}/annotation/s1?-iw{b}-slc-vv*.xml'
        calibration_XML_pattern = f'{safe_file}/annotation/calibration/calibration-s1?-iw{b}-slc-vv*.xml'
        noise_XML_pattern = f"{safe_file}/annotation/calibration/noise-s1?-iw{b}-slc-vv*.xml"

        GeoTIFF = glob(GeoTIFF_pattern)[0] if glob(GeoTIFF_pattern) else None
        annotation_XML = glob(annotation_XML_pattern)[0] if glob(annotation_XML_pattern) else None
        calibration_XML = glob(calibration_XML_pattern)[0] if glob(calibration_XML_pattern) else None
        noise_XML = glob(noise_XML_pattern)[0] if glob(noise_XML_pattern) else None
        par_file =  f"{date}.iw{b}.all.slc.par"
        slc_file =  f"{date}.iw{b}.all.slc"
        tops_par = f"{date}.iw{b}.all.slc.TOPS_par"
        dtype = 1 # S complex
        try:
            print(f'pg.par_S1_SLC({GeoTIFF},{annotation_XML},{calibration_XML},{noise_XML},{os.path.join(slc_dir,date,par_file)},{os.path.join(slc_dir,date,slc_file)},{dtype})')
            
            pg.par_S1_SLC(GeoTIFF,annotation_XML,calibration_XML,noise_XML,os.path.join(slc_dir,date,par_file),os.path.join(slc_dir,date,slc_file),dtype)
            active_beams.append(b)
            import pdb
            pdb.set_trace()
            
        except Exception as e:
            print(bcolors.FAIL + f"ERROR: {e}" + bcolors.ENDC)

    
    
    len_active_beams = len(active_beams)
    if len_active_beams == 0:
        print(bcolors.FAIL + f"ERROR: No active beams found for {date}" +
                " Skipping this date." + bcolors.ENDC)
        shutil.rmtree(os.path.join(slc_dir,date))
        return
    elif len_active_beams == 1:
        print(bcolors.WARNING + f"Warning: Only one active beam found for {date}" + bcolors.ENDC)
    elif len_active_beams > 1:
        for b in active_beams:
            par_file =  os.path.join(slc_dir,date,f"{date}.iw{b}.all.slc.par")
            slc_file =  os.path.join(slc_dir,date,f"{date}.iw{b}.all.slc")
            tops_par = os.path.join(slc_dir,date,f"{date}.iw{b}.all.slc.TOPS_par")

            slc_par = pg.ParFile(os.path.join(slc_dir, date, f"{date}.iw{b}.all.slc.par"))
            width_slc = int(slc_par.get_value('range_samples'))
            pg.rasSLC(slc_file,width_slc, 1, 0, 50, 10, 1., 0.35, 1, 1, 0, os.path.join(slc_dir,date,f'{date}.iw{b}.all.slc.tif'))
            with open(os.path.join(slc_dir, date, 'SLC_tab'), 'a') as f:
                f.write(f'{date}.iw{b}.slc {date}.iw{b}.slc.par {date}.iw{b}.slc.TOPS_par\n')
    

    pg.multi_S1_TOPS(os.path.join(slc_dir, date,'SLC_tab'), 
                     os.path.join(slc_dir, date,f'{date}.mli'),
                     os.path.join(slc_dir, date,f'{date}.mli.par'), rlks, azlks)
    mli_par = pg.ParFile(os.path.join(slc_dir, date,f'{date}.mli.par'))
    widthmli = int(mli_par.get_value('range_samples'))

    pg.raspwr(os.path.join(slc_dir, date,f'{date}.mli'), 
              widthmli, 1, 0, 10, 10, 1., 0.20, 1,
              os.path.join(slc_dir, date,f'{date}.mli.tif'))

    pg.SLC_mosaic_S1_TOPS(os.path.join(slc_dir, date,'SLC_tab'),
                            os.path.join(slc_dir, date,f'{date}.slc'),
                            os.path.join(slc_dir, date,f'{date}.slc.par'), rlks, azlks) 
    return print(bcolors.OKGREEN + 'scenes  SLC successful' + bcolors.ENDC)
    


def dim_to_slc(date,config):
    print('in dim_to_slc')
    slc_dir = config['slc_dir']
    dim_dir = config['dim_dir']
    topdir = config['topdir']
    dateM = config['dateM']
    os.chdir(topdir)

    # check if file has been processed previously and the file is in same orbit direction as master 
    

        
    if os.path.exists(os.path.join(slc_dir,date)):
        print(bcolors.WARNING + f"Skipping {date} as SLC directory already exists"+bcolors.ENDC)
        return
    else:
        os.makedirs(os.path.join(slc_dir,date))
    
    
    date_xml = glob(os.path.join(topdir,'*','*','TSX-1*',f'T?X*{date}*','*xml'))[0]
    date_cos = glob(os.path.join(topdir,'*','*','TSX-1*',f'T?X*{date}*','IMAGEDATA','*cos'))[0]

    for file in glob(os.path.join(dim_dir,'*','TSX-1*',f'T?X*{date}*','IMAGEDATA','*cos')):
        print(bcolors.OKBLUE+file+bcolors.ENDC)
    if len(glob(os.path.join(dim_dir,'*','TSX-1*',f'T?X*{date}*','IMAGEDATA','*cos'))) != 1:
        print(glob(os.path.join(dim_dir,'*','TSX-1*',f'TDX*{date}*','IMAGEDATA','*cos')))
        print(bcolors.OKCYAN+'WARNING multiple DIMS for same date. Going to try concat slcs \033[0m'+bcolors.ENDC)
        try:
            cat_multiple_slcs(date,config)
            return print(bcolors.OKGREEN + 'Concatenated SLCs successful' + bcolors.ENDC) 
        except Exception as e:
            print(bcolors.FAIL+f'ERROR: {e}'+bcolors.ENDC)
    else:        
    
        print(bcolors.OKCYAN+'Par_tx_slc creating new SLC file'+bcolors.ENDC)
        # par_TX_SLC is the interface between TerraSAR-X complex SSC data in a format developed by DLR and the GAMMA software. 
        pg.par_TX_SLC(date_xml,
                    date_cos,
                    os.path.join(slc_dir,date,date+'.slc.par'),
                    os.path.join(slc_dir,date,date+'.slc'))	
        
        # Open parameter file associated with each slc    


    return print(bcolors.OKGREEN + 'Single SLC successful' + bcolors.ENDC)
    



def parse_dem_ers_file(filepath):

    with open(filepath, 'r') as file:
        data = {}
        current_section = data
        section_stack = []
        
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):  # skip empty lines and comments
                continue
            
            if " Begin" in line:
                section_name = line.replace(" Begin", "").strip()
                new_section = {}
                current_section[section_name] = new_section
                section_stack.append(current_section)
                current_section = new_section
            elif " End" in line:
                current_section = section_stack.pop()
            else:
                if "=" in line:
                    key, value = map(str.strip, line.split("=", 1))
                    current_section[key] = value.strip('"')

    dem_ers_dict = data['DatasetHeader']
    ncells = int(dem_ers_dict['RasterInfo']['NrOfCellsPerLine'])#run_command(f"grep NrOfCellsPerLine {topdir}/dem/{dem}.dem.ers | awk '{{print $3}}'").strip()
    nlines = int(dem_ers_dict['RasterInfo']['NrOfLines'])#run_command(f"grep NrOfLines {topdir}/dem/{dem}.dem.ers | awk '{{print $3}}'").strip()
    xdim = float(dem_ers_dict['RasterInfo']['CellInfo']['Xdimension'])#run_command(f"grep Xdimension {topdir}/dem/{dem}.dem.ers | awk '{{printf \"%.11f\\n\", $3}}'").strip()
    ydim = float(dem_ers_dict['RasterInfo']['CellInfo']['Ydimension'])#run_command(f"grep Ydimension {topdir}/dem/{dem}.dem.ers | awk '{{printf \"%.11f\\n\", -$3}}'").strip()
    west = float(dem_ers_dict['RasterInfo']['RegistrationCoord']['Eastings'])#run_command(f"grep Eastings {topdir}/dem/{dem}.dem.ers | awk '{{printf \"%.11f\\n\", $3}}'").strip()
    north = float(dem_ers_dict['RasterInfo']['RegistrationCoord']['Northings'])#run_command(f"grep Northings {topdir}/dem/{dem}.dem.ers | awk '{{print $3}}'").strip()

    output_list = [ncells,nlines,xdim,ydim,west,north]

    return data, output_list


def plot_png(fp, radar=False, ax=None):
    if radar:
        if ax is None:
            plt.figure(figsize=(10, 10))
            plt.ion()
            img = plt.imread(fp)
            plt.imshow(img)
            plt.gca().invert_yaxis()
            plt.xlabel('Range')
            plt.ylabel('Azimuth')
            plt.show()
        else:
            img = plt.imread(fp)
            ax.imshow(img)
            ax.invert_yaxis()
            ax.set_xlabel('Range')
            ax.set_ylabel('Azimuth')
    else:
        if ax is None:
            plt.figure(figsize=(10, 10))
            plt.ion()
            img = plt.imread(fp)
            plt.imshow(img)
            plt.xlabel('East-West')
            plt.ylabel('North-South')
            plt.show()
        else:
            img = plt.imread(fp)
            ax.imshow(img)
            ax.set_xlabel('East-West')
            ax.set_ylabel('North-South')
def produce_geocode_hgt(
    master_date,
    mli_par_file,
    dem_par_file,
    slc_directory,
    optional_input_file=None,
    raspixavr=1,
    raspixavaz=1
):
    """
    Python version of produce_geocode_hgt.sh.
    Args:
        master_date (str): e.g. '20150708'
        mli_par_file (str): Path to MLI parameter file
        dem_par_file (str): Path to DEM parameter file
        slc_directory (str): Directory to operate in
        optional_input_file (str, optional): Optional input file
        raspixavr (int, optional): Value for rashgt (default 1)
        raspixavaz (int, optional): Value for rashgt (default 1)
    """
    # Change to SLC directory
    if not os.path.isdir(slc_directory):
        raise FileNotFoundError(f"SLC directory does not exist: {slc_directory}")
    os.chdir(slc_directory)

    dateM = f"{master_date}M"

    # Extract width from DEM parameter file
    widthdem = None
    with open(dem_par_file) as f:
        for line in f:
            if line.startswith("width:"):
                widthdem = int(line.split()[1])
            if line.startswith("width:"):    
                break

    if widthdem is None:
        raise ValueError("Could not find 'width:' in DEM parameter file.")

    # Extract range_samples from MLI parameter file
    widthmli = None
    lengthmli = None
    with open(mli_par_file) as f:
        for line in f:
            if line.startswith("range_samples:"):
                widthmli = int(line.split()[1])

            if line.startswith("azimuth_lines:"):
                lengthmli = int(line.split()[1])
            #if widthmli and lengthmli not eqaul to none then break
            if widthmli is not None and lengthmli is not None:
                break

    if widthmli is None:
        raise ValueError("Could not find 'range_samples:' in MLI parameter file.")

    print(f"DEM width: {widthdem}")
    print(f"MLI width (range samples): {widthmli}")

    # Output TIF of DEM
    pg.rashgt(f"{dateM}.hgt", "-", widthmli, "-", "-", "-", 1, 1, "-", 1.0, 0.35, "-", f"{dateM}.hgt.tif")

    # Geocode back DEM
    pg.geocode_back(f"{dateM}.hgt", widthmli, f"{dateM}.lt_fine", f"{dateM}.hgt.geo", widthdem, "-", 0, 0)

    # Output TIF of geocoded DEM
    pg.rashgt(f"{dateM}.hgt.geo", "-", widthdem, "-", "-", "-", raspixavr, raspixavaz, "-", 1.0, 0.35, "-", f"{dateM}.hgt.geo.tif")

    pg.data2geotiff(dem_par_file, f"{dateM}.hgt.geo", 2, f"{dateM}.hgt.geotiff.tif")

    # If optional input file is given, run rashgt again with it
    if optional_input_file and optional_input_file != slc_directory:
        print(f"Running rashgt with optional input file: {optional_input_file}")
        pg.rashgt(f"{dateM}.hgt.geo", optional_input_file, widthdem, "-", "-", "-", 1, 1, "-", 1.0, 0.35, "-", f"{dateM}.mli.hgt.geo.tif")

def produce_lookvectors(config):

    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = os.path.join(topdir,'slcs')

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    lengthdem = int(dem_par.get_value('nlines'))

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]

    geodir = os.path.join(topdir,'geo')
    # make the geodir
    if not os.path.exists(geodir):
        os.makedirs(geodir)

    slcMdir = os.path.join(topdir,'slcs',f'{dateM}M')
    slcMpar = os.path.join(slcMdir,f'{dateM}'+'.slc.par')

    u = os.path.join(topdir,'geo','u')
    #orientation angle of n 
    v = os.path.join(topdir,'geo','v')
    #local incidence angle
    inc = os.path.join(topdir,'geo','inc')
    #projection angle
    psi = os.path.join(topdir,'geo','psi')
    #pixel area normalization factor
    pix = os.path.join(topdir,'geo','pix')
    #layover and shadow map
    lsmap = os.path.join(topdir,'geo','ls_map')

    pg.gc_map(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'), #  MLI_par         (input) ISP MLI or SLC image parameter file (slant range geometry)
                '-', 
                os.path.join(f'{topdir}/dem/{dem}.swap.dem_par'), 
                os.path.join(f'{topdir}/dem/{dem}.swap.dem'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem_par'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt'), 
                demlat, 
                demlon, 
                os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.sim_sar'),
                u,
                v,
                inc,
                psi,
                pix,
                lsmap,
                '8',
                '2',
                '')



    [width, length] = [widthmli,lengthmli]
    offpar = '-'

    [demwidth, demlength] =[widthdem,lengthdem]


    dem = os.path.join(slcMdir,'P.dem')
    theta = os.path.join(geodir,'theta')
    phi = os.path.join(geodir,'phi')
    lutfile = os.path.join(slcMdir,f'{dateM}M'+'.lt_fine')
    dempar = os.path.join(slc_dir,f'{dateM}M','P.dem_par')
    dem_par = pg.ParFile(dempar)	
    widthdem=int(dem_par.get_value('width'))
    lengthdem = int(dem_par.get_value('nlines'))



    pg.look_vector(slcMpar,offpar,os.path.join(slc_dir,f'{dateM}M','P.dem_par'),dem,theta,phi)

    pg.geocode(lutfile,theta,demwidth,theta+'.rc',width,length,0,0)

    pg.geocode(lutfile,phi,demwidth,phi+'.rc',width,length,0,0)

    thetarc = np.fromfile(theta+'.rc',dtype=np.float32).byteswap().reshape((int(length),int(width)))
    nanix = thetarc == 0
    thetarc[nanix] = np.nan
    phirc = np.fromfile(phi+'.rc',dtype=np.float32).byteswap().reshape((int(length),int(width)))
    phirc[nanix] = np.nan
    U = np.sin(thetarc)
    E = np.cos(phirc)*np.cos(thetarc)
    N = np.sin(phirc)*np.cos(thetarc)

    U[nanix] = 0
    E[nanix] = 0
    N[nanix] = 0
    U.byteswap().tofile(os.path.join(geodir,'U'))
    E.byteswap().tofile(os.path.join(geodir,'E'))
    N.byteswap().tofile(os.path.join(geodir,'N'))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'E')))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'N')))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'U')))
    os.remove(theta)
    os.remove(theta+'.rc')
    os.remove(phi)
    os.remove(phi+'.rc')


    lat=float(dem_par.get_value('corner_lat')[0])#`awk '$1 == "corner_lat:" {print $2}' ${procdir}/geo/EQA.dem_par`
    lon=float(dem_par.get_value('corner_lon')[0])#`awk '$1 == "corner_lon:" {print $2}' ${procdir}/geo/EQA.dem_par`
    latstep=float(dem_par.get_value('post_lat')[0])#`awk '$1 == "post_lat:" {print $2}' ${procdir}/geo/EQA.dem_par`
    lonstep=float(dem_par.get_value('post_lon')[0])#`awk '$1 == "post_lon:" {print $2}' ${procdir}/geo/EQA.dem_par`
    length_dem=int(dem_par.get_value('nlines')) #`awk '$1 == "nlines:" {print $2}' ${procdir}/geo/EQA.dem_par`
    width_dem=int(dem_par.get_value('width'))#`awk '$1 == "width:" {print $2}' ${procdir}/geo/EQA.dem_par`
    reducfac_dem = max(1, width_dem // 2000)

    lat1 = float(lat) + float(latstep) * (length_dem - 1)  # Subtract one because width starts at zero

    lon1 = float(lon) + float(lonstep) * (width_dem - 1)
    latstep = abs(float(latstep))
    lonstep = abs(float(lonstep))

    # Because no wavelength is reported in master.rmli.par file, we calculated here according to the radar frequency (IN CENTIMETERS)
    # Frequency = (C / Wavelength), Where: Frequency: Frequency of the wave in hertz (hz). C: Speed of light (29,979,245,800 cm/sec (3 x 10^10 approx))
    radar_frequency = float(dateM_mli_par.get_value('radar_frequency')[0])
    wavelength = 29979245800 / radar_frequency


    print("   Geocoding results for lookangles." )
    #psi and incidence

    if os.path.exists(psi):
        pg.geocode_back(psi, width_dem, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.psi'), width_dem, length_dem, 1, 0)
        # pg.data2geotiff(dem_par, os.path.join(geodir, f'{dateM}M.geo.psi'), 2, os.path.join(geodir, f'{dateM}M.geo.psi.tif'), 0.0)

    if os.path.exists(inc):
        pg.geocode_back(inc, width_dem, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.inc'), width_dem, length_dem, 1, 0)
        # pg.data2geotiff(dem_par, os.path.join(geodir, f'{dateM}M.geo.inc'), 2, os.path.join(geodir, f'{dateM}M.geo.inc.tif'), 0.0)

    # E-N-U
    if os.path.exists(os.path.join(geodir, 'E')):
        pg.geocode_back(os.path.join(geodir, 'E'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.E'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.E'), 2, os.path.join(geodir, f'{dateM}M.geo.E.tif'), 0.0)

    if os.path.exists(os.path.join(geodir, 'N')):
        pg.geocode_back(os.path.join(geodir, 'N'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.N'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.N'), 2, os.path.join(geodir, f'{dateM}M.geo.N.tif'), 0.0)

    if os.path.exists(os.path.join(geodir, 'U')):
        pg.geocode_back(os.path.join(geodir, 'U'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.U'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.U'), 2, os.path.join(geodir, f'{dateM}M.geo.U.tif'), 0.0)

    #hgt - not a 'look angle', but useful for LiCSBAS etc
    print('HGT file geocoding')
    if os.path.exists(os.path.join(slcMdir, f'{dateM}M.hgt')):
        print(f"Geocoding {dateM}M.hgt file")
        pg.geocode_back(os.path.join(slcMdir, f'{dateM}M.hgt'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.hgt'), width_dem, length_dem, 1, 0)
        print('Finished geocoding hgt file')
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.hgt'), 2, os.path.join(geodir, f'{dateM}M.geo.hgt.tif'), 0.0)
    
    # geocode back mli

    pg.geocode_back(os.path.join(slcMdir,f'{dateM}.mli'),
                        widthmli,
                        os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt_fine'),
                        os.path.join(slcMdir,f'{dateM}.geo.mli'),
                        widthdem, '-', 2, 0)
    pg.data2geotiff(dempar, os.path.join(slcMdir,f'{dateM}.geo.mli'), 2, os.path.join(slcMdir,f'{dateM}.geo.mli.tif'), 0.0)
    # use pg.SLC_ovr to over sample the rslc
    if os.path.exists(os.path.join(slcMdir, f'{dateM}.hgt')):
        pg.geocode_back(os.path.join(slcMdir, f'{dateM}.hgt'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.hgt'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.hgt'), 2, os.path.join(geodir, f'{dateM}M.geo.hgt.tif'), 0.0)

    return



def produce_lookvectors_gcmap2(config):

    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = os.path.join(topdir,'slcs')

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    lengthdem = int(dem_par.get_value('nlines'))

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]

    geodir = os.path.join(topdir,'geo')
    # make the geodir
    if not os.path.exists(geodir):
        os.makedirs(geodir)

    slcMdir = os.path.join(topdir,'slcs',f'{dateM}M')
    slcMpar = os.path.join(slcMdir,f'{dateM}'+'.slc.par')

    u = os.path.join(topdir,'geo','u')
    #orientation angle of n 
    v = os.path.join(topdir,'geo','v')
    #local incidence angle
    inc = os.path.join(topdir,'geo','inc')
    #projection angle
    psi = os.path.join(topdir,'geo','psi')
    #pixel area normalization factor
    pix = os.path.join(topdir,'geo','pix')
    #layover and shadow map
    lsmap = os.path.join(topdir,'geo','ls_map')

    pg.gc_map2(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'), #  MLI_par         (input) ISP MLI or SLC image parameter file (slant range geometry)
                os.path.join(f'{topdir}/dem/{dem}.swap.dem_par'), 
                os.path.join(f'{topdir}/dem/{dem}.swap.dem'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem_par'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem'), 
                os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt'), 
                demlat, 
                demlon, 
                lsmap,
                lsmap+'.rc',
                inc,
                '-',
                '-',
                os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.sim_sar'),
                u,
                v,
                psi,
                pix,
                '-',
                '-',
                0,
                8,
                '-',
                '-',
                '-')



    [width, length] = [widthmli,lengthmli]
    offpar = '-'

    [demwidth, demlength] =[widthdem,lengthdem]


    dem = os.path.join(slcMdir,'P.dem')
    theta = os.path.join(geodir,'theta')
    phi = os.path.join(geodir,'phi')
    lutfile = os.path.join(slcMdir,f'{dateM}M'+'.lt_fine')
    dempar = os.path.join(slc_dir,f'{dateM}M','P.dem_par')
    dem_par = pg.ParFile(dempar)	
    widthdem=int(dem_par.get_value('width'))
    lengthdem = int(dem_par.get_value('nlines'))



    pg.look_vector(slcMpar,offpar,os.path.join(slc_dir,f'{dateM}M','P.dem_par'),dem,theta,phi)

    pg.geocode(lutfile,theta,demwidth,theta+'.rc',width,length,0,0)

    pg.geocode(lutfile,phi,demwidth,phi+'.rc',width,length,0,0)

    thetarc = np.fromfile(theta+'.rc',dtype=np.float32).byteswap().reshape((int(length),int(width)))
    nanix = thetarc == 0
    thetarc[nanix] = np.nan
    phirc = np.fromfile(phi+'.rc',dtype=np.float32).byteswap().reshape((int(length),int(width)))
    phirc[nanix] = np.nan
    U = np.sin(thetarc)
    E = np.cos(phirc)*np.cos(thetarc)
    N = np.sin(phirc)*np.cos(thetarc)

    U[nanix] = 0
    E[nanix] = 0
    N[nanix] = 0
    U.byteswap().tofile(os.path.join(geodir,'U'))
    E.byteswap().tofile(os.path.join(geodir,'E'))
    N.byteswap().tofile(os.path.join(geodir,'N'))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'E')))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'N')))
    os.system('chmod 777 {0}'.format(os.path.join(geodir,'U')))
    os.remove(theta)
    os.remove(theta+'.rc')
    os.remove(phi)
    os.remove(phi+'.rc')


    lat=float(dem_par.get_value('corner_lat')[0])#`awk '$1 == "corner_lat:" {print $2}' ${procdir}/geo/EQA.dem_par`
    lon=float(dem_par.get_value('corner_lon')[0])#`awk '$1 == "corner_lon:" {print $2}' ${procdir}/geo/EQA.dem_par`
    latstep=float(dem_par.get_value('post_lat')[0])#`awk '$1 == "post_lat:" {print $2}' ${procdir}/geo/EQA.dem_par`
    lonstep=float(dem_par.get_value('post_lon')[0])#`awk '$1 == "post_lon:" {print $2}' ${procdir}/geo/EQA.dem_par`
    length_dem=int(dem_par.get_value('nlines')) #`awk '$1 == "nlines:" {print $2}' ${procdir}/geo/EQA.dem_par`
    width_dem=int(dem_par.get_value('width'))#`awk '$1 == "width:" {print $2}' ${procdir}/geo/EQA.dem_par`
    reducfac_dem = max(1, width_dem // 2000)

    lat1 = float(lat) + float(latstep) * (length_dem - 1)  # Subtract one because width starts at zero

    lon1 = float(lon) + float(lonstep) * (width_dem - 1)
    latstep = abs(float(latstep))
    lonstep = abs(float(lonstep))

    # Because no wavelength is reported in master.rmli.par file, we calculated here according to the radar frequency (IN CENTIMETERS)
    # Frequency = (C / Wavelength), Where: Frequency: Frequency of the wave in hertz (hz). C: Speed of light (29,979,245,800 cm/sec (3 x 10^10 approx))
    radar_frequency = float(dateM_mli_par.get_value('radar_frequency')[0])
    wavelength = 29979245800 / radar_frequency


    print("   Geocoding results for lookangles." )
    #psi and incidence

    if os.path.exists(psi):
        pg.geocode_back(psi, width_dem, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.psi'), width_dem, length_dem, 1, 0)
        # pg.data2geotiff(dem_par, os.path.join(geodir, f'{dateM}M.geo.psi'), 2, os.path.join(geodir, f'{dateM}M.geo.psi.tif'), 0.0)

    if os.path.exists(inc):
        pg.geocode_back(inc, width_dem, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.inc'), width_dem, length_dem, 1, 0)
        # pg.data2geotiff(dem_par, os.path.join(geodir, f'{dateM}M.geo.inc'), 2, os.path.join(geodir, f'{dateM}M.geo.inc.tif'), 0.0)

    # E-N-U
    if os.path.exists(os.path.join(geodir, 'E')):
        pg.geocode_back(os.path.join(geodir, 'E'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.E'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.E'), 2, os.path.join(geodir, f'{dateM}M.geo.E.tif'), 0.0)

    if os.path.exists(os.path.join(geodir, 'N')):
        pg.geocode_back(os.path.join(geodir, 'N'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.N'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.N'), 2, os.path.join(geodir, f'{dateM}M.geo.N.tif'), 0.0)

    if os.path.exists(os.path.join(geodir, 'U')):
        pg.geocode_back(os.path.join(geodir, 'U'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.U'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.U'), 2, os.path.join(geodir, f'{dateM}M.geo.U.tif'), 0.0)

    #hgt - not a 'look angle', but useful for LiCSBAS etc
    print('HGT file geocoding')
    if os.path.exists(os.path.join(slcMdir, f'{dateM}M.hgt')):
        print(f"Geocoding {dateM}M.hgt file")
        pg.geocode_back(os.path.join(slcMdir, f'{dateM}M.hgt'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.hgt'), width_dem, length_dem, 1, 0)
        print('Finished geocoding hgt file')
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.hgt'), 2, os.path.join(geodir, f'{dateM}M.geo.hgt.tif'), 0.0)
    
    # geocode back mli

    pg.geocode_back(os.path.join(slcMdir,f'{dateM}.mli'),
                        widthmli,
                        os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt_fine'),
                        os.path.join(slcMdir,f'{dateM}.geo.mli'),
                        widthdem, '-', 2, 0)
    pg.data2geotiff(dempar, os.path.join(slcMdir,f'{dateM}.geo.mli'), 2, os.path.join(slcMdir,f'{dateM}.geo.mli.tif'), 0.0)
    # use pg.SLC_ovr to over sample the rslc
    if os.path.exists(os.path.join(slcMdir, f'{dateM}.hgt')):
        pg.geocode_back(os.path.join(slcMdir, f'{dateM}.hgt'), width, os.path.join(slcMdir, f'{dateM}M.lt_fine'), os.path.join(geodir, f'{dateM}M.geo.hgt'), width_dem, length_dem, 1, 0)
        pg.data2geotiff(dempar, os.path.join(geodir, f'{dateM}M.geo.hgt'), 2, os.path.join(geodir, f'{dateM}M.geo.hgt.tif'), 0.0)

    return


def dem_to_master(config):
    
    # Sort DEM
    #----------------------------------------------------------------------------------#
    print(bcolors.OKBLUE+"Generating DEM files and lookup tables \033[0m"+bcolors.ENDC)
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config['slc_dir'] 
    dim_dir = config['dim_dir'] 
    og_dem_dir = config['og_dem_dir'] 
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    cleanup = config["cleanup"]

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    os.chdir(topdir)
    # Assign variables in config to be used in future functions 
    config['lengthmli'] = lengthmli
    config['widthmli'] = widthmli

    dem_dir = os.path.join(topdir, 'dem')
    if not os.path.exists(dem_dir):
        os.mkdir(dem_dir)
    else:
        print(bcolors.WARNING + f"DEM directory already exists at {dem_dir}. Skipping DEM generation." + bcolors.ENDC)
        dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
        widthdem=int(dem_par.get_value('width'))

        config['widthdem'] = widthdem
        return config

    os.chdir(dem_dir)

    for file in glob(os.path.join(og_dem_dir,'*',f'{dem}*')):
        if os.path.exists(os.path.join(topdir,'dem',file.split('/')[-1])):
            print(bcolors.WARNING +f'No sym link for {file}, file already exists' +bcolors.ENDC)
        else:
            print(bcolors.OKBLUE +f'sym link for {file}' +bcolors.ENDC)
            os.symlink(file,os.path.join(topdir,'dem',file.split('/')[-1]))

    print(f"Oversampling DEM {dem} by factor of {demlat} in Latitude and {demlon} in Longitude")

    # Get DEM sizes
    dem_ers_dict,[ncells,nlines,xdim,ydim,west,north] = parse_dem_ers_file(f'{topdir}/dem/{dem}.dem.ers')

    print('no. of cells: ',ncells,', nlines: ',nlines,', xdim: ', xdim, 'ydim: ',ydim, ', west: ',west,', North:', north)
    if None in [ncells, nlines, xdim, ydim, west, north]:sys.exit()

    # 2022 Update way to import DEM and apply geoid correction so relative to ellipsoid
    dem_import_dict = {'input_dem':os.path.abspath(f'{topdir}/dem/{dem}.tif'),
                'bin_dem':f'{topdir}/dem/{dem}.swap.dem',
                'dem_par':f'{topdir}/dem/{dem}.swap.dem_par',
                'input_type':0, # 0: GeoTIFF / GDAL supported raster format (default)
                'priority':1,
                'geoid': f"$DIFF_HOME/scripts/egm2008-5.dem",
                'geoid_par':f"$DIFF_HOME/scripts/egm2008-5.dem_par", 
                'geoid_type':0}

    # 2022 Update way to import DEM and apply geoid correction so relative to ellipsoid
    # dem_import $topdir/dem/$dem.tif $dem.swap.dem $dem.swap.dem_par 0 1 /apps/applications/gamma/$gammaver/2/default/DIFF/scripts/egm2008-5.dem /apps/applications/gamma/$gammaver/2/default/DIFF/scripts/egm2008-5.dem_par 0

    print(bcolors.OKBLUE+'Using py_gamma: pg.dem_import'+ bcolors.ENDC)
    pg.dem_import(dem_import_dict.get('input_dem'),#(input) input DEM in original format
                dem_import_dict.get('bin_dem'),#(output) DEM in binary format (float, enter - for none)
                dem_import_dict.get('dem_par'),#DEM_par     (input/output) DEM parameter file corresponding to output DEM
                dem_import_dict.get('input_type'),
                dem_import_dict.get('priority'),
                dem_import_dict.get('geoid'),
                dem_import_dict.get('geoid_par'),
                dem_import_dict.get('geoid_type'))

     # Look-up table
    print(bcolors.OKBLUE +' pg.gc_map() '+bcolors.ENDC)
    #----------------------------------------------------------------------------------#
    pg.gc_map(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'), #  MLI_par         (input) ISP MLI or SLC image parameter file (slant range geometry)
              '-', 
              os.path.join(topdir,'dem',dem_import_dict['dem_par']), 
              os.path.join(topdir,'dem',dem_import_dict['bin_dem']), 
              os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem_par'), 
              os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem'), 
              os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt'), 
              demlat, 
              demlon, 
              os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.sim_sar'),
              os.path.join(topdir,'slcs',f'{dateM}M','u'),
              os.path.join(topdir,'slcs',f'{dateM}M','v'),
              os.path.join(topdir,'slcs',f'{dateM}M','inc'),
              os.path.join(topdir,'slcs',f'{dateM}M','psi')
              )


    # Open parameter file    
    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))

    config['widthdem'] = widthdem
    pg.rasmph(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.sim_sar'),widthdem , '-', '-', '-', '-')

    
    pg.create_diff_par(os.path.join(slc_dir,f'{dateM}M',f'{dateM}.mli.par'),
                       '-', 
                       os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.diff_par'),
                       1,
                       0)
    
    #Geocoding lookup table correction using offset polynomials from the DIFF parameter file
    
    pg.gc_map_fine(os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.lt'), #geocoding lookup table
                   widthdem, #width of lookup table (samples)
                   os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.diff_par'), #DIFF/GEO parameter file containing fine registration polynomial coefficients
                   os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.lt_fine'), # (output) refined geocoding lookup table
                   1) #1: simulated image reference (default)


    
    # Forward transformation with a geocoding look-up table. For each image point defined in 
    # coordinate system A, the lookup table contains the corresponding coordinates in system B. 
    # The program geocode is used to resample the data in coordinate system A into the coordinates of system B.
    print(
        f"DEM width (widthdem): {widthdem}, "
        f"MLI width (widthmli): {widthmli}, "
        f"MLI length (lengthmli): {lengthmli}"
    )
    
    pg.geocode(os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.lt_fine'),  #      lookup_table  (input) lookup table containing pairs of real-valued output data coordinates
               os.path.join(slc_dir,f'{dateM}M','P.dem'),             #   data_in   (input) data file (format as specified by format_flag parameter)
               widthdem,            #   width_in  width of input data file and gc_map lookup table
               os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.hgt'),      #   data_out  (output) output data file
               widthmli,            #   width_out width of output data file
               lengthmli,                 #lengthmli,
               2,                    
               0)                  
    
    pg.geocode(os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.lt_fine'),  #      lookup_table  (input) lookup table containing pairs of real-valued output data coordinates
               os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.sim_sar'),             #   data_in   (input) data file (format as specified by format_flag parameter)
               widthdem,            #   width_in  width of input data file and gc_map lookup table
               os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.sim_sar.sar'),      #   data_out  (output) output data file
               widthmli,            #   width_out width of output data file
               lengthmli,                 #lengthmli,
               2,                   
               0)   
    pg.geocode(os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.lt_fine'),  #      lookup_table  (input) lookup table containing pairs of real-valued output data coordinates
               os.path.join(slc_dir,f'{dateM}M','P.dem'),             #   data_in   (input) data file (format as specified by format_flag parameter)
               widthdem,            #   width_in  width of input data file and gc_map lookup table
               os.path.join(slc_dir,f'{dateM}M',f'{dateM}M.hgt_no_ovr'),      #   data_out  (output) output data file
               widthmli,            #   width_out width of output data file
               lengthmli,                 #lengthmli,
               2,                   
               0)      
    produce_geocode_hgt(dateM,os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'),os.path.join(topdir,'slcs',f'{dateM}M',f'P.dem_par'),os.path.join(topdir,'slcs',f'{dateM}M'),os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli'))
    
    if cleanup:
        im_fp = os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.lt_fine')
        im_tif_fp = os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.lt_fine.tif')
        im_png_fp = os.path.join(topdir,'slcs',f'{dateM}M/{dateM}M.lt_fine.png')
        im_width = widthdem

        pg.rasmph_pwr24(im_fp, os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli'),im_width,  1, 1, 0, 1, 1, 0.8, .35, 1, im_tif_fp)
        #pg.rasmph(im_fp,im_width,'-',rlks,azlks,0.5,'-','-',im_tif_fp,'-')
        print(bcolors.OKGREEN,'5. Look-up table fine IMAGE PRINT: ',im_png_fp,bcolors.ENDC)
        pg.run_cmd('convert', im_tif_fp, '-transparent', 'black', im_png_fp)
        

        



    os.chdir(topdir)



    return config


def proc_master_slc_S1(config):
    
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config['slc_dir'] 
    os.chdir(topdir)

    if not os.path.exists(slc_dir):
        os.makedirs(slc_dir)

    safe_to_slc(dateM, config)

    # Create master date folder to be used as non-master date
    # pg.multi_look(os.path.join(slc_dir,f'{dateM}/{dateM}.slc'),     #input slc
    #              os.path.join(slc_dir,f'{dateM}/{dateM}.slc.par'), #input par
    #              os.path.join(slc_dir,f'{dateM}/{dateM}.mli'),     # output mli
    #              os.path.join(slc_dir,f'{dateM}/{dateM}.mli.par'), #output par
    #              config["rlks"], config["azlks"]) 
    
    # Copy slc_dir/{dateM} directory to slc_dir/{dateM}M  and use as master date
    dateMM = f"{dateM}M"
    src_dir = os.path.join(slc_dir, dateM)
    dst_dir = os.path.join(slc_dir, dateMM)

    if os.path.exists(dst_dir):
        print(bcolors.WARNING + f"Directory {dst_dir} already exists. Skipping copy." + bcolors.ENDC)
    else:
        shutil.copytree(src_dir, dst_dir)
        print(bcolors.OKGREEN + f"Copied {src_dir} to {dst_dir}" + bcolors.ENDC)

    return print(bcolors.OKGREEN + 'Master SLC successfully' + bcolors.ENDC)


def proc_master_slc(config):
    
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config['slc_dir'] 
    os.chdir(topdir)

    if not os.path.exists(slc_dir):
        os.makedirs(slc_dir)

    dim_to_slc(dateM, config)

    # Create master date folder to be used as non-master date
    pg.multi_look(os.path.join(slc_dir,f'{dateM}/{dateM}.slc'),     #input slc
                 os.path.join(slc_dir,f'{dateM}/{dateM}.slc.par'), #input par
                 os.path.join(slc_dir,f'{dateM}/{dateM}.mli'),     # output mli
                 os.path.join(slc_dir,f'{dateM}/{dateM}.mli.par'), #output par
                 config["rlks"], config["azlks"]) 
    
    # Copy slc_dir/{dateM} directory to slc_dir/{dateM}M  and use as master date
    dateMM = f"{dateM}M"
    src_dir = os.path.join(slc_dir, dateM)
    dst_dir = os.path.join(slc_dir, dateMM)

    if os.path.exists(dst_dir):
        print(bcolors.WARNING + f"Directory {dst_dir} already exists. Skipping copy." + bcolors.ENDC)
    else:
        shutil.copytree(src_dir, dst_dir)
        print(bcolors.OKGREEN + f"Copied {src_dir} to {dst_dir}" + bcolors.ENDC)

    return print(bcolors.OKGREEN + 'Master SLC successfully' + bcolors.ENDC)


def check_orbit_direction(date,config):
    topdir = config['topdir']
    slc_dir = config['slc_dir']
    dateM = config['dateM']
    asc_desc_file = os.path.join(topdir, config['orbit_dir_file'])
    date_h = None


    dateM_param = pg.ParFile(os.path.join(slc_dir,f'{dateM}/{dateM}.slc.par'))
    dateM_h = float(dateM_param.get_value('heading')[0])
   
    if os.path.exists(os.path.join(topdir,asc_desc_file)):
        print('Checking to see if dates are within 90 degrees of each other')
        with open(asc_desc_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if date in line:
                    date_h = float(line.split(' ')[1])
    else:
        
        with open(os.path.join(topdir,asc_desc_file), 'a+') as f:
            f.write(f'{dateM} {dateM_h}\n')

    

               
   
    # if more than 1 of date1 date2 dateM is not none
    if date_h is not None:
        if not within_90_degrees(date_h, dateM_h):
            print(bcolors.WARNING+ "Heading angles are not within 90 degrees of each other."+bcolors.ENDC)
            orbit_dir = False
        else:
            orbit_dir = True
    else:
        orbit_dir = None


    return orbit_dir


def dev_proc_slc_to_rslc(date, config):


    print(f"Processing SLC to RSLC for date: {date}")
    # Assign variables
    rlks, azlks, dem, demlat, demlon = config["rlks"], config["azlks"], config["dem"], config["demlat"], config["demlon"]
    npat_r, npat_az, r_init, az_init = config["npat_r"], config["npat_az"], config["r_init"], config["az_init"]
    dateM, topdir, slc_dir, dim_dir = config['dateM'], config['topdir'], config["slc_dir"], config["dim_dir"]
    cleanup = config["cleanup"]
    
    slc_date_dir = os.path.join(slc_dir,date)
    slc_dateM_dir = os.path.join(slc_dir,dateM+'M')

    rslc_dateM_dir = os.path.join(topdir, 'rslc', f'{dateM}M')
    os.makedirs(rslc_dateM_dir, exist_ok=True)


    if os.path.exists(rslc_dateM_dir):
       
        pass
    else:
        shutil.copytree(slc_dateM_dir, rslc_dateM_dir)
            # Redirect stdout to a log file
        log_file = os.path.join(config['topdir'], f'proc_slc_to_rslc_{date}.log')
    os.makedirs(os.path.join(topdir, 'rslc'), exist_ok=True)

    rslc_dir = os.path.join(topdir, 'rslc')

    rslc_date_dir = os.path.join(rslc_dir, date)
    if os.path.exists(rslc_date_dir):
        print(f"Skipping SLC to RSLC for date: {date}")
        return 
    else:
        os.makedirs(rslc_date_dir, exist_ok=True)


    # Coregister SLC to reference SLC using SLC_coreg
    print(bcolors.OKBLUE + 'pg.SLC_coreg()' + bcolors.ENDC)
    # Define file paths
    slc_file = os.path.join(slc_date_dir, f'{date}.slc')
    slc_par_file = os.path.join(slc_date_dir, f'{date}.slc.par')
    rslc_file = os.path.join(rslc_date_dir, f'{date}.rslc')
    rslc_par_file = os.path.join(rslc_date_dir, f'{date}.rslc.par')
    rmli_file = os.path.join(rslc_date_dir, f'{date}.mli')
    rmli_par_file = os.path.join(rslc_date_dir, f'{date}.mli.par')
    ref_slc_file = os.path.join(slc_dateM_dir, f'{dateM}.slc')
    ref_slc_par_file = os.path.join(slc_dateM_dir, f'{dateM}.slc.par')
    hgt_file = os.path.join(slc_dateM_dir, f'{dateM}M.hgt')  # or provide a height map if available
   

    pg.SLC_coreg(
        slc_file,
        slc_par_file,
        rslc_file,
        rslc_par_file,
        rmli_file,
        rmli_par_file,
        ref_slc_file,
        ref_slc_par_file,
        hgt_file,
        rlks,
        azlks
    )


    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

   
    cleanup = config["cleanup"]

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    
    pg.geocode_back(os.path.join(rslc_dir,date,f'{date}.mli'),
                        widthmli, 
                        os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.lt_fine'), 
                        os.path.join(rslc_dir,date,f'{date}_geocode.mli'), 
                        widthdem, '-', 2, 0)
    # use pg.SLC_ovr to over sample the rslc 
    """usage: SLC_ovr <SLC> <SLC_par> <SLC_ovr> <SLC_ovr_par> [r_ovr] [az_ovr] [mode] [order]

    input parameters:
    SLC          (input) SLC image  (FCOMPLEX or SCOMPLEX format)
    SLC_par      (input) SLC image parameter file
    SLC_ovr      (output) oversampled SLC image
    SLC_ovr_par  (output) oversampled SLC image parameter file
    r_ovr        range oversampling factor (enter - for default: 1.0)
    az_ovr       azimuth oversampling factor (enter - for default: 1.0)
    mode         interpolation mode (enter - for default)
                    0: Lanczos interpolation (default)
                    1: B-spline interpolation
    order        Lanczos interpolator order / B-spline degree 4 -> 9 (enter - for default: 4)"""

    # print(bcolors.OKBLUE + 'pg.SLC_ovr()' + bcolors.ENDC)
    # pg.SLC_ovr(
    #     rslc_file,
    #     rslc_par_file,
    #     os.path.join(rslc_date_dir, f'{date}.rslc.ovr'),
    #     os.path.join(rslc_date_dir, f'{date}.rslc.ovr.par'),
    #     2,
    #     2,
    #     0,  # mode: 0 for Lanczos interpolation
    #     4   # order: 4 for Lanczos order
    # )

    # # change name of rslc to rslc.pre_over and change name of rslc.ovr to rslc
    # rslc_pre_over_file = os.path.join(rslc_date_dir, f'{date}.rslc.pre_over')
    # rslc_ovr_file = os.path.join(rslc_date_dir, f'{date}.rslc.ovr')
    # if os.path.exists(rslc_pre_over_file):
    #     os.remove(rslc_pre_over_file)
    # os.rename(rslc_file, rslc_pre_over_file)
    # rslc_pre_ovr__file = os.path.join(rslc_date_dir, f'{date}.rslc.pre_ovr.par')
    # os.rename(rslc_par_file, rslc_pre_ovr__file)
    # os.rename(os.path.join(rslc_date_dir, f'{date}.rslc.ovr'), rslc_file)
    # os.rename(os.path.join(rslc_date_dir, f'{date}.rslc.ovr.par'), rslc_par_file)


    return      

# def dev_geocode_reference_slc(date, config):

#     print(f"Running geocoding.py for master MLI: {date}")
#     dateM = config['dateM']
#     topdir = config['topdir']
#     slc_dir = config['slc_dir']

#     mli = os.path.join(slc_dir, f"{dateM}M", f"{dateM}.mli")
#     mli_par = os.path.join(slc_dir, f"{dateM}M", f"{dateM}.mli.par")
#     dem = os.path.join(slc_dir, f"{dateM}M", "P.dem")
#     dem_par = os.path.join(slc_dir, f"{dateM}M", "P.dem_par")
#     root_name = os.path.join(slc_dir, f"{dateM}M", f"{dateM}")

#     cmd = [
#         sys.executable,  # Use current python interpreter
#         "/nfs/a283/homes/ee16eme/py/tsx_if_processing_code/tsx_if_py/src/geocoding.py",
#         mli,
#         mli_par,
#         dem,
#         dem_par,
#         root_name
#     ]
#     print(" ".join(cmd))
#     subprocess.run(cmd, check=True)
#     return

def proc_slc_to_rslc(date, config):


    print(f"Processing SLC to RSLC for date: {date}")
    # Assign variables
    rlks, azlks, dem, demlat, demlon = config["rlks"], config["azlks"], config["dem"], config["demlat"], config["demlon"]
    npat_r, npat_az, r_init, az_init = config["npat_r"], config["npat_az"], config["r_init"], config["az_init"]
    dateM, topdir, slc_dir, dim_dir = config['dateM'], config['topdir'], config["slc_dir"], config["dim_dir"]
    cleanup = config["cleanup"]
    
    slc_date_dir = os.path.join(slc_dir,date)
    slc_dateM_dir = os.path.join(slc_dir,dateM+'M')

    rslc_dateM_dir = os.path.join(topdir, 'rslc', f'{dateM}M')
    os.makedirs(rslc_dateM_dir, exist_ok=True)


    if os.path.exists(rslc_dateM_dir):
       
        pass
    else:
        shutil.copytree(slc_dateM_dir, rslc_dateM_dir)
            # Redirect stdout to a log file
        log_file = os.path.join(config['topdir'], f'proc_slc_to_rslc_{date}.log')
    os.makedirs(os.path.join(topdir, 'rslc'), exist_ok=True)

    rslc_dir = os.path.join(topdir, 'rslc')
            
            

    rslc_date_dir = os.path.join(rslc_dir, date)
    if os.path.exists(rslc_date_dir):
        print(f"Skipping SLC to RSLC for date: {date}")
        return 
    else:
        os.makedirs(rslc_date_dir, exist_ok=True)

    log_file = os.path.join(config['topdir'], f'proc_slc_to_rslc_{date}.log')
    
    with open(log_file, 'a') as log:
        with redirect_stdout(log):
                    # Remove any files with substrings 'ccp', 'off', 'rslc'
          
            
            # look for files with *rslc* already in slc_date_dir folder and  retun if so 
            if len(glob(os.path.join(slc_date_dir,'*rslc*'))) > 0:
                print(bcolors.WARNING + f"Skipping {date} as rslc already exists"+bcolors.ENDC)
                return
            

            # Create offset parameter file using cross-correlation algorithm 
            print(bcolors.OKBLUE +' pg.create_offset() '+bcolors.ENDC)
            pg.create_offset(os.path.join(slc_dateM_dir,f'{dateM}.slc.par'),
                            os.path.join(slc_date_dir,f'{date}.slc.par'), 
                            os.path.join(slc_date_dir,f'{dateM}M_{date}.off'), 
                            1, # choice of algorithm
                            rlks, 
                            azlks, 
                            0) #interactive yes or no (no - 0)
            
            print(bcolors.OKBLUE +' pg.offset_pwr_tracking() '+bcolors.ENDC)
            #offset_pwr_tracking2 estimates the range and azimuth registration offset fields using cross correlation optimization of the detected SLC data
            # pg.offset_pwr_tracking(os.path.join(slc_dir,f'{dateM}M/{dateM}.slc'), # SLC1 (input) single-look complex image 1 (reference)
            #             os.path.join(slc_dir,f'{date}/{date}.slc'), # SLC2 (input) single-look complex image 2
            #             os.path.join(slc_dir,f'{dateM}M/{dateM}.slc.par'), # SLC1_par (input) SLC-1 ISP image parameter file
            #             os.path.join(slc_dir,f'{date}/{date}.slc.par'), # SLC2_par (input) SLC-2 ISP image parameter file
            #             os.path.join(slc_dir,f'{date}/{dateM}M_{date}.off'), # OFF_par (input) ISP offset/interferogram parameter file
            #             os.path.join(slc_dir,f'{date}/{dateM}M_{date}.offs'), # offs (output) offset estimates in range and azimuth (fcomplex)
            #             os.path.join(slc_dir,f'{date}/{dateM}M_{date}.ccp'), # ccp (output) cross-correlation of each patch (0.0->1.0) (float)
            #             '-', # rwin range patch size (range pixels, enter - for default from offset parameter file)
            #             '-', # azwin azimuth patch size (azimuth lines, enter - for default from offset parameter file)
            #             '-', # offsets (output) range and azimuth offsets and cross-correlation data in text format, enter - for no output
            #             '-', # n_ovr SLC oversampling factor (integer 2**N (1,2,4), enter - for default: 2)
            #             0.1, # thres cross-correlation threshold (0.0->1.0) (enter - for default from offset parameter file)
            #             '-', # rstep step in range pixels (enter - for default: rwin/2)
            #             '-', # azstep step in azimuth pixels (enter - for default: azwin/2)
            #             0, # rstart offset to starting range pixel (enter - for default: 0)
            #             '-', # rstop offset to ending range pixel (enter - for default: nr-1)
            #             0, # azstart offset to starting azimuth line (enter - for default: 0)
            #             '-', # azstop offset to ending azimuth line (enter - for default: nlines-1)
            #             5, # lanczos Lanczos interpolator order 5 -> 9 (enter - for default: 5)
            #             1.0, # bw_frac bandwidth fraction of low-pass filter on complex data (0.0->1.0) (enter - for default: 1.0)
            #             0, # deramp deramp SLC phase flag (enter - for default)
            #             1, # int_filt intensity low-pass filter flag (enter - for default)
            #             0, # pflag print flag (enter - for default)
            #             '-', # pltflg plotting flag (enter - for default)
            #             '-') # ccs (output) cross-correlation standard deviation of each patch (float)
            
            pg.offset_pwr(os.path.join(slc_dateM_dir, f'{dateM}.slc'),
                            os.path.join(slc_date_dir, f'{date}.slc'),
                            os.path.join(slc_dateM_dir, f'{dateM}.slc.par'),
                            os.path.join(slc_date_dir, f'{date}.slc.par'),
                            os.path.join(slc_date_dir, f'{dateM}M_{date}.off'),
                            os.path.join(slc_date_dir, f'{dateM}M_{date}.offs'),
                            os.path.join(slc_date_dir, f'{dateM}M_{date}.ccp'),
                            2048, 2048, '-', 1, 32,32 , 0.1, 5)
            

            
            print(bcolors.OKBLUE +' pg.offset_fit() '+bcolors.ENDC)
            #offset_fit computes range and azimuth registration offset polynomials from offsets estimated by offset_pwr
            pg.offset_fit(os.path.join(slc_date_dir,f'{dateM}M_{date}.offs'), #(input) range and azimuth offset estimates (fcomplex) (fcomplex)
                        os.path.join(slc_date_dir,f'{dateM}M_{date}.ccp'), # (input)  cross-correlation of each patch (float)
                        os.path.join(slc_date_dir,f'{dateM}M_{date}.off'), # (input) ISP offset/interferogram parameter file
                        '-', # (output) culled range and azimuth offset estimates (fcomplex, enter - for none)
                        '-', # (output) culled offset estimates and SNR values (text format, enter - for none)
                        0.1) # cross-correlation threshold  (default from OFF_par)   

            print(bcolors.OKBLUE +' pg.offset_trackingm() '+bcolors.ENDC)
            pg.run_cmd('offset_tracking', 
                        os.path.join(slc_date_dir, f'{dateM}M_{date}.offs'), 
                        os.path.join(slc_date_dir, f'{dateM}M_{date}.ccp'), 
                        os.path.join(slc_dateM_dir, f'{dateM}.slc.par'), 
                        os.path.join(slc_date_dir, f'{dateM}M_{date}.off'), 
                        os.path.join(slc_date_dir, 'disp_map'), 
                        os.path.join(slc_date_dir, 'disp_val'), 
                        '1', '0.1', '1')

            print(bcolors.OKBLUE +' pg.SLC_interp() '+bcolors.ENDC)
            # Uses range and azimuth offset function polynomials to resample slc 
            pg.SLC_interp( os.path.join(slc_dir,f'{date}/{date}.slc'), # image to be resampled to the geometry of the reference SLC-1 image 
                        os.path.join(slc_dir,f'{dateM}M/{dateM}.slc.par'), # SLC-1 ISP image parameter file (Master)
                        os.path.join(slc_dir,f'{date}/{date}.slc.par'), # SLC-2 ISP image parameter file (Slave)
                        os.path.join(slc_dir,f'{date}/{dateM}M_{date}.off'), #ISP offset/interferogram parameter file
                        os.path.join(rslc_dir,f'{date}/{date}.rslc'), # (output) SLC-2 resampled into the reference geometry of SLC-1 (fcomplex)
                        os.path.join(rslc_dir,f'{date}/{date}.rslc.par')) # (output) ISP image parameter file for resampled SLC-2R
            


            print('1')
            pg.create_offset(os.path.join(slc_dateM_dir, f'{dateM}.slc.par'),
                            os.path.join(rslc_date_dir, f'{date}.rslc.par'),
                            os.path.join(rslc_date_dir, f'{dateM}M_{date}.off1'),
                            1, rlks, azlks, 0)
            print('2')
            pg.offset_pwr(os.path.join(slc_dateM_dir, f'{dateM}.slc'),
                        os.path.join(rslc_date_dir, f'{date}.rslc'),
                        os.path.join(slc_dateM_dir, f'{dateM}.slc.par'),
                        os.path.join(rslc_date_dir, f'{date}.rslc.par'),
                        os.path.join(rslc_date_dir, f'{dateM}M_{date}.off1'),
                        os.path.join(rslc_date_dir, f'{dateM}M_{date}.offs1'),
                        os.path.join(rslc_date_dir, f'{dateM}M_{date}.ccp1'),
                        256/4, 64, '-', 2, 128,128 , 0.15, 5)


            print('3')

            pg.offset_fit(os.path.join(rslc_date_dir, f'{dateM}M_{date}.offs1'),
                        os.path.join(rslc_date_dir, f'{dateM}M_{date}.ccp1'),
                        os.path.join(rslc_date_dir, f'{dateM}M_{date}.off1'),
                        '-', '-', 0.1, 1, 0)
            
            # Test of Offset value to test for refinement in azimuth offset
            with open(os.path.join(rslc_date_dir, f'{dateM}M_{date}.off1'), 'r') as file:
                for line in file:
                    if 'azimuth_offset_polynomial' in line:
                        azimuth_offset = float(line.split()[1])
                        break
            print('azimuth_offset:', azimuth_offset)
            offtest = 1 if abs(azimuth_offset) < 0.01 else 0
            print('offtest:', offtest)
            if offtest == 0:

                print('WARNING: Azimuth offset is too large between date rslc1 and master slc . Refining azimuth offset.')
                # Add the offsets together
                pg.offset_add(os.path.join(slc_date_dir, f'{dateM}M_{date}.off'),
                            os.path.join(rslc_date_dir, f'{dateM}M_{date}.off1'),
                            os.path.join(rslc_date_dir, f'{dateM}M_{date}.off.totalcc'))
            else:
                shutil.copy(os.path.join(slc_date_dir, f'{dateM}M_{date}.off'),
                            os.path.join(rslc_date_dir, f'{dateM}M_{date}.off.totalcc'))
            print('4')
            pg.SLC_interp( os.path.join(slc_dir,f'{date}/{date}.slc'), # image to be resampled to the geometry of the reference SLC-1 image 
                        os.path.join(slc_dir,f'{dateM}M/{dateM}.slc.par'), # SLC-1 ISP image parameter file (Master)
                        os.path.join(slc_dir,f'{date}/{date}.slc.par'), # SLC-2 ISP image parameter file (Slave)
                        os.path.join(rslc_dir,f'{date}/{dateM}M_{date}.off.totalcc'), #ISP offset/interferogram parameter file
                        os.path.join(rslc_dir,f'{date}/{date}.rslc2'), # (output) SLC-2 resampled into the reference geometry of SLC-1 (fcomplex)
                        os.path.join(rslc_dir,f'{date}/{date}.rslc2.par')) # (output) ISP image parameter file for resampled SLC-2R
            

            # os.rename(os.path.join(rslc_date_dir, f'{date}.rslc2'),
            #         os.path.join(rslc_date_dir, f'{date}.rslc'))
            # os.rename(os.path.join(rslc_date_dir, f'{date}.rslc2.par'),
            #         os.path.join(rslc_date_dir, f'{date}.rslc.par'))
            
            os.rename(os.path.join(rslc_date_dir, f'{date}.rslc2'),os.path.join(rslc_date_dir, f'{date}.rslc'))
            os.rename(os.path.join(rslc_date_dir, f'{date}.rslc2.par'),os.path.join(rslc_date_dir, f'{date}.rslc.par'))

            pg.multi_look(os.path.join(rslc_dir,f'{date}/{date}.rslc'),# input slc image 
                            os.path.join(rslc_dir,f'{date}/{date}.rslc.par'), # input SLC processing parameter file
                            os.path.join(rslc_dir,f'{date}/{date}.rslc.mli'), # output mli
                            os.path.join(rslc_dir,f'{date}/{date}.rslc.mli.par'), # output mli param file 
                            rlks, azlks)
            # if cleanup:
            #     # Remove all files for rslc1 and rslc2
            #     for file in glob(os.path.join(rslc_date_dir, '*rslc1*')) + glob(os.path.join(rslc_date_dir, '*rslc2*')):
            #         os.remove(file)



    


def proc_if(date1,date2,config):


    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    
    # check if config has adf_unw_config 
    if "adf_filter" in config:
        adf_filter = config["adf_filter"]
    else:
        adf_filter = False

  

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

   
    cleanup = config["cleanup"]

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    
    if os.path.exists(os.path.join(topdir,'ifgms',f'{date1}-{date2}')):
        print(bcolors.WARNING + f"Directory {topdir}/ifgms/{date1}-{date2} already exists. Skipping processing." + bcolors.ENDC)
        return False
    
    os.makedirs(os.path.join(topdir,'ifgms',f'{date1}-{date2}'),exist_ok = True)
    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')
    rslc_dir = os.path.join(topdir,'rslc')
    
    file_list = []
    for pattern in [[f'{dateM}M','*.lt*'],[f'{dateM}M','*.mli*'], [f'{dateM}M','*.hgt'], [f'{dateM}M','P.*']]:
        print(bcolors.OKBLUE+f'{os.path.join(slc_dir,pattern[0],pattern[1])}'+bcolors.ENDC)
        for files in glob(os.path.join(slc_dir,pattern[0],pattern[1])):
            file_list.append(files)
    for pattern in [[date1,f'{date1}*.rslc*'],[date2,f'{date2}*.rslc*']]:
        print(bcolors.OKBLUE+f'{os.path.join(slc_dir,pattern[0],pattern[1])}'+bcolors.ENDC)
        for files in glob(os.path.join(rslc_dir,pattern[0],pattern[1])):
            file_list.append(files)
    
    for file in file_list:
        if os.path.exists(os.path.join(ifgm_dir,file.split('/')[-1])):
            print(bcolors.WARNING +f'No sym link for {file}, file already exists' +bcolors.ENDC)
       
        else:
            print(bcolors.OKBLUE +f'sym link for {file}' +bcolors.ENDC)
            os.symlink(file,os.path.join(ifgm_dir,file.split('/')[-1]))

        # pg.geocode(os.path.join(ifgm_dir,f'{dateM}M.lt_fine'),
        #            os.path.join(ifgm_dir,f'P.dem'),
        #            widthdem, 
        #            os.path.join(ifgm_dir,f'{dateM}M.hgt'),
        #            widthmli,lengthmli,2,0)
    
    pg.create_offset(os.path.join(ifgm_dir,f'{date1}.rslc.par'),
                     os.path.join(ifgm_dir,f'{date2}.rslc.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.off'),
                     1, rlks, azlks, 0)

    pg.phase_sim_orb(os.path.join(ifgm_dir,f'{date1}.rslc.par'),
                     os.path.join(ifgm_dir, f'{date2}.rslc.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.off'),
                     os.path.join(ifgm_dir, f'{dateM}M.hgt'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.sim_unw'),
                     os.path.join(slc_dir,f'{dateM}M', f'{dateM}.slc.par'),
                     '-', '-', 1, 1)

    pg.SLC_diff_intf(os.path.join(ifgm_dir,f'{date1}.rslc'),
                     os.path.join(ifgm_dir,f'{date2}.rslc'),
                     os.path.join(ifgm_dir,f'{date1}.rslc.par'),
                     os.path.join(ifgm_dir,f'{date2}.rslc.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.off'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.sim_unw'),
                     os.path.join(ifgm_dir, f'{date1}-{date2}.diff'),
                     rlks, azlks, 0, 0, 0.2, 1, 1)
    


      
    pg.base_init(os.path.join(ifgm_dir,f'{date2}.rslc.par'),
                    os.path.join(ifgm_dir,f'{date1}.rslc.par'), 
                    os.path.join(ifgm_dir,f'{date1}_{date2}.off'), 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.diff'), 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.base'), 0)
        
    #Computation of baseline components normal and parallel to look vector.       
    pg.rasmph_pwr(os.path.join(ifgm_dir,f'{date1}-{date2}.diff'), 
                  os.path.join(slc_dir,f'{dateM}M',f'{dateM}.mli'),
                  widthmli, 1, 1, 0, '-', '-', 1., .20, 1,
                  os.path.join(ifgm_dir,f'{date1}-{date2}.diff.tif'))    
    
    
    base_perp_file =os.path.join(ifgm_dir,f'{date1}_{date2}.base.perp')
    with open(base_perp_file, 'w') as file:
        with redirect_stdout(file):
             pg.base_perp(os.path.join(ifgm_dir,f'{date1}-{date2}.base'), 
                          os.path.join(slc_dir,date2,f'{date2}.slc.par'), 
                          os.path.join(ifgm_dir,f'{date1}_{date2}.off'))
    
    
    # Calculate bperp
    with open(base_perp_file, 'r') as file:
        lines = file.readlines()[17:]

        bperp_values = []
        for line in lines:
            # if line in lines is empty, contains 'user time', 'system time', 'elapsed time' or only contains whitespace, skip it
            if not line or 'user time' in line or 'system time' in line or 'elapsed time' in line or not line.strip():
                continue
            else:
                try:
                    bperp_values.append(float(line.split()[7]))
                except IndexError:
                    print(f"Skipping line due to insufficient values: {line.strip()}")
                
    if not bperp_values:
        print(f"No bperp values found for {date1} and {date2}. Skipping.")
    else:

        bperp = int(sum(bperp_values) / len(bperp_values)) 
    

        # Get bperp1 and bperp2
        bperp1 = subprocess.check_output(f'grep {date1} {topdir}/slcs/{dateM}.b_perp | awk \'(NR==1){{print $2}}\'', shell=True).decode().strip()
        bperp2 = subprocess.check_output(f'grep {date2} {topdir}/slcs/{dateM}.b_perp | awk \'(NR==1){{print $2}}\'', shell=True).decode().strip()
        sm = int(datetime.strptime(dateM, "%Y%m%d").timestamp())
        s1 = int(datetime.strptime(date1, "%Y%m%d").timestamp())
        s2 = int(datetime.strptime(date2, "%Y%m%d").timestamp())
        # Calculate number of days
        ndays12 = (s2 - s1) / 86400
        ndays1 = (sm - s1) / 86400
        ndays2 = (sm - s2) / 86400
        try:
            with open(f'{topdir}/b.perp', 'a') as file:
                file.write(f'{date1} {date2} {bperp} {ndays12:.1f} {ndays1:.1f} {ndays2:.1f} {bperp1} {bperp2}\n')
        except Exception as e: 
            print(f"Error writing bperp values to file: {e}")
    if adf_filter==False:
    #Adaptive interferogram filter using the power spectral density
        pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.diff'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc'),
            widthmli, 0.3, 64, 7, '-', 0, '-', 0.2)
        
        #Adaptive interferogram filter using the power spectral density    
        pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm2'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc2'), 
            widthmli, 0.4, 32, 7, '-',0, '-', 0.2)
        

    
        #Adaptive interferogram filter using the power spectral density    
        pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm2'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm3'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'), 
            widthmli, 0.5, 16, 7, '-', 0, '-', 0.2)
        rounds = 3
    else: 
        rounds = config["adf_filter"]["rounds"]
        # Extract the settings dictionary from your loaded JSON data
        settings = config["adf_filter"]["settings"]

        # Define the file suffixes for each consecutive step
        in_suffixes = ["", "_sm", "_sm2"]
        out_suffixes = ["_sm", "_sm2", "_sm3"]
        cc_suffixes = ["", "2", "3"]

        # Dynamically loop through the rounds (1 to 3)
        for step in range(1, 4):
            # Dynamically fetch the current round's configuration (round_1, round_2, round_3)
            setting = settings[f"round_{step}"]
            
            # Map index for file suffixes
            idx = step - 1
            
            # Construct input, output, and cc file paths
            in_file = os.path.join(ifgm_dir, f"{date1}-{date2}.diff{in_suffixes[idx]}")
            out_file = os.path.join(ifgm_dir, f"{date1}-{date2}.diff{out_suffixes[idx]}")
            cc_file = os.path.join(ifgm_dir, f"{date1}-{date2}.smcc{cc_suffixes[idx]}")
            
            # Execute the PyRATE / Gamma adf command using the round's specific parameters
            pg.adf(
                in_file, 
                out_file, 
                cc_file,
                widthmli, 
                setting["alpha"], 
                setting["nfft"], 
                setting["cc_win"], 
                '-', 
                0, 
                '-', 
                setting['wfrac']
            )


    
    pg.rasmph_pwr(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm{rounds}'), 
                  os.path.join(rslc_dir,f'{date2}',f'{date2}.mli'),
                  widthmli, 1, 1, 0, '-', '-', 1., .20, 1,
                  os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm{rounds}.tif'))
    
    pg.rascc(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc{rounds}'), 
                os.path.join(rslc_dir,date1,f'{date1}.mli'), 
                widthmli, 1, 1, 0, '-', '-', 0.1, 0.9, 1.0, .35, 1,
                os.path.join(ifgm_dir,f'{date1}-{date2}.smcc{rounds}'+'.tif'))
    
    #plot_backup_diff(date1,date2,config)

    if cleanup:
        for file in [f'{date1}-{date2}.diff_sm', f'{date1}-{date2}.smcc', f'{date1}-{date2}.diff_sm2', f'{date1}-{date2}.smcc2']:
            try:
                os.remove(os.path.join(ifgm_dir, file))
            except Exception as e:
                print(f'ERROR removing {file}: {e}')

    return True

def date_diff_days(d1, d2):
    fmt = "%Y%m%d"  # matches '20210101'
    dt1 = datetime.strptime(d1, fmt)
    dt2 = datetime.strptime(d2, fmt)
    return (dt2 - dt1).days
def baseline_relative_to_master(date,config):
    import subprocess as subp
    from datetime import datetime



    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    rslc_dir = os.path.join(topdir,'rslc')
    # Output baseline relative to master

    # check if baselines file exists in topdir
    if os.path.exists(os.path.join(topdir,'baselines')):
        print('baselines file exists')
    else:
        # make empty file 
        open(os.path.join(topdir,'baselines'),'a').close()

   
    basecall = f"base_orbit {os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.slc.par')} {os.path.join(topdir,'rslc',date,date+'.rslc.par')} - | grep perpendicular | gawk '{{print $5}}'"
                                                              
    
    print(bcolors.OKBLUE + f'Calculating baseline using command: {basecall}'+bcolors.ENDC)
    
    btemp = date_diff_days(dateM, date)
    try:
        bperp = subp.check_output(basecall, shell=True).decode('utf-8')
        # check if bperp is empty
        if bperp.strip() == '':
            raise ValueError('bperp is empty')
        print(bcolors.OKGREEN + f'Baseline perpendicular for {date} relative to {dateM} is {bperp.strip()} meters'+bcolors.ENDC)

        # calculate difference in days between dateM and date 
        
        with open(os.path.join(topdir,'baselines'),'a') as f:
            f.write(f'{dateM} {date} {bperp.strip()} {btemp}\n')
    except Exception as e:
        print(bcolors.FAIL + f'Error calculating baseline for {date}: {e}'+bcolors.ENDC)
        with open(os.path.join(topdir,'baselines'),'a') as f:
            f.write(f'{dateM} {date} 9999 {btemp}\n')


    # pg.base_init(os.path.join(slc_dir,f'{dateM}M', f'{dateM}.slc.par'), os.path.join(rslc_dir,f'{date}', f'{date}.rslc.par'), os.path.join(topdir, f'{dateM}_{date}.off'), '-', os.path.join(topdir, f'{dateM}_{date}.base'), 1)
    # pg.base_perp(os.path.join(topdir, f'{dateM}_{date}.base'), os.path.join(topdir, f'{date}.rslc.par'), os.path.join(topdir, f'{dateM}_{date}.off'), os.path.join(topdir, f'{dateM}_{date}.base.perp'))
    # # compute average bperp from the base.perp file (skip first 12 header lines, use 8th column)
    # base_perp_fp = os.path.join(topdir, f'{dateM}_{date}.base.perp')
    # bperp = None
    # try:
    #     values = []
    #     with open(base_perp_fp, 'r') as fh:
    #         for line in fh.readlines()[12:]:
    #             parts = line.split()
    #             if len(parts) >= 8:
    #                 try:
    #                     values.append(float(parts[7]))
    #                 except ValueError:
    #                     continue
    #     if values:
    #         bperp = int(sum(values) / len(values))
    #     else:
    #         bperp = 9999
    # except FileNotFoundError:
    #     print(bcolors.WARNING + f"Warning: {base_perp_fp} not found" + bcolors.ENDC)
    #     bperp = 9999
    # except Exception as e:
    #     print(bcolors.FAIL + f"Error reading {base_perp_fp}: {e}" + bcolors.ENDC)
    #     bperp = 9999    

    # # ensure rslc dir exists and append bperp entry
    # os.makedirs(os.path.join(topdir, 'rslc'), exist_ok=True)
    # bperp_file = os.path.join(topdir, 'rslc', f'{dateM}.b_perp')
    # try:
    #     with open(bperp_file, 'a') as fh:
    #         fh.write(f'{date} {bperp}\n')
    # except Exception as e:
    #     print(bcolors.FAIL + f"Error writing to {bperp_file}: {e}" + bcolors.ENDC)

def pixel_offset_tracking(date1, date2, config):

    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    rslc_dir = os.path.join(topdir,'rslc')
    

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    config['widthdem'] = widthdem

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    
    os.makedirs(os.path.join(topdir,'pixel_offset'), exist_ok=True)

    if os.path.exists(os.path.join(topdir,'pixel_offset',f'{date1}-{date2}')):
        print(bcolors.WARNING + f"Directory {topdir}/pixel_offset/{date1}-{date2} already exists. Skipping processing." + bcolors.ENDC)
        return False
    
    os.makedirs(os.path.join(topdir,'pixel_offset',f'{date1}-{date2}'),exist_ok = True)
    pixoff_dir = os.path.join(topdir,'pixel_offset',f'{date1}-{date2}')
    

    offset_file = os.path.join(pixoff_dir,f'{date1}_{date2}.fullpix.off')
    disp_map_file = os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map')
    disp_val_file = os.path.join(pixoff_dir,f'{date1}_{date2}.disp_val')
    corr_file = os.path.join(pixoff_dir,f'{date1}_{date2}.corr')
    offsets_file = os.path.join(pixoff_dir,f'{date1}_{date2}.offsets')
    rslc_date1 = os.path.join(rslc_dir,f'{date1}',f'{date1}.rslc')
    rslc_date2 = os.path.join(rslc_dir,f'{date2}',f'{date2}.rslc')
    rslc_date1_par = os.path.join(rslc_dir,f'{date1}',f'{date1}.rslc.par')
    rslc_date2_par = os.path.join(rslc_dir,f'{date2}',f'{date2}.rslc.par')
    corrstd_file = os.path.join(pixoff_dir,f'{date1}_{date2}.corrstd')
    pg.create_offset(rslc_date1_par,
                     rslc_date2_par, 
                     offset_file, 1, 1, 1, 0)

    pg.offset_pwr_tracking(rslc_date1,
                           rslc_date2,
                           rslc_date1_par,
                           rslc_date2_par,
                           offset_file,
                           offsets_file,
                           corr_file,'-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',corrstd_file)
    pg.offset_tracking(offsets_file,
                        corr_file,
                        rslc_date1_par,
                        offset_file,
                        disp_map_file,
                        disp_val_file, 1, '-', 0)
    
    
    def get_offset_estimation_range_samples(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip().startswith('offset_estimation_range_samples:'):
                    widthoff = int(line.split(':')[1].strip())
                if line.strip().startswith('offset_estimation_azimuth_samples:'):
                    lenoff = int(line.split(':')[1].strip())
        if 'widthoff' in locals() and 'lenoff' in locals():
            return widthoff, lenoff
        return None


    widthoff, lenoff = get_offset_estimation_range_samples(os.path.join(pixoff_dir,f'{date1}_{date2}.fullpix.off'))
    
    
    
    # extract both range and azi displacements
    pg.cpx_to_real(disp_map_file,disp_map_file+'.rng',widthoff,0) #$outdir/disp_map $outdir/disp_map.rng $widthoff 0 >/dev/null
    pg.cpx_to_real(disp_map_file,disp_map_file+'.azi',widthoff,1) #$outdir/disp_map $outdir/disp_map.azi $widthoff 1 >/dev/null

    output_rng = os.path.join(pixoff_dir,f'{date1}_{date2}.rng')
    output_az = os.path.join(pixoff_dir,f'{date1}_{date2}.az')
    output_corr = os.path.join(pixoff_dir,f'{date1}_{date2}.offset_tracking.corr')
    output_corrstd = os.path.join(pixoff_dir,f'{date1}_{date2}.offset_tracking.corrstd')
    
    cv2_installed = False

    import numpy as np
    # try import cv2
    try:
        import cv2
        cv2_installed = True
    except ImportError:
        print(bcolors.FAIL + 'Error: OpenCV (cv2) is not installed. Going to try use SciPy.' + bcolors.ENDC)
        
    # if cv2 is not installed, skip resampling and geocoding
    if not cv2_installed:
        
        from scipy.ndimage import zoom

        def resize_and_write(infile, outfile, in_shape, out_shape):
            a = (
                np.fromfile(infile, dtype=np.float32)
                .byteswap()
                .reshape(in_shape)
            )

            zoom_factors = (
                out_shape[0] / in_shape[0],  # rows
                out_shape[1] / in_shape[1],  # cols
            )

            a_resized = zoom(a, zoom_factors, order=1)

            a_resized.byteswap().tofile(outfile)
        resize_and_write(disp_map_file+'.rng', output_rng, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(disp_map_file+'.azi', output_az, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(corr_file, output_corr, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(corrstd_file, output_corrstd, (lenoff, widthoff), (lengthmli, widthmli))
    else:
    # resample towards orig size
        a = np.fromfile(disp_map_file+'.rng', dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_rng)

        a = np.fromfile(disp_map_file+'.azi', dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_az)

        a = np.fromfile(corr_file, dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_corr)

        a = np.fromfile(corrstd_file, dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_corrstd) 

    # pg.rasmph_pwr(os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map'), 
    #               os.path.join(rslc_dir,f'{date1}',f'{date1}.mli'), 
    #               value, 1, 1, 0, '-', '-', 1., .20, 1,
    #               os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map.tif'))
    output_list = [output_rng, output_az, output_corr, output_corrstd]
    for output in output_list:
        print(bcolors.OKBLUE + f'Geocoding {output}'+bcolors.ENDC)
        pg.geocode_back(output, widthmli, 
                        os.path.join(slc_dir,f"{dateM}M",f'{dateM}M.lt_fine'), 
                        output+'.geo', widthdem, '-', 0) 
        print(bcolors.OKBLUE + f'Converting {output} to geotiff'+bcolors.ENDC)
        pg.data2geotiff(os.path.join(slc_dir,f"{dateM}M",f'P.dem_par'), output+'.geo', 2, output+'.geo.tif', 0.0)


    return 


def pixel_offset_tracking_with_mask(date1, date2, config, ls_map_path):


    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    rslc_dir = os.path.join(topdir,'rslc')
    

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    config['widthdem'] = widthdem

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    
    os.makedirs(os.path.join(topdir,'pixel_offset'), exist_ok=True)

    if os.path.exists(os.path.join(topdir,'pixel_offset',f'{date1}-{date2}')):
        print(bcolors.WARNING + f"Directory {topdir}/pixel_offset/{date1}-{date2} already exists. Skipping processing." + bcolors.ENDC)
        return False
    
    os.makedirs(os.path.join(topdir,'pixel_offset',f'{date1}-{date2}'),exist_ok = True)
    pixoff_dir = os.path.join(topdir,'pixel_offset',f'{date1}-{date2}')
    

    offset_file = os.path.join(pixoff_dir,f'{date1}_{date2}.fullpix.off')
    disp_map_file = os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map')
    disp_val_file = os.path.join(pixoff_dir,f'{date1}_{date2}.disp_val')
    corr_file = os.path.join(pixoff_dir,f'{date1}_{date2}.corr')
    offsets_file = os.path.join(pixoff_dir,f'{date1}_{date2}.offsets')
    rslc_date1 = os.path.join(rslc_dir,f'{date1}',f'{date1}.rslc')
    rslc_date2 = os.path.join(rslc_dir,f'{date2}',f'{date2}.rslc')
    rslc_date1_par = os.path.join(rslc_dir,f'{date1}',f'{date1}.rslc.par')
    rslc_date2_par = os.path.join(rslc_dir,f'{date2}',f'{date2}.rslc.par')
    corrstd_file = os.path.join(pixoff_dir,f'{date1}_{date2}.corrstd')
    pg.create_offset(rslc_date1_par,
                     rslc_date2_par, 
                     offset_file, 1, 1, 1, 0)

    pg.offset_pwr_tracking(rslc_date1,
                           rslc_date2,
                           rslc_date1_par,
                           rslc_date2_par,
                           offset_file,
                           offsets_file,
                           corr_file,'-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',corrstd_file)
    pg.offset_tracking(offsets_file,
                        corr_file,
                        rslc_date1_par,
                        offset_file,
                        disp_map_file,
                        disp_val_file, 1, '-', 0)
    
    
    def get_offset_estimation_range_samples(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip().startswith('offset_estimation_range_samples:'):
                    widthoff = int(line.split(':')[1].strip())
                if line.strip().startswith('offset_estimation_azimuth_samples:'):
                    lenoff = int(line.split(':')[1].strip())
        if 'widthoff' in locals() and 'lenoff' in locals():
            return widthoff, lenoff
        return None


    widthoff, lenoff = get_offset_estimation_range_samples(os.path.join(pixoff_dir,f'{date1}_{date2}.fullpix.off'))
    
    
    
    # extract both range and azi displacements
    pg.cpx_to_real(disp_map_file,disp_map_file+'.rng',widthoff,0) #$outdir/disp_map $outdir/disp_map.rng $widthoff 0 >/dev/null
    pg.cpx_to_real(disp_map_file,disp_map_file+'.azi',widthoff,1) #$outdir/disp_map $outdir/disp_map.azi $widthoff 1 >/dev/null

    output_rng = os.path.join(pixoff_dir,f'{date1}_{date2}.rng')
    output_az = os.path.join(pixoff_dir,f'{date1}_{date2}.az')
    output_corr = os.path.join(pixoff_dir,f'{date1}_{date2}.offset_tracking.corr')
    output_corrstd = os.path.join(pixoff_dir,f'{date1}_{date2}.offset_tracking.corrstd')
    
    cv2_installed = False

    import numpy as np
    # try import cv2
    try:
        import cv2
        cv2_installed = True
    except ImportError:
        print(bcolors.FAIL + 'Error: OpenCV (cv2) is not installed. Going to try use SciPy.' + bcolors.ENDC)
        
    # if cv2 is not installed, skip resampling and geocoding
    if not cv2_installed:
        
        from scipy.ndimage import zoom

        def resize_and_write(infile, outfile, in_shape, out_shape):
            a = (
                np.fromfile(infile, dtype=np.float32)
                .byteswap()
                .reshape(in_shape)
            )

            zoom_factors = (
                out_shape[0] / in_shape[0],  # rows
                out_shape[1] / in_shape[1],  # cols
            )

            a_resized = zoom(a, zoom_factors, order=1)

            a_resized.byteswap().tofile(outfile)
        resize_and_write(disp_map_file+'.rng', output_rng, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(disp_map_file+'.azi', output_az, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(corr_file, output_corr, (lenoff, widthoff), (lengthmli, widthmli))
        resize_and_write(corrstd_file, output_corrstd, (lenoff, widthoff), (lengthmli, widthmli))
    else:
    # resample towards orig size
        a = np.fromfile(disp_map_file+'.rng', dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_rng)

        a = np.fromfile(disp_map_file+'.azi', dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_az)

        a = np.fromfile(corr_file, dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_corr)

        a = np.fromfile(corrstd_file, dtype=np.float32).byteswap().reshape((lenoff,widthoff))
        cv2.resize(a,dsize=(widthmli,lengthmli), interpolation=cv2.INTER_LINEAR).byteswap().tofile(output_corrstd) 

    # pg.rasmph_pwr(os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map'), 
    #               os.path.join(rslc_dir,f'{date1}',f'{date1}.mli'), 
    #               value, 1, 1, 0, '-', '-', 1., .20, 1,
    #               os.path.join(pixoff_dir,f'{date1}_{date2}.disp_map.tif'))
    output_list = [output_rng, output_az, output_corr, output_corrstd]
    for output in output_list:
        print(bcolors.OKBLUE + f'Geocoding {output}'+bcolors.ENDC)
        pg.geocode_back(output, widthmli, 
                        os.path.join(slc_dir,f"{dateM}M",f'{dateM}M.lt_fine'), 
                        output+'.geo', widthdem, '-', 0) 
        print(bcolors.OKBLUE + f'Converting {output} to geotiff'+bcolors.ENDC)
        pg.data2geotiff(os.path.join(slc_dir,f"{dateM}M",f'P.dem_par'), output+'.geo', 2, output+'.geo.tif', 0.0)

        

    return 




def read_gamma_ls_map(path, width, length):
    """
    Read and verify a GAMMA-style Layover and Shadow Map (ls_map).

    Format:
    1 byte (uint8) per pixel.
    Bit-flagged categorization mapping.
    No header.

    Parameters:
    -----------
    path : str
        File path to the binary ls_map data.
    width : int
        Number of columns (range samples).
    length : int
        Number of rows (azimuth lines).

    Returns:
    --------
    np.ndarray
        2D uint8 matrix of dimensions (length, width).
    """
    file_size = os.path.getsize(path)
    expected_bytes = width * length

    print("\n--- GAMMA ls_map Check ---")
    print(f"Path: {path}")
    print(f"File size: {file_size} bytes")
    print(f"Expected geometry: {length} lines x {width} samples ({expected_bytes} bytes)")

    if file_size != expected_bytes:
        raise ValueError(
            f"ls_map file size does not match expected uint8 geometry.\n"
            f"Got: {file_size} bytes\n"
            f"Expected: {expected_bytes} bytes"
        )

    # 1-byte data type means system endianness does not matter
    ls_map = np.fromfile(path, dtype=np.uint8, count=expected_bytes)
    ls_map = ls_map.reshape((length, width))

    # Print structural summary to console for tracking verification
    unique, counts = np.unique(ls_map, return_counts=True)
    meaning_map = {0: "Outside Swath", 1: "Good Visibility", 5: "Layover", 17: "Shadow", 21: "Layover+Shadow"}
    
    print("Detected Category Profile:")
    for val, count in zip(unique, counts):
        label = meaning_map.get(val, "Custom Bit-Flag Combination")
        print(f"  -> Value {val:2d} ({label}): {count} pixels")

    return ls_map

def proc_unw(date1,date2,config):

    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    rslc_dir = os.path.join(topdir,'rslc')
    
    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    config['widthdem'] = widthdem

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')
    # Coherence
    # Do on unsmoothed interferogram
    # Window currently at 5x5. (also triangular weighting - difference not investigated)
    # coherence estimation from normalized interferogram and co-registered intensity images
    if os.path.exists(os.path.join(rslc_dir,date2,f'{date2}_geocode.mli')):
        pass
    else:
        pg.geocode_back(os.path.join(rslc_dir,date2,f'{date2}.mli'),
                        widthmli, 
                        os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                        os.path.join(rslc_dir,date2,f'{date2}_geocode.mli'), 
                        widthdem, '-', 2, 0)
                
    pg.cc_wave(os.path.join(ifgm_dir,f'{date1}-{date2}.diff'), 
               os.path.join(rslc_dir,date1,f'{date1}.mli'), 
               os.path.join(rslc_dir,date2,f'{date2}.mli'), 
               os.path.join(ifgm_dir,f'{date1}-{date2}.cc'), 
               widthmli, 5, 5, 1)
    pg.geocode_back(os.path.join(ifgm_dir,f'{date1}-{date2}.cc'), 
                                widthmli, 
                                os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                                os.path.join(ifgm_dir,f'{date1}-{date2}.cc.geo'),
                                widthdem, '-', 2)
    
    pg.rascc(os.path.join(ifgm_dir,f'{date1}-{date2}.cc.geo'), 
                        os.path.join(rslc_dir,date2,f'{date2}_geocode.mli'), 
                        widthdem, 1, 1, 0, 10, 10, 0.1, 0.9, 1.0, .35, 1,
                        os.path.join(ifgm_dir,f'{date1}-{date2}.cc.geo.tif'))
    
    if 'unw_in_radar' in config:
        unw_in_radar = config['unw_in_radar']
    else: 
        unw_in_radar = True

    if 'unw_in_geo' in config:
        unw_in_geo = config['unw_in_geo']
    else:
        unw_in_geo = False

    ###############
    # UNWRAPPING
    ########## MCF

	# Phase unwrapping mask
	# Be careful with what you are using as Coherence (smoothed or original) to mask

    if unw_in_radar:
        # print in blue, phase unwrapping in radar coords 
        print(bcolors.OKBLUE + f'Phase unwrapping {date1}-{date2} in radar coordinates' + bcolors.ENDC)
        # Phase unwrapping mask
        pg.rascc_mask(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'),
                    os.path.join(rslc_dir,date1, f'{date1}.mli'), widthmli, 1, 1, 0, 1, 1, 0.5, 0.0, 0.1, 0.9, 1.0, 0.20, 1, 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.mask.ras'))
        # Unwrap Minimum Cost Function
        pg.mcf(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm3'),
            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.mask.ras'),
            os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw'), 
                widthmli, 
                0, 
                '-', '-', '-', '-', 
                npat_r, npat_az, '-',
                r_init, az_init, 1)

    
        
        #disrmg f'{date1}-{date2}.diff_sm.unw {date1}.rslc.mli widthmli 1 1 0 1.0 1. .20 0. &

        # Geocode unwrapped
        pg.geocode_back(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw'), widthmli, 
                        os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                        os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw.geo'), widthdem, '-', 0) 

        
        pg.geocode_back(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'), 
                            widthmli, 
                            os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc.geo'),
                            widthdem, '-', 2)
        pg.rasmph_pwr(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw'), 
                          os.path.join(rslc_dir,f'{date2}',f'{date2}.mli'),
                          widthmli, 1, 1, 0, '-', '-', 1., .20, 1,
                          os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw.tif'))
        
        pg.rasrmg(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw.geo'), 
                    os.path.join(rslc_dir,date2,f'{date2}_geocode.mli'), 
                    widthdem, 1, 1, 0, 10, 10, 1., 1., .20, 0, 1, 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw.geo.tif'))


        pg.rascc(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'), 
                    os.path.join(rslc_dir,date2,f'{date2}.mli'), 
                    widthmli, 1, 1, 0, 10, 10, 0.1, 0.9, 1.0, .35, 1,
                    os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'+'.tif'))
    if unw_in_geo:
        # print in blue, phase unwrapping in geo coordinates
        print(bcolors.OKBLUE + f'Phase unwrapping {date1}-{date2} in geo coordinates' + bcolors.ENDC)
         # Geocode unwrapped
        rounds = config['adf_filter']['rounds']
        pg.geocode_back(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm{rounds}'), widthmli, 
                        os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                        os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.geo'), widthdem, '-', 0) 

        pg.geocode_back(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc{rounds}'), 
                            widthmli, 
                            os.path.join(ifgm_dir,f'{dateM}M.lt_fine'), 
                            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc{rounds}.geo'),
                            widthdem, '-', 2)
        # Phase unwrapping mask
        pg.rascc_mask(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3.geo'),
                    os.path.join(rslc_dir,date1, f'{date1}_geocode.mli'), widthdem, 1, 1, 0, 1, 1, 0.5, 0.0, 0.1, 0.9, 1.0, 0.20, 1, 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.geo.mask.ras'))
        # Unwrap Minimum Cost Function
        pg.mcf(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.geo'),
            os.path.join(ifgm_dir,f'{date1}-{date2}.smcc.geo'), 
            os.path.join(ifgm_dir,f'{date1}-{date2}.geo.mask.ras'),
            os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.geo.unw'), 
                widthdem, 
                0, 
                '-', '-', '-', '-', 
                npat_r, npat_az, '-',
                '-', '-', 1)

        pg.rasrmg(os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.geo.unw'), 
                    os.path.join(rslc_dir,date2,f'{date2}_geocode.mli'), 
                    widthdem, 1, 1, 0, 10, 10, 1., 1., .20, 0, 1, 
                    os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.geo.unw.tif'))


        pg.rascc(os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'), 
                    os.path.join(rslc_dir,date2,f'{date2}.mli'), 
                    widthmli, 1, 1, 0, 10, 10, 0.1, 0.9, 1.0, .35, 1,
                    os.path.join(ifgm_dir,f'{date1}-{date2}.smcc3'+'.tif'))
        


    return 



def output_licsbas_tifs(date1,date2,config):
    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
   
    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')

    os.makedirs(os.path.join(topdir,'LiCSBAS'),exist_ok = True)
    os.makedirs(os.path.join(topdir,'LiCSBAS','GEOC'),exist_ok = True)
    os.makedirs(os.path.join(topdir,'LiCSBAS','GEOC',f'{date1}_{date2}'),exist_ok = True)
    GEOC_IF_dir = os.path.join(topdir,'LiCSBAS','GEOC',f'{date1}_{date2}')

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

   
    cleanup = config["cleanup"]

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    
    licsbas_geo_tif = os.path.join(GEOC_IF_dir,f'{date1}_{date2}'+'.geo.unw.tif')
    licsbas_geo_cc_tif = os.path.join(GEOC_IF_dir,f'{date1}_{date2}'+'.geo.cc.tif')
    try:
        pg.data2geotiff(os.path.join(ifgm_dir,'P.dem_par'), os.path.join(ifgm_dir,f'{date1}-{date2}.diff_sm.unw.geo'), 2, licsbas_geo_tif, 0.0)
        pg.data2geotiff(os.path.join(ifgm_dir,'P.dem_par'), 
                        os.path.join(ifgm_dir,f'{date1}-{date2}.cc.geo'),
                        2, licsbas_geo_cc_tif, 0.0) 
    except Exception as e:
        print(f"Error during data2geotiff: {e}")
    
    os.chdir(topdir)




def output_unw_smart_plot_pdf(date1,date2,config):

    try:
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        from matplotlib.colors import LinearSegmentedColormap
        import seaborn as sns
        from osgeo import gdal
        import rasterio as rio
        import earthpy.spatial as es
        from cmcrameri import cm
        import datetime
        from matplotlib.colors import ListedColormap
        import matplotlib as mpl
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    except:
        print(" Please use pygmt for step7")
        

    def add_scale_bar(ax):
        # Scale bar helper
        scale_bar_length_deg = 500 / 111000  # 500 meters in degrees
        inset = inset_axes(ax, width="15%", height="5%", loc='lower right')
        inset.plot([0, scale_bar_length_deg], [0, 0], color='k', lw=3)
        inset.set_xlim(0, scale_bar_length_deg)
        inset.set_ylim(-0.01, 0.01)
        inset.axis('off')
        inset.text(scale_bar_length_deg/2, 0.01, '500 m', ha='center', va='bottom', fontsize=8)
    def add_los_arrow(ax, heading_deg):
        """
        Adds two black arrows in an inset axis:
        - One in the LOS direction (heading_deg),
        - One 90° clockwise (perpendicular),
        with a label θᵢ = 48.7755°.

        Parameters:
        - ax: The axis to attach the inset to.
        - heading_deg: LOS heading in degrees clockwise from North.
        """
        import math

        # Create a small inset axis
        inset = inset_axes(ax, width="25%", height="25%", loc='upper left')

        #inset_ll = inset_axes(ax, width="25%", height="25%", loc='lower left')
        inset_ur = inset_axes(ax, width="25%", height="25%", loc='lower left')

        
        
        los_len = 0.4 * 2      # LOS arrow (twice as long)
        perp_len = 0.4         # Perpendicular arrow


        theta_rad = math.radians(heading_deg)

        # LOS direction unit vector
        dx1 = math.sin(theta_rad)
        dy1 = math.cos(theta_rad)

        # Perpendicular direction unit vector (90° clockwise)
        dx2 = math.sin(theta_rad + math.pi / 2)
        dy2 = math.cos(theta_rad + math.pi / 2)

        # Arrows start before the center, end after the center
        # Shift start points backward from center
        start_los = (0.5 - dx1 * los_len / 2, 0.5 - dy1 * los_len / 2)
        start_perp = (0.5 - dx2 * perp_len / 2, 0.5 - dy2 * perp_len / 2)

        # Draw arrows
        inset.arrow(*start_los, dx1 * los_len, dy1 * los_len, head_width=0.08, head_length=0.08, fc='k', ec='k')
        inset.arrow(*start_perp, dx2 * perp_len, dy2 * perp_len, head_width=0.08, head_length=0.08, fc='k', ec='k')
        inc = round(float(dateM_mli_par.get_value('incidence_angle')[0]), 2)
        inset_ur.text(0.1, 0.05, rf'$\theta_i = {inc}^\circ$', ha='left', va='bottom', fontsize=11)
        inset_ur.set_xlim(0, 1)
        inset_ur.set_ylim(0, 1)
        inset_ur.axis('off')
        # Clean up inset
        inset.set_xlim(0, 1)
        inset.set_ylim(0, 1)
        inset.axis('off')
        return

    # Assign variables
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    lon_min, lon_max = config["min_lon"], config["max_lon"]
    lat_min, lat_max = config["min_lat"], config["max_lat"]

    print(bcolors.OKBLUE + f'Outputting smart plot pdf for {date1} and {date2}' + bcolors.ENDC)

    print('Must be in conda activate pygmt')
    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')

    os.makedirs(os.path.join(topdir,'outputs'),exist_ok = True)

    GEOC_IF_dir = os.path.join(topdir,'LiCSBAS','GEOC',f'{date1}_{date2}')

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

   
    cleanup = config["cleanup"]

    dem_par = pg.ParFile(os.path.join(slc_dir,f'{dateM}M','P.dem_par'))	
    widthdem=int(dem_par.get_value('width'))
    
    licsbas_geo_tif = os.path.join(GEOC_IF_dir,f'{date1}_{date2}'+'.geo.unw.tif')
    licsbas_geo_cc_tif = os.path.join(GEOC_IF_dir,f'{date1}_{date2}'+'.geo.cc.tif')

    

    sns.set_context("paper")

    # File paths
    displacement_fp = licsbas_geo_tif
    displacement_fp_2 = licsbas_geo_cc_tif

    dem_fp = os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}M.hgt.geotiff.tif')

    # Load displacement raster and mask zeros
    with gdal.Open(displacement_fp) as disp_ds:
        mDisplacement = np.array(disp_ds.ReadAsArray(), dtype=float)
        mDisplacement[mDisplacement == 0.] = np.nan
        mDisplacement = -mDisplacement
        ulx, xres, xskew, uly, yskew, yres = disp_ds.GetGeoTransform()
        lrx = ulx + (disp_ds.RasterXSize * xres)
        lry = uly + (disp_ds.RasterYSize * yres)

    with gdal.Open(displacement_fp_2) as disp_ds_2:
        coherence = np.array(disp_ds_2.ReadAsArray(), dtype=float)
        coherence[coherence == 0.] = np.nan
        coherence = -coherence
        ulx_2, xres_2, xskew_2, uly_2, yskew_2, yres_2 = disp_ds_2.GetGeoTransform()
        lrx_2 = ulx_2 + (disp_ds_2.RasterXSize * xres_2)
        lry_2 = uly_2 + (disp_ds_2.RasterYSize * yres_2)


    with rio.open(dem_fp) as src:
        elevation = src.read(1)
        elevation = np.where(elevation < 0, np.nan, elevation)
        
        # Get the affine transform
        transform = src.transform
        dem_ulx = transform.c
        dem_uly = transform.f
        dem_xres = transform.a
        dem_yres = transform.e
        dem_xskew = transform.b
        dem_yskew = transform.d
        dem_lrx = dem_ulx + (src.width * dem_xres)
        dem_lry = dem_uly + (src.height * dem_yres)


    h_dem = es.hillshade(elevation, azimuth=-10)

   

    # Plotting
    sns.reset_orig()
    sns.set_context("paper")

    mpl.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif',
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11
    })

    fig = plt.figure(figsize=(16, 10))

    brighter_roma_r = cm.vik#LinearSegmentedColormap.from_list("brighter_roma_r", cm.roma_r(np.linspace(0.3, 1.0, 256)))

    gs = fig.add_gridspec(1, 3, hspace=0.05, wspace=0.05)

    # Create axes
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1],sharex=ax1, sharey=ax1)
    ax4 = fig.add_subplot(gs[0, 2],sharex=ax1, sharey=ax1)

    

    # Plotting helper
    plot_params = [
        (ax1, mDisplacement, ulx, lrx, lry, uly, f'{date1}-{date2}',-30,30),
        (ax2, coherence, ulx_2, lrx_2, lry_2, uly_2, f'{date1}-{date2}',-100,100)]
      

    colorbars = []
    images = []
    for ax, data, x1, x2, y1, y2, title,vmin,vmax in plot_params:
        
        ax.imshow(h_dem, cmap=cm.grayC, alpha=0.8, extent=[dem_ulx, dem_lrx,dem_lry,dem_uly])
        im = ax.imshow(data, cmap=brighter_roma_r, interpolation='nearest', alpha=0.6,
                    extent=[x1, x2, y1, y2])#,vmin=vmin,vmax=vmax)
        images.append(im)
        ax.set_xlim([lon_min, lon_max])
        ax.set_ylim([lat_min, lat_max])
        ax.set_xticks([round(lon_min, 3), round(lon_max, 3)])
        ax.set_yticks([round(lat_min, 3), round(lat_max, 3)])
        ax.ticklabel_format(useOffset=False, style='plain') 
        # Place colorbar under each subplot
        cax = inset_axes(ax,
                         width="80%",  # 80% of the axis width
                         height="5%",  # 5% of the axis height
                         loc='lower center',
                         bbox_to_anchor=(0.1, -0.18, 0.8, 0.05),
                         bbox_transform=ax.transAxes,
                         borderpad=0)
        if ax == ax1:
            cbar = plt.colorbar(im, cax=cax, orientation='horizontal', label='Displacement (mm)')
        elif ax == ax2:
            cbar = plt.colorbar(im, cax=cax, orientation='horizontal', label='Coherence')
        # Make colorbar thicker
        cbar.ax.tick_params(axis='x', length=8, width=2)
        cbar.outline.set_linewidth(2)
        cbar.ax.xaxis.set_tick_params(labelsize=11)
        colorbars.append(cbar)

        ax.tick_params(axis='x', labelrotation=0)

        ax.set_title(title)
        add_scale_bar(ax)
        heading = float(dateM_mli_par.get_value('heading')[0])

        add_los_arrow(ax, heading)

    for ax in [ax2, ax4]:
        plt.setp(ax.get_yticklabels(), visible=False)
    # DEM + hillshade + points
    half_fes = ListedColormap(cm.fes(np.linspace(0.5, 1.0, 256)))
    half_fes.set_bad(color='black')
    elevation = np.where(elevation == 0, np.nan, elevation)
    im3 = ax4.imshow(elevation, cmap=half_fes, alpha=0.8, extent=[ulx, lrx, lry, uly])
    ax4.imshow(h_dem, cmap=cm.grayC, alpha=0.5, extent=[ulx, lrx, lry, uly])
    ax4.set_xlim([lon_min, lon_max])
    ax4.set_ylim([lat_min, lat_max])
    ax4.set_title('Elevation')
    ax4.set_xticks([round(lon_min, 3), round(lon_max, 3)])
    ax4.set_yticks([round(lat_min, 3), round(lat_max, 3)])
    ax4.tick_params(axis='x', labelrotation=0)
    ax4.ticklabel_format(useOffset=False, style='plain')
    # Colorbar under ax4
    cax4 = inset_axes(ax4,
                      width="80%",
                      height="5%",
                      loc='lower center',
                      bbox_to_anchor=(0.1, -0.18, 0.8, 0.05),
                      bbox_transform=ax4.transAxes,
                      borderpad=0)
    cbar4 = plt.colorbar(im3, cax=cax4, orientation='horizontal', label='Elevation (m)',aspect=100)
    # Make colorbar thicker and bigger


    fig.tight_layout()
    fig.savefig(f"{date1}-{date2}.pdf", dpi=300)
    fig.savefig(f"{date1}-{date2}.png", dpi=300)
    plt.close()


    os.chdir(topdir)



def convert_tif_to_png(tif_file):
    png_file = tif_file.replace('.tif', '.png')
    pg.run_cmd('convert', tif_file, '-transparent', 'black', png_file)
    print(f"Converted {tif_file} to {png_file}")
    return


def cat_multiple_slcs(date,config):
    rlks, azlks, dem, demlat, demlon = config["rlks"], config["azlks"], config["dem"], config["demlat"], config["demlon"]
    npat_r, npat_az, r_init, az_init = config["npat_r"], config["npat_az"], config["r_init"], config["az_init"]
    dateM, topdir, slc_dir, dim_dir = config['dateM'], config['topdir'], config["slc_dir"], config["dim_dir"]
    
    cleanup = config['cleanup']
    slc_date_dir = os.path.join(slc_dir,date)
    slc_dateM_dir = os.path.join(slc_dir,dateM+'M')
  

    tif_dir = os.path.join(topdir,'tifs')
    if not os.path.exists(slc_dir):
        os.makedirs(slc_dir)
    if not os.path.exists(slc_date_dir):
        os.makedirs(slc_date_dir)
    if not os.path.exists(tif_dir):
        os.makedirs(tif_dir)
    # find number of slcs for each date 
    dims_for_date =glob(os.path.join(topdir,'*','*','TSX-1*',f'T?X*{date}*'))
    print(f'Found {len(dims_for_date)} DIMs for date {date}')
    # Extract the first five parts of each path
    dims_for_date_short = [os.path.join(*path.split(os.sep)[:5]) for path in dims_for_date]

    # Extract timestamps and sort paths by timestamp
    def extract_timestamp(path):
        match = re.search(r'(\d{8}T\d{6})_(\d{8}T\d{6})', path)
        if match:
            start_time = datetime.strptime(match.group(1), '%Y%m%dT%H%M%S')
            end_time = datetime.strptime(match.group(2), '%Y%m%dT%H%M%S')
            return start_time, end_time
        return None, None


    dims_with_times = [(path, *extract_timestamp(path)) for path in dims_for_date]
    dims_with_times = [item for item in dims_with_times if item[1] and item[2]]
    dims_with_times.sort(key=lambda x: x[1])

    print('dims with times',dims_with_times)
    # Filter for consecutive or overlapping times
    consecutive_dims = []
    for i in range(len(dims_with_times) - 1):
        if dims_with_times[i][2] >= dims_with_times[i + 1][1]:
            consecutive_dims.append(dims_with_times[i][0])
            consecutive_dims.append(dims_with_times[i + 1][0])

    # Remove duplicates
    consecutive_dims = list(dict.fromkeys(consecutive_dims))

    print(consecutive_dims)
    
    n_date_slcs = len(dims_for_date)
    print(f'Found {n_date_slcs} slcs for date {date}')

    for i,dim in enumerate(consecutive_dims):
        print(bcolors.OKBLUE+dim+bcolors.ENDC)

        date_xml = glob(os.path.join(dim,'*xml'))[0]
        date_cos = glob(os.path.join(dim,'IMAGEDATA','*cos'))[0]
        print(date_xml)
        print(date_cos)

        pg.par_TX_SLC(date_xml,date_cos,os.path.join(slc_dir,date,date+f'.{i+1}.slc.par'),os.path.join(slc_dir,date,date+f'.{i+1}.slc'))	

        slc_name = os.path.join(slc_dir, date, f'{date}.{i+1}.slc')
        slc_par_name = os.path.join(slc_dir, date, f'{date}.{i+1}.slc.par')

        pg.SLC_corners(slc_par_name,0,slc_par_name+'.kml')

        slc_to_tif(slc_name)

    if consecutive_dims == []:
        print(bcolors.WARNING+f'No consecutive or overlapping DIMs found for date {date}, cannot combine into single SLC. Please check the DIM timestamps and ensure they are correct.'+bcolors.ENDC)
        for i,dim in enumerate(dims_with_times):
            print(bcolors.OKBLUE+dim[0]+bcolors.ENDC)

            date_xml = glob(os.path.join(dim[0],'*xml'))[0]
            date_cos = glob(os.path.join(dim[0],'IMAGEDATA','*cos'))[0]
            print(date_xml)
            print(date_cos)

            pg.par_TX_SLC(date_xml,date_cos,os.path.join(slc_dir,date,date+f'.0{i+1}.slc.par'),os.path.join(slc_dir,date,date+f'.0{i+1}.slc'))	

            slc_name = os.path.join(slc_dir, date, f'{date}.0{i+1}.slc')
            slc_par_name = os.path.join(slc_dir, date, f'{date}.0{i+1}.slc.par')

            pg.SLC_corners(slc_par_name,0,slc_par_name+'.kml')

            slc_to_tif(slc_name)

    if n_date_slcs == 1:
        print(bcolors.OKCYAN+'Only one SLC found, copying to .slc and .slc.par'+bcolors.ENDC)
        shutil.copy(os.path.join(slc_dir,date,date+f'.1.slc'),os.path.join(slc_dir,date,date+'.slc'))
        shutil.copy(os.path.join(slc_dir,date,date+f'.1.slc.par'),os.path.join(slc_dir,date,date+'.slc.par')) 

    if n_date_slcs > 1:
        print(bcolors.OKCYAN+'More than one SLC found, combining into single SLC'+bcolors.ENDC)

        pg.create_offset(os.path.join(slc_dir,date,date+f'.1.slc.par'),
                         os.path.join(slc_dir,date,date+f'.2.slc.par'),
                         os.path.join(slc_dir,date,date+f'.1-2.off'),
                         1, 1, 1, 0)

        
        slc_1_parfile = pg.ParFile(os.path.join(slc_dir,date,date+f'.1.slc.par'))

        slc_1_halfwidth = int(int(slc_1_parfile.get_value('range_samples'))/2)
        slc_1_7_8_length = int(int(slc_1_parfile.get_value('azimuth_lines'))*(9/10))

        pg.init_offset_orbit(os.path.join(slc_dir,date,date+f'.1.slc.par'),
                             os.path.join(slc_dir,date,date+f'.2.slc.par'),
                             os.path.join(slc_dir,date,date+f'.1-2.off'),'-',slc_1_7_8_length)

        pg.init_offset(os.path.join(slc_dir,date,f'{date}.1.slc'),
                       os.path.join(slc_dir,date,f'{date}.2.slc'),
                       os.path.join(slc_dir,date,f'{date}.1.slc.par'),
                       os.path.join(slc_dir,date,f'{date}.2.slc.par'),
                       os.path.join(slc_dir,date,f'{date}.1-2.off'))

        pg.offset_pwr(os.path.join(slc_dir,date,f'{date}.1.slc'),
                      os.path.join(slc_dir,date,f'{date}.2.slc'),
                      os.path.join(slc_dir,date,f'{date}.1.slc.par'), 
                      os.path.join(slc_dir,date,f'{date}.2.slc.par'),
                      os.path.join(slc_dir,date,f'{date}.1-2.off'),
                      os.path.join(slc_dir,date,f'{date}.1-2.offs'),
                      os.path.join(slc_dir,date,f'{date}.ccp'),
                      32, 32, '-', 1, 128*2*2, 128*2*2, 0.1, 5)

        pg.offset_fit(os.path.join(slc_dir,date,f'{date}.1-2.offs'),
                      os.path.join(slc_dir,date,f'{date}.ccp'),
                      os.path.join(slc_dir,date,f'{date}.1-2.off'),
                      '-', '-', 0.1, 1, 0)

        pg.SLC_cat(os.path.join(slc_dir,date,date+f'.1.slc'), 
                   os.path.join(slc_dir,date,date+f'.2.slc'), 
                   os.path.join(slc_dir,date,date+f'.1.slc.par'), 
                   os.path.join(slc_dir,date,date+f'.2.slc.par'),
                   os.path.join(slc_dir,date,date+f'.1-2.off'), 
                   os.path.join(slc_dir,date,date+f'.1-2.slc'), 
                   os.path.join(slc_dir,date,date+f'.1-2.slc.par'))

        slc_to_tif(os.path.join(slc_dir,date,date+f'.1-2.slc'))

        # Check if date.3.slc exists and combine with 1-2.slc
        if os.path.exists(os.path.join(slc_dir,date,date+f'.3.slc')):
            print(bcolors.OKCYAN+'Combining 1-2.slc with 3.slc'+bcolors.ENDC)

            pg.create_offset(os.path.join(slc_dir,date,date+f'.1-2.slc.par'),
                             os.path.join(slc_dir,date,date+f'.3.slc.par'),
                             os.path.join(slc_dir,date,date+f'.1-2-3.off'),
                             1, 1, 1, 0)

            pg.init_offset_orbit(os.path.join(slc_dir,date,date+f'.1-2.slc.par'),
                                 os.path.join(slc_dir,date,date+f'.3.slc.par'),
                                 os.path.join(slc_dir,date,date+f'.1-2-3.off'))

            pg.init_offset(os.path.join(slc_dir,date,f'{date}.1-2.slc'),
                           os.path.join(slc_dir,date,f'{date}.3.slc'),
                           os.path.join(slc_dir,date,f'{date}.1-2.slc.par'),
                           os.path.join(slc_dir,date,f'{date}.3.slc.par'),
                           os.path.join(slc_dir,date,f'{date}.1-2-3.off'))

            pg.offset_pwr(os.path.join(slc_dir,date,f'{date}.1-2.slc'),
                          os.path.join(slc_dir,date,f'{date}.3.slc'),
                          os.path.join(slc_dir,date,f'{date}.1-2.slc.par'), 
                          os.path.join(slc_dir,date,f'{date}.3.slc.par'),
                          os.path.join(slc_dir,date,f'{date}.1-2-3.off'),
                          os.path.join(slc_dir,date,f'{date}.1-2-3.offs'),
                          os.path.join(slc_dir,date,f'{date}.ccp'),
                          256, 64, '-', 1, 128*2, 128*2, 0.1, 5)

            pg.offset_fit(os.path.join(slc_dir,date,f'{date}.1-2-3.offs'),
                          os.path.join(slc_dir,date,f'{date}.ccp'),
                          os.path.join(slc_dir,date,f'{date}.1-2-3.off'),
                          '-', '-', 0.1, 1, 0)

            pg.SLC_cat(os.path.join(slc_dir,date,date+f'.1-2.slc'), 
                       os.path.join(slc_dir,date,date+f'.3.slc'), 
                       os.path.join(slc_dir,date,date+f'.1-2.slc.par'), 
                       os.path.join(slc_dir,date,date+f'.3.slc.par'),
                       os.path.join(slc_dir,date,date+f'.1-2-3.off'), 
                       os.path.join(slc_dir,date,date+f'.1-2-3.slc'), 
                       os.path.join(slc_dir,date,date+f'.1-2-3.slc.par'))

            slc_to_tif(os.path.join(slc_dir,date,date+f'.1-2-3.slc'))

            shutil.copy(os.path.join(slc_dir,date,date+f'.1-2-3.slc'),os.path.join(slc_dir,date,date+'.slc'))
            shutil.copy(os.path.join(slc_dir,date,date+f'.1-2-3.slc.par'),os.path.join(slc_dir,date,date+'.slc.par')) 
        else:
            shutil.copy(os.path.join(slc_dir,date,date+f'.1-2.slc'),os.path.join(slc_dir,date,date+'.slc'))
            shutil.copy(os.path.join(slc_dir,date,date+f'.1-2.slc.par'),os.path.join(slc_dir,date,date+'.slc.par')) 

    # if cleanup:
    #     intermediate_files = glob(os.path.join(slc_date_dir, f'{date}.*'))
    #     for file in intermediate_files:
    #         if not (file.endswith(f'{date}.slc') or file.endswith(f'{date}.slc.par')):
    #             os.remove(file)
    # return 

def parse_log_file(filepath):
    log_details = {
        "latitude_longitude": [],
        "center_latitude_longitude": None,
        "min_max_latitude": None,
        "min_max_longitude": None,
        "delta_latitude_longitude": None,
        "upper_left_corner": None,
        "lower_right_corner": None,
        "lower_left_corner": None,
        "upper_right_corner": None,
        "warning": None,
        "user_time": None,
        "system_time": None,
        "elapsed_time": None
    }
    with open(filepath, 'r') as file:
        for line in file:
            if "latitude (deg.):" in line and "longitude (deg.):" in line:
                lat_lon = re.findall(r'-?\d+\.\d+', line)
                log_details["latitude_longitude"].append((float(lat_lon[0]), float(lat_lon[1])))
            elif "center latitude (deg.):" in line and "center longitude (deg.):" in line:
                lat_lon = re.findall(r'-?\d+\.\d+', line)
                log_details["center_latitude_longitude"] = (float(lat_lon[0]), float(lat_lon[1]))
            elif "min. latitude (deg.):" in line and "max. latitude (deg.):" in line:
                lat = re.findall(r'-?\d+\.\d+', line)
                log_details["min_max_latitude"] = (float(lat[0]), float(lat[1]))
            elif "min. longitude (deg.):" in line and "max. longitude (deg.):" in line:
                lon = re.findall(r'-?\d+\.\d+', line)
                log_details["min_max_longitude"] = (float(lon[0]), float(lon[1]))
            elif "delta latitude (deg.):" in line and "delta longitude (deg.):" in line:
                delta = re.findall(r'-?\d+\.\d+', line)
                log_details["delta_latitude_longitude"] = (float(delta[0]), float(delta[1]))
            elif "upper left  corner latitude,  longitude (deg.):" in line:
                lat_lon = re.findall(r'-?\d+\.\d+', line)
                log_details["upper_left_corner"] = (float(lat_lon[0]), float(lat_lon[1]))
            elif "lower right corner latitude,  longitude (deg.):" in line:
                lat_lon = re.findall(r'-?\d+\.\d+', line)
                log_details["lower_right_corner"] = (float(lat_lon[0]), float(lat_lon[1]))
            elif "lower left  corner longitude, latitude (deg.):" in line:
                lon_lat = re.findall(r'-?\d+\.\d+', line)
                log_details["lower_left_corner"] = (float(lon_lat[0]), float(lon_lat[1]))
            elif "upper right corner longitude, latitude (deg.):" in line:
                lon_lat = re.findall(r'-?\d+\.\d+', line)
                log_details["upper_right_corner"] = (float(lon_lat[0]), float(lon_lat[1]))
            elif "Warning:" in line:
                log_details["warning"] = line.strip()
            elif "user time (s):" in line:
                log_details["user_time"] = float(re.findall(r'\d+\.\d+', line)[0])
            elif "system time (s):" in line:
                log_details["system_time"] = float(re.findall(r'\d+\.\d+', line)[0])
            elif "elapsed time (s):" in line:
                log_details["elapsed_time"] = float(re.findall(r'\d+\.\d+', line)[0])

    return log_details



def crop_slc(date,config):
    rlks, azlks, dem, demlat, demlon = config["rlks"], config["azlks"], config["dem"], config["demlat"], config["demlon"]
    npat_r, npat_az, r_init, az_init = config["npat_r"], config["npat_az"], config["r_init"], config["az_init"]
    dateM, topdir, slc_dir, dim_dir = config['dateM'], config['topdir'], config["slc_dir"], config["dim_dir"]
    
    min_lat = config['min_lat']
    max_lat = config['max_lat']
    
    slc_par_name = os.path.join(slc_dir, date, f'{date}.slc.par')
    corner_details=parse_log_file(slc_par_name+'.kml.log')

    print(corner_details)
    (y_ul,x_ul) = corner_details['latitude_longitude'][2]
    (y_lr,x_lr) = corner_details['latitude_longitude'][1]

    (y_ll,x_ll) = corner_details['latitude_longitude'][0]
    (y_ur,x_ur) = corner_details['latitude_longitude'][3]

    print('upper left:',y_ul)
    print('upper right', y_ur)
    print('lower left',y_ll)
    print('lower right',y_lr)

    if min_lat == '-':
        min_lat = config['max_lower_right_lat']
        
    else:
        min_lat = float(min_lat)
    if max_lat == '-':
        max_lat = config['min_upper_right_lat']
    else:
        max_lat = float(max_lat)

    if min_lat > max_lat:
        min_lat, max_lat = max_lat, min_lat
        print(f"WARNING: min_lat is greater than max_lat. Swapping values. min_lat: {min_lat}, max_lat: {max_lat}")
    slc_date_dir = os.path.join(slc_dir,date)
    slc_dateM_dir = os.path.join(slc_dir,dateM+'M')
  
    if dateM == date:
        min_lat = min_lat
        max_lat = max_lat
    else:
        min_lat = min_lat
        max_lat = max_lat
        
    slc_name = os.path.join(slc_dir, date, f'{date}.slc')
    slc_par_name = os.path.join(slc_dir, date, f'{date}.slc.par')
    slc_new_name = os.path.join(slc_dir, date, f'{date}.crop.slc')
    slc_par_new_name = os.path.join(slc_dir, date, f'{date}.crop.slc.par')

    if not os.path.exists(slc_par_name+'.kml.log'):
        pg.run_cmd('SLC_corners', slc_par_name, 0, slc_par_name+'.kml', '>', slc_par_name+'.kml.log')

    
    


    slc_par = pg.ParFile(os.path.join(slc_dir,date,date+'.slc.par'))
    slc_width = slc_par.get_value('range_samples')
    slc_length = int(slc_par.get_value('azimuth_lines'))
    slc_heading = slc_par.get_value('heading')

   
    

    print('WANRING: ONLY TESTED FOR ASCENDING DATA')

    end_fraction = ((max_lat-y_lr)/(y_ur-y_lr))
    lower_fraction = ((min_lat-y_lr)/(y_ur-y_lr))
    buffer = 0
    if end_fraction>1:
        end_fraction = 1
        buffer = 0
        print('ERROR: SLC is smaller that max_lat')
    if lower_fraction<0:
        lower_fraction = 0
        buffer = 0
        print('ERROR: SlC is smaller than min_lat')

    
    end_line = int(end_fraction*slc_length)+buffer
    start_line = int(lower_fraction*slc_length)-buffer
    

    if end_line < start_line:
        start_line, end_line = end_line, start_line

    print('total lines:',slc_length)
    print('start line:',start_line)
    print('end line:',end_line)
    
  
    print('fraction of line to end :',end_fraction)
    print('fraction from begininig:',lower_fraction)
    n_crop_lines = end_line-start_line
    print('number of lines to keep:', n_crop_lines)

    pg.SLC_copy(slc_name, slc_par_name, slc_new_name, slc_par_new_name,'-', '-','-','-',start_line, n_crop_lines)
    
    try:
        #
        os.rename(slc_name,slc_name+'.precrop')
        os.rename(slc_par_name,slc_par_name+'.precrop')
        # Rename the original SLC and parameter files
        # os.remove(slc_name)
        # os.remove(slc_par_name)
    

        # Rename the cropped SLC and parameter files to the original names
        
        os.rename(slc_new_name, slc_name)
        os.rename(slc_par_new_name, slc_par_name)

        
    except Exception as e:
        print(f'ERROR during renaming slc files: {e}')

    try:
        slc_to_tif(slc_name+'.precrop')
        slc_to_tif(slc_name)
    except Exception as e:
        print(f'ERROR during converting slc to tif: {e}')


    if config['cleanup']:
        keep_files = [slc_name, 
                      slc_par_name,date+'.slc.par.kml.log',
                      date+'.slc.par.kml',
                      date+'.ccp']
        
        all_files = glob(os.path.join(slc_date_dir, f'{date}.*'))
        for file in all_files:
            if file not in keep_files:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f'ERROR during cleanup of intermediate files: {e}')
    
    return 

def plot_backup_diff(date1,date2,config):
    rlks = config["rlks"]
    azlks = config["azlks"]
    dem = config["dem"]
    demlat = config["demlat"]
    demlon = config["demlon"]
    npat_r = config["npat_r"]
    npat_az = config["npat_az"]
    r_init = config["r_init"]
    az_init = config["az_init"]
    dateM = config['dateM']
    topdir = config['topdir']
    slc_dir = config["slc_dir"]
    dim_dir = config["dim_dir"]
    cleanup = config["cleanup"]

    dateM_mli_par = pg.ParFile(os.path.join(topdir,'slcs',f'{dateM}M',f'{dateM}.mli.par'))
    lengthmli= int(dateM_mli_par.get_value('azimuth_lines')) 
    widthmli=int(dateM_mli_par.get_value('range_samples'))

    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')
    rslc_dir = os.path.join(topdir,'rslc')

    pg.create_offset(os.path.join(ifgm_dir,f'{date1}.rslc2.par'),
                     os.path.join(ifgm_dir,f'{date2}.rslc2.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.2off'),
                     1, rlks, azlks, 0)

    pg.phase_sim_orb(os.path.join(ifgm_dir,f'{date1}.rslc2.par'),
                     os.path.join(ifgm_dir, f'{date2}.rslc2.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.2off'),
                     os.path.join(ifgm_dir, f'{dateM}M.hgt'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.2sim_unw'),
                     os.path.join(slc_dir,f'{dateM}M', f'{dateM}.slc.par'),
                     '-', '-', 1, 1)

    pg.SLC_diff_intf(os.path.join(ifgm_dir,f'{date1}.rslc2'),
                     os.path.join(ifgm_dir,f'{date2}.rslc2'),
                     os.path.join(ifgm_dir,f'{date1}.rslc2.par'),
                     os.path.join(ifgm_dir,f'{date2}.rslc2.par'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.2off'),
                     os.path.join(ifgm_dir, f'{date1}_{date2}.2sim_unw'),
                     os.path.join(ifgm_dir, f'{date1}-{date2}.2diff'),
                     rlks, azlks, 0, 0, 0.2, 1, 1)
  
   
    
    #Adaptive interferogram filter using the power spectral density
    pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.2diff'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2smcc'),
           widthmli, 0.3, 64, 7, '-', 0, '-', 0.2)
    
    #Adaptive interferogram filter using the power spectral density    
    pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm2'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2smcc2'), 
           widthmli, 0.4, 32, 7, '-',0, '-', 0.2)
    

 
    #Adaptive interferogram filter using the power spectral density    
    pg.adf(os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm2'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm3'), 
           os.path.join(ifgm_dir,f'{date1}-{date2}.2smcc3'), 
           widthmli, 0.5, 16, 7, '-', 0, '-', 0.2)
    
    pg.rasmph_pwr(os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm3'), 
                  os.path.join(rslc_dir,f'{date1}',f'{date1}.rslc.mli'),
                  widthmli, 1, 1, 0, 10, 10, 1., .20, 1,
                  os.path.join(ifgm_dir,f'{date1}-{date2}.2diff_sm3.tif'))
    if cleanup:
        for file in [f'{date1}-{date2}.2diff_sm', f'{date1}-{date2}.2smcc', f'{date1}-{date2}.2diff_sm2', f'{date1}-{date2}.2smcc2']:
            try:
                os.remove(os.path.join(ifgm_dir, file))
            except Exception as e:
                print(f'ERROR removing {file}: {e}')
    
 
    

def cleanup_files(date1,date2,config):
    topdir = config['topdir']
    ifgm_dir = os.path.join(topdir,'ifgms',f'{date1}-{date2}')

    # Remove all files in the ifgm_dir except for the 
    print('Clean up files: diff_sm1,smcc1,smcc2,diff_sm2')
    for file in [f'{date1}-{date2}.diff_sm',f'{date1}-{date2}.smcc',f'{date1}-{date2}.diff_sm2',f'{date1}-{date2}.smcc2']:
        try:
            os.remove(os.path.join(ifgm_dir,file))
        except:
            print(f'ERROR removing {file}')
        
    return

def slc_to_tif(slc_name):
    try:
        # Extract range_samples from the parameter file
        with open(slc_name+'.par', 'r') as f:
            for line in f:
                if 'range_samples' in line:
                    range_samples = int(line.split()[1])
                    break

        # Use pg.rasSLC to output the TIFF file
        pg.rasSLC(slc_name, range_samples, '-', '-', 20, 20, '-', '-', '-', 1, '-', slc_name+'.tif')
        return print(f"Finished slc to tif, SLC: {slc_name}")
    except:
        return 0  


