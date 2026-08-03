#!/usr/bin/env python
import sys
import os
import shutil
import datetime
import ntpath
import getopt
import re
try:
  import py_gamma as pg
except ImportError as e:
  if 'py_gamma' in str(e):
    print('\nERROR: cannot load py_gamma.py')
    print('       setting the environmental variable "PYTHONPATH" in your .bashrc as follows may solve the issue:')
    print('       export PYTHONPATH=.:$GAMMA_HOME:$PYTHONPATH\n')
  else:
    print('\nERROR: ' + str(e))
  sys.exit(1)

def usage(exit_code):
  print("""
usage: SLC_coreg.py <SLC> <SLC_par> <RSLC> <RSLC_par> <RMLI> <RMLI_par> <REF_SLC> <REF_SLC_par> [hgt] [rlks] [azlks] [options]
    SLC           (input) SLC image to be resampled (e.g. 20061003.slc, FCOMPLEX or SCOMPLEX)
    SLC_par       (input) ISP SLC parameter file of SLC (e.g. 20061003.slc.par)
    RSLC          (output) resampled SLC (e.g. 20061003.rslc, same format as SLC)
    RSLC_par      (output) ISP SLC parameter file of resampled SLC (e.g. 20061003.rslc.par)
    RMLI          (output) resampled MLI (e.g. 20061003.rmli, enter - to avoid generating RMLI)
    RMLI_par      (output) ISP MLI parameter file of resampled MLI
                  (e.g. 20061003.rmli.par, enter - to avoid generating RMLI_par)
    REF_SLC       (input) reference SLC image (e.g. 20050812.slc)
    REF_SLC_par   (input) reference SLC parameter file (e.g. 20050812.slc.par)
    hgt           (input) height map in reference MLI geometry (height (m) relative to WGS-84 ellipsoid, FLOAT)
                  or constant height value (enter - for default: 0.1)
    rlks          number of range looks in the output MLI image (enter - for default: 2)
    azlks         number of azimuth looks in the output MLI image (enter - for default: 6)
    
    --sar_mode number   SAR data acquisition mode:
                          0: single-pass interferometry (LT-1 and SuperView-2)
                          1: repeat-pass (default)
    --npoly number      number of model polynomial parameters (1, 3, 4 or 6, default: 3)
    --nr number         number of offset estimates in range direction in intensity matching
                        (default: calculated automatically)
    --naz number        number of offset estimates in azimuth direction in intensity matching
                        (default: calculated automatically)
    --rwin number       range patch size in intensity matching (default: calculated automatically)
    --azwin number      azimuth patch size in intensity matching (default: calculated automatically)
    --thres value       cross-correlation threshold (default: 0.1)
    --imode txt         interpolation mode, \"txt\" is either \"L\" for Lanczos or \"B\" for B-spline (default: Lanczos)
    --order number      Lanczos interpolator order / B-spline degree 4 -> 9 (default: 4)
    --init_offset       perform offset initialization step
    --no_cleaning       keep intermediate files
    
  """)
  print("Python version: " + sys.version)
  sys.exit(exit_code)

def check_output(status, cleaning, tmp_dir):
  if (status != 0):
    print("\nERROR in previous command\n")
    
    if cleaning:
      try:
        shutil.rmtree(tmp_dir)
      except OSError:
        print("\nDeletion of the directory %s failed" % tmp_dir)
      else:
        print("\nSuccessfully deleted the directory %s" % tmp_dir)
    
    sys.exit(1)

def main():
  print('*** SLC_coreg.py: Script to coregister an SLC to a reference SLC ***')
  print('*** Copyright 2024 Gamma Remote Sensing, v1.9 15-Mar-2024 cm/uw/clw ***')
  
  # init values
  t_cur = datetime.datetime.now()
  tmp_dir = 'tmp_dir_coreg_' + str(int(t_cur.hour)) + str(int(t_cur.minute)) + str(int(t_cur.second)) + str(int(t_cur.microsecond))
  cleaning = 1            # 0: no, 1: yes
  init_offset = 0
  hgt_name = '-'
  hgt_file_flag = 0       # flag indicating if height file exists (0: no, 1: yes)
  hgt_val = 0.1
  rlks = 2
  azlks = 6
  npoly = 3
  thres = 0.1
  rwin = None
  azwin = None
  rwin_flag = False
  azwin_flag = False
  nrstep = None
  nazstep = None
  nrstep_flag = False
  nazstep_flag = False
  mode = 0
  order = 4
  RMLI_name = None
  RMLI_par_name = None
  rlks_init = 1
  azlks_init = 1
  sar_mode = 1
  
  # verbose mode
  pg.is_verbose = True
  
  # parse arguments
  if (len(sys.argv) > 9) and re.match(r'-(\.|)\d', sys.argv[9]):  #match - and either .decimal or decimal number, no options -1, -2.... are possible
    sys.argv[9] = " " + sys.argv[9]
    
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "", ["sar_mode=", "npoly=", "nr=", "naz=", "rwin=", "azwin=", "thres=", "imode=", "order=", "init_offset", "no_cleaning"])
  except getopt.GetoptError as err:
    print(str(err))  # will print something like "option -a not recognized"
    usage(1)
  
  if len(args) < 8:
    if len(args) > 0:
      print("\nERROR: insufficient data parameters on the command line")
      usage(1)
    usage(0)

  print("\nSLC_coreg.py arguments: %s" %str(args))
  print("SLC_coreg.py options: %s\n" %str(opts))
  
  # SLC
  SLC_name = args[0]
  
  exists = os.path.isfile(SLC_name)
  if not exists:
    print("\nERROR: %s not found\n" %SLC_name)
    sys.exit(1)

  # SLC_par
  SLC_par_name = args[1]
  
  exists = os.path.isfile(SLC_par_name)
  if not exists:
    print("\nERROR: %s not found\n" %SLC_par_name)
    sys.exit(1)
  
  # RSLC
  RSLC_name = args[2]
  
  # RSLC_par
  RSLC_par_name = args[3]
  
  # RMLI
  if args[4] != "-" and args[5] != "-":
    RMLI_name = args[4]
  
    # RMLI_par
    RMLI_par_name = args[5]
  
  # REF_SLC
  REF_SLC_name = args[6]
  
  exists = os.path.isfile(REF_SLC_name)
  if not exists:
    print("\nERROR: %s not found\n" %REF_SLC_name)
    sys.exit(1)

  # REF_SLC_par
  REF_SLC_par_name = args[7]
  
  exists = os.path.isfile(REF_SLC_par_name)
  if not exists:
    print("\nERROR: %s not found\n" %REF_SLC_par_name)
    sys.exit(1)
  
  # height map
  if len(args) > 8 and args[8] != "-":
    hgt_name = args[8]
  
    exists = os.path.isfile(hgt_name)
    if exists:
      hgt_file_flag = 1
      hgt_val = hgt_name
    else:
      try:
        hgt_val = float(hgt_name)
      except:
        print("\nERROR: invalid entry for hgt: %s\n" %hgt_name)
        sys.exit(1)

  if hgt_file_flag == 1:
    print("using the height file %s" %hgt_name)
  else:
    print("using a constant height value: %f m" %hgt_val)

  # range looks
  if len(args) > 9 and args[9] != "-":
    rlks = int(args[9])
  
  # azimuth looks
  if len(args) > 10 and args[10] != "-":
    azlks = int(args[10])
  
  for o, a in opts:
    # sar_mode
    if (o == "--sar_mode"):
      sar_mode = int(a)
      
      if ((sar_mode != 0) and (sar_mode != 1)):
        print("\nERROR: invalid value for the --sar_mode option")
        sys.exit(1)
    
    # npoly
    elif (o == "--npoly"):
      npoly = int(a)
      
      if ((npoly != 1) and (npoly != 3) and (npoly != 4) and (npoly != 6)):
        print("\nERROR: invalid number of model polynomial parameters: \n" %npoly)
        sys.exit(1)
    
    # nr
    elif (o == "--nr"):
      nrstep = int(a)
      nrstep_flag = True
    
    # naz
    elif (o == "--naz"):
      nazstep = int(a)
      nazstep_flag = True
    
    # rwin
    elif (o == "--rwin"):
      rwin = int(a)
      rwin_flag = True
    
    # azwin
    elif (o == "--azwin"):
      azwin = int(a)
      azwin_flag = True
    
    # azwin
    elif (o == "--thres"):
      thres = a
    
    # interpolation mode
    elif (o == "--imode"):
      if a == "l" or a == "L" or a == "Lanczos" or a == "lanczos":
        mode = 0
      elif a == "b" or a == "B" or a == "bspline" or a == "b-spline" or a == "Bspline" or a == "B-spline":
        mode = 1
      else:
        print("\nERROR: invalid choise for oversampling mode: %s\n" %a)
        sys.exit(1)
    
    # Lanczos interpolator order / B-spline degree
    elif (o == "--order"):
      order = int(a)
    
    # init_offset
    elif (o == "--init_offset"):
      init_offset = 1
    
    # no_cleaning
    elif (o == "--no_cleaning"):
      cleaning = 0
    
    # option not found
    else:
      print("\nERROR: invalid option on the command line: ", o)
      sys.exit(1)
  
  # prepare intermediate file names
  if '.slc' in SLC_name:
    MLI_name = SLC_name.replace('.slc', '.mli')
  else:
    MLI_name = SLC_name + '.mli'
  if '.slc' in SLC_par_name:
    MLI_par_name = SLC_par_name.replace('.slc', '.mli')
  else:
    MLI_par_name = SLC_name + '.mli.par'
  if '.slc' in REF_SLC_name:
    REF_MLI_name = REF_SLC_name.replace('.slc', '.mli')
  elif '.rslc' in REF_SLC_name:
    REF_MLI_name = REF_SLC_name.replace('.rslc', '.rmli')
  else:
    REF_MLI_name = REF_SLC_name + '.mli'
  if '.slc' in REF_SLC_par_name:
    REF_MLI_par_name = REF_SLC_par_name.replace('.slc', '.mli')
  elif '.rslc' in REF_SLC_par_name:
    REF_MLI_par_name = REF_SLC_par_name.replace('.rslc', '.rmli')
  else:
    REF_MLI_par_name = REF_SLC_name + '.mli'
  
  MLI_name = tmp_dir + '/' + ntpath.basename(MLI_name)
  MLI_par_name = tmp_dir + '/' + ntpath.basename(MLI_par_name)
  lt_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.lt'
  lt_fine_name = SLC_name + '.lt_fine'
  MLI_diff_par_name = MLI_name + '.diff_par'
  REF_MLI_name = tmp_dir + '/' + ntpath.basename(REF_MLI_name)
  REF_MLI_par_name = tmp_dir + '/' + ntpath.basename(REF_MLI_par_name)
  MLI_sim_name = MLI_name + '.sim'
  MLI_offs_name = MLI_name + '.offs'
  MLI_offsets_name = MLI_name + '.offsets'
  MLI_snr_name = MLI_name + '.snr'
  MLI_coffs_name = MLI_name + '.coffs'
  MLI_coffsets_name = MLI_name + '.coffsets'
  log1_name = MLI_diff_par_name + '.out'
  SLC_off_par_name = SLC_name + '.off'
  SLC_offs_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.offs'
  SLC_offsets_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.offsets'
  SLC_snr_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.snr'
  SLC_coffs_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.coffs'
  SLC_coffsets_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.coffsets'
  log2_name = tmp_dir + '/' + ntpath.basename(SLC_off_par_name) + '.out'
  SLC_test_off_par_name = tmp_dir + '/' + ntpath.basename(SLC_name) + '.off.test'
  log3_name = SLC_test_off_par_name + '.out'
  
  if RMLI_name is not None and RMLI_par_name is not None:
    RMLI_bmp_name = RMLI_name + '.bmp'
  
  if os.path.isfile(log1_name):
    os.remove(log1_name)
  
  # create temporary directory
  if not os.path.isdir(tmp_dir):
    try:
      os.mkdir(tmp_dir)
    except OSError:
      print("\nERROR: Creation of the directory %s failed\n" % tmp_dir)
      sys.exit(1)
    else:
      print("\nSuccessfully created the directory %s\n" % tmp_dir)
  
  # initialize the output coregistration quality file
  quality_name = RSLC_name + '.coreg_quality'
  quality = open(quality_name, "w+")
  quality.write("SLC coregistration quality file\n")
  quality.write("###############################\n\n")
  
  # write out command used and script versions
  quality.write("command used:\n")
  quality.write("SLC_coreg.py")
  for i in range(1, len(sys.argv)):
    quality.write(" %s" %sys.argv[i])
  quality.write("\n\n")
  quality.write("reference SLC:      %s %s\n" %(REF_SLC_name, REF_SLC_par_name))
  quality.write("co-registered RSLC: %s %s\n" %(RSLC_name, RSLC_par_name))
  if RMLI_name is not None and RMLI_par_name is not None:
    quality.write("co-registered RMLI: %s %s\n" %(RMLI_name, RMLI_par_name))
  quality.write("co-registration lookup table: %s  with refinement in: %s\n" %(lt_fine_name, SLC_off_par_name))
  quality.close()
  
  # generate multilooked images
  status = pg.multi_look(SLC_name, SLC_par_name, MLI_name, MLI_par_name, rlks, azlks)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.multi_look(REF_SLC_name, REF_SLC_par_name, REF_MLI_name, REF_MLI_par_name, rlks, azlks)
  check_output(status, cleaning, tmp_dir)
  
  # read MLI parameter files
  REF_MLI_par = pg.ParFile(REF_MLI_par_name)
  REF_MLI_width = REF_MLI_par.get_value('range_samples', dtype = int, index = 0)
  
  MLI_par = pg.ParFile(MLI_par_name)
  MLI_width = MLI_par.get_value('range_samples', dtype = int, index = 0)
  MLI_nlines = MLI_par.get_value('azimuth_lines', dtype = int, index = 0)
  
  # steps for calculation of MLI offsets
  nr_factor = max(1.0, MLI_width/MLI_nlines)
  naz_factor = max(1.0, MLI_nlines/MLI_width)
  nr_factor = min(4.0, nr_factor)
  naz_factor = min(4.0, naz_factor)

  if not nrstep_flag:
    nrstep = int(32 * nr_factor)
  if not nazstep_flag:
    nazstep = int(32 * naz_factor)
  if not rwin_flag:
    rwin = min(256, int(MLI_width/4)*2)
  if not azwin_flag:
    azwin = min(256, int(MLI_nlines/4)*2)
  
  # determine lookup table based on orbit data and DEM
  status = pg.rdc_trans(REF_MLI_par_name, hgt_val, MLI_par_name, lt_name, sar_mode)
  check_output(status, cleaning, tmp_dir)
  
  # resample reference MLI to second MLI geometry
  status = pg.geocode(lt_name, REF_MLI_name, REF_MLI_width, MLI_sim_name, MLI_width, MLI_nlines, 0, 0)
  check_output(status, cleaning, tmp_dir)
  
  # generate diff_par
  if os.path.isfile(MLI_diff_par_name):
    os.remove(MLI_diff_par_name)
  
  status = pg.create_diff_par(MLI_par_name, '-', MLI_diff_par_name, 1, 0)
  check_output(status, cleaning, tmp_dir)
  
  # calculate initial offset
  if init_offset:
    size_init = min(1024, min(MLI_width, MLI_nlines))
    if size_init == 1024:
      rlks_init = MLI_width // 1024
      azlks_init = MLI_nlines // 1024
    status = pg.init_offsetm(MLI_sim_name, MLI_name, MLI_diff_par_name, rlks_init, azlks_init, '-', '-', '-', '-', 0.1, size_init)
    check_output(status, cleaning, tmp_dir)
  
  # estimate offsets based on MLIs
  status = pg.offset_pwrm(MLI_sim_name, MLI_name, MLI_diff_par_name, MLI_offs_name, MLI_snr_name, min(512, int(MLI_width/4)*2), min(512, int(MLI_nlines/4)*2), MLI_offsets_name, 1, int(12 * nr_factor), int(12 * naz_factor), 0.1)
  
  if status != 0:
    if init_offset:
      check_output(status, cleaning, tmp_dir)
    else:
      # generate diff_par
      if os.path.isfile(MLI_diff_par_name):
        os.remove(MLI_diff_par_name)
      
      status = pg.create_diff_par(MLI_par_name, '-', MLI_diff_par_name, 1, 0)
      check_output(status, cleaning, tmp_dir)
      
      # calculate initial offset
      size_init = min(1024, min(MLI_width, MLI_nlines))
      if size_init == 1024:
        rlks_init = MLI_width // 1024
        azlks_init = MLI_nlines // 1024
      status = pg.init_offsetm(MLI_sim_name, MLI_name, MLI_diff_par_name, rlks_init, azlks_init, '-', '-', '-', '-', 0.1, size_init)
      check_output(status, cleaning, tmp_dir)
      
      status = pg.offset_pwrm(MLI_sim_name, MLI_name, MLI_diff_par_name, MLI_offs_name, MLI_snr_name, min(512, int(MLI_width/4)*2), min(512, int(MLI_nlines/4)*2), MLI_offsets_name, 1, int(12 * nr_factor), int(12 * naz_factor), 0.1)
      check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_fitm(MLI_offs_name, MLI_snr_name, MLI_diff_par_name, MLI_coffs_name, MLI_coffsets_name, thres, 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_pwrm(MLI_sim_name, MLI_name, MLI_diff_par_name, MLI_offs_name, MLI_snr_name, rwin, azwin, MLI_offsets_name, 1, nrstep, nazstep, 0.1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_fitm(MLI_offs_name, MLI_snr_name, MLI_diff_par_name, MLI_coffs_name, MLI_coffsets_name, thres, npoly, logf = log1_name)
  check_output(status, cleaning, tmp_dir)
  
  quality = open(quality_name, "a+")
  quality.write("\n")
  quality.write("first co-registration refinement using MLIs:\n")
  print("first co-registration refinement using MLIs:")
  log1 = open(log1_name, "r")
  for line in log1:
    if 'final' in line and not 'coeff. errors:' in line:
      quality.write("%s"%line)
      print("%s"%line.rstrip())
  print('')
  quality.close()
  log1.close()
  
  # apply offset poly based on MLIs
  status = pg.gc_map_fine(lt_name, REF_MLI_width, MLI_diff_par_name, lt_fine_name, 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.SLC_interp_lt(SLC_name, REF_SLC_par_name, SLC_par_name, lt_fine_name, REF_MLI_par_name, MLI_par_name, '-', RSLC_name, RSLC_par_name, 1024, mode, order)
  check_output(status, cleaning, tmp_dir)
  
  # read SLC parameter files
  REF_SLC_par = pg.ParFile(REF_SLC_par_name)
  REF_SLC_width = REF_SLC_par.get_value('range_samples', dtype = int, index = 0)
  REF_SLC_nlines = REF_SLC_par.get_value('azimuth_lines', dtype = int, index = 0)
  
  # steps for calculation of SLC offsets
  nr_factor = max(1.0, REF_SLC_width/REF_SLC_nlines)
  naz_factor = max(1.0, REF_SLC_nlines/REF_SLC_width)
  nr_factor = min(4.0, nr_factor)
  naz_factor = min(4.0, naz_factor)
  
  if not nrstep_flag:
    nrstep = int(32 * nr_factor)
  if not nazstep_flag:
    nazstep = int(32 * naz_factor)
  if not rwin_flag:
    rwin = min(256, int(REF_SLC_width/4)*2)
  if not azwin_flag:
    azwin = min(256, int(REF_SLC_nlines/4)*2)

  # generate off_par
  if os.path.isfile(SLC_off_par_name):
    os.remove(SLC_off_par_name)
  
  status = pg.create_offset(REF_SLC_par_name, RSLC_par_name, SLC_off_par_name, 1, rlks, azlks, 0)
  check_output(status, cleaning, tmp_dir)
  
  # estimate offsets based on SLCs (already co-registered using MLI based refinement)
  status = pg.offset_pwr(REF_SLC_name, RSLC_name, REF_SLC_par_name, RSLC_par_name, SLC_off_par_name, SLC_offs_name, SLC_snr_name, rwin, azwin, SLC_offsets_name, 2, int(12 * nr_factor), int(12 * naz_factor), 0.1, '-', '-', 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_fit(SLC_offs_name, SLC_snr_name, SLC_off_par_name, SLC_coffs_name, SLC_coffsets_name, thres, 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_pwr(REF_SLC_name, RSLC_name, REF_SLC_par_name, RSLC_par_name, SLC_off_par_name, SLC_offs_name, SLC_snr_name, rwin, azwin, SLC_offsets_name, 2, nrstep, nazstep, 0.1, '-', '-', 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_fit(SLC_offs_name, SLC_snr_name, SLC_off_par_name, SLC_coffs_name, SLC_coffsets_name, thres, npoly, logf = log2_name)
  check_output(status, cleaning, tmp_dir)
  
  quality = open(quality_name, "a+")
  quality.write("\n")
  quality.write("second co-registration refinement using SLCs:\n")
  print("second co-registration refinement using SLCs:")
  log2 = open(log2_name, "r")
  for line in log2:
    if 'final' in line and not 'coeff. errors:' in line:
      quality.write("%s"%line)
      print("%s"%line.rstrip())
  print('')
  quality.close()
  log2.close()
  
  # apply offset poly based on SLCs
  status = pg.SLC_interp_lt(SLC_name, REF_SLC_par_name, SLC_par_name, lt_fine_name, REF_MLI_par_name, MLI_par_name, SLC_off_par_name, RSLC_name, RSLC_par_name, 1024, mode, order)
  check_output(status, cleaning, tmp_dir)
  
  # generate test off_par
  if os.path.isfile(SLC_test_off_par_name):
    os.remove(SLC_test_off_par_name)
  
  status = pg.create_offset(REF_SLC_par_name, RSLC_par_name, SLC_test_off_par_name, 1, rlks, azlks, 0)
  check_output(status, cleaning, tmp_dir)
  
  # estimate offsets after coregistration
  status = pg.offset_pwr(REF_SLC_name, RSLC_name, REF_SLC_par_name, RSLC_par_name, SLC_test_off_par_name, SLC_offs_name, SLC_snr_name, rwin, azwin, SLC_offsets_name, 2, nrstep, nazstep, 0.1, '-', '-', 1)
  check_output(status, cleaning, tmp_dir)
  
  status = pg.offset_fit(SLC_offs_name, SLC_snr_name, SLC_test_off_par_name, SLC_coffs_name, SLC_coffsets_name, thres, 1, logf = log3_name)
  check_output(status, cleaning, tmp_dir)
  
  if RMLI_name is not None and RMLI_par_name is not None:
    RSLC_par = pg.ParFile(RSLC_par_name)
    RSLC_image_format = RSLC_par.get_value('image_format', index = 0)
    if RSLC_image_format == 'SCOMPLEX':
      RSLC_cal_gain = RSLC_par.get_value('calibration_gain', dtype = float, index = 0)
      sc = 10**(-RSLC_cal_gain / 10.0)
    else:
      sc = 1.0
    
    status = pg.multi_look(RSLC_name, RSLC_par_name, RMLI_name, RMLI_par_name, rlks, azlks, '-', '-', sc)
    check_output(status, cleaning, tmp_dir)
    
    status = pg.raspwr(RMLI_name, REF_MLI_width, '-', '-', '-', '-', '-', '-', 'gray.cm', RMLI_bmp_name)
    check_output(status, cleaning, tmp_dir)
  
  quality = open(quality_name, "a+")
  quality.write("\n")
  quality.write("co-registration quality test result:\n")
  print("co-registration quality test result:")
  log3 = open(log3_name, "r")
  for line in log3:
    if 'final' in line:
      quality.write("%s"%line)
      print("%s"%line.rstrip())
  quality.close()
  log3.close()
  
  if cleaning:
    try:
      shutil.rmtree(tmp_dir)
    except OSError:
      print("\ndeletion of the directory %s failed" % tmp_dir)
    else:
      print("\nsuccessfully deleted the directory %s" % tmp_dir)
  
  t_end = datetime.datetime.now()
  delta_t = t_end - t_cur
  print("\nend of SLC_coreg.py, elapsed time (s): %s\n" %(str(delta_t.total_seconds())))
  
  quality = open(quality_name, "a+")
  quality.write("\n")
  quality.write("end of SLC_coreg.py\n")
  quality.write("%s\n\n" %(str(t_end)))
  quality.close()
  
  return 0

if __name__ == "__main__":
  main()
  
