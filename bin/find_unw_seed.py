#!/usr/bin/env python3
from datetime import datetime
import pdb 
import sys
import itertools
import argparse
import re 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from datetime import timedelta
import pdb 
import os 

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

def main(diff_sm2_file, r_init, az_init):

    topdir = os.getcwd()

    date1, date2 = diff_sm2_file.split('/')[-1].split('.')[0].split('-')

    fig, axs = plt.subplots(1, 1, figsize=(20, 20))
    plot_png(diff_sm2_file, ax=axs, radar=True)
    axs.set_title('Coherence Image')
    axs.plot(r_init, az_init, 'r+', markersize=20, markeredgewidth=3)
    fig.savefig(f'{date1}-{date2}_unw_seedpoint.png')
    plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process diff_sm2 file.')
    parser.add_argument('diff_sm2_file', type=str, help='The diff_sm2 file name')
    parser.add_argument('r_init', type=int, help='Initial range value')
    parser.add_argument('az_init', type=int, help='Initial azimuth value')
    if len(sys.argv) == 1:
        print('No arguments provided. Please provide the diff_sm2 file name, initial range, and initial azimuth values.')
        print('Example usage: python find_unw_seed.py example_diff_file.tif 100 200')
        sys.exit(1)
    args = parser.parse_args()
    # Example usage:
    # python find_unw_seed.py example_diff_file.tif 100 200

    main(args.diff_sm2_file, args.r_init, args.az_init)