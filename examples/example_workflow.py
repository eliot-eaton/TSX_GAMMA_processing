#!/usr/bin/env python3
"""
Example workflow script for TSX Supersite GAMMA Processing

This script demonstrates a complete workflow from download to LiCSBAS preparation.
Adapt this script for your specific processing needs.
"""

import os
import sys
from pathlib import Path
import argparse

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from download.tsx_downloader import TSXDownloader
from gamma_processing.insar_processor import GAMMAProcessor
from licsbar_prep.prepare_licsbar import LiCSBASPreparator


def example_workflow(config):
    """
    Run a complete processing workflow
    
    Args:
        config: Dictionary with configuration parameters
    """
    print("="*70)
    print("TSX Supersite GAMMA Processing - Example Workflow")
    print("="*70)
    
    # Step 1: Download TerraSAR-X data
    print("\n" + "="*70)
    print("Step 1: Download TerraSAR-X Data")
    print("="*70)
    
    downloader = TSXDownloader(
        username=config.get('username'),
        password=config.get('password'),
        output_dir=config.get('raw_dir', 'data/raw')
    )
    
    # Example search
    bbox = config.get('bbox', [10.0, 45.0, 11.0, 46.0])
    start_date = config.get('start_date', '2020-01-01')
    end_date = config.get('end_date', '2020-12-31')
    
    products = downloader.search_data(bbox, start_date, end_date)
    
    if products:
        print(f"Found {len(products)} products")
        # Download first few products as example
        downloader.download_batch(products[:3])
    else:
        print("Note: No products found (EOC credentials required)")
    
    # Step 2: Process with GAMMA
    print("\n" + "="*70)
    print("Step 2: GAMMA InSAR Processing")
    print("="*70)
    
    processor = GAMMAProcessor(
        gamma_home=config.get('gamma_home'),
        work_dir=config.get('work_dir', 'data/processed')
    )
    
    # Check GAMMA installation
    if processor.check_gamma_installation():
        print("GAMMA installation found")
        
        # Example: Process a pair
        master_file = config.get('master_file', 'data/raw/master.tar.gz')
        slave_file = config.get('slave_file', 'data/raw/slave.tar.gz')
        dem_file = config.get('dem_file', 'data/dem/dem.tif')
        
        if Path(master_file).exists() and Path(slave_file).exists():
            results = processor.process_pair(
                master_file, slave_file, dem_file,
                output_prefix='example_pair'
            )
            
            if results:
                print("Processing successful!")
        else:
            print(f"Note: Example data files not found")
            print(f"  Expected: {master_file}, {slave_file}")
    else:
        print("Note: GAMMA not installed - skipping processing")
    
    # Step 3: Prepare for LiCSBAS
    print("\n" + "="*70)
    print("Step 3: Prepare for LiCSBAS")
    print("="*70)
    
    preparator = LiCSBASPreparator(
        input_dir=config.get('work_dir', 'data/processed'),
        output_dir=config.get('output_dir', 'data/output/licsbar')
    )
    
    # Create configuration template
    preparator.create_licsbar_config()
    
    # Example pairs (would normally come from processing)
    example_pairs = [
        {'master': '20200101', 'slave': '20200113', 'bperp': 45.2, 'btemp': 12},
        {'master': '20200113', 'slave': '20200125', 'bperp': 67.8, 'btemp': 12},
    ]
    
    # Create baseline file
    preparator.create_baseline_file(example_pairs)
    
    print("\n" + "="*70)
    print("Workflow Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review downloaded data in:", config.get('raw_dir', 'data/raw'))
    print("2. Run GAMMA processing on your data")
    print("3. Prepare for LiCSBAS using prepare_licsbar.py")
    print("4. Run LiCSBAS time-series processing")
    print("\nSee WORKFLOW.md for detailed instructions")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Example workflow for TSX GAMMA processing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--bbox', nargs=4, type=float,
                        metavar=('MIN_LON', 'MIN_LAT', 'MAX_LON', 'MAX_LAT'),
                        default=[10.0, 45.0, 11.0, 46.0],
                        help='Bounding box')
    parser.add_argument('--start', type=str, default='2020-01-01',
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2020-12-31',
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--username', type=str,
                        help='EOC username')
    parser.add_argument('--password', type=str,
                        help='EOC password')
    parser.add_argument('--gamma-home', type=str,
                        help='GAMMA installation directory')
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        'bbox': args.bbox,
        'start_date': args.start,
        'end_date': args.end,
        'username': args.username,
        'password': args.password,
        'gamma_home': args.gamma_home,
        'raw_dir': 'data/raw',
        'work_dir': 'data/processed',
        'output_dir': 'data/output/licsbar',
    }
    
    # Run workflow
    example_workflow(config)


if __name__ == '__main__':
    main()
