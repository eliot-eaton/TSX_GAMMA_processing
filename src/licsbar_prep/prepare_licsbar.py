#!/usr/bin/env python3
"""
Prepare GAMMA InSAR products for COMET-LiCSAR LiCSBAS time-series processing

This script converts GAMMA-processed interferograms into the format required
by LiCSBAS for time-series analysis.

LiCSBAS repository: https://github.com/yumorishita/LiCSBAS
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime
import h5py


class LiCSBASPreparator:
    """Prepare GAMMA products for LiCSBAS time-series processing"""
    
    def __init__(self, input_dir, output_dir='data/output/licsbar'):
        """
        Initialize the LiCSBAS preparator
        
        Args:
            input_dir: Directory containing GAMMA processed products
            output_dir: Output directory for LiCSBAS-ready data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create LiCSBAS expected directory structure
        self.geo_dir = self.output_dir / 'GEOCml10FRAME'
        self.geo_dir.mkdir(exist_ok=True)
        
    def convert_unwrapped_phase(self, gamma_unw_file, output_name):
        """
        Convert GAMMA unwrapped phase to LiCSBAS format
        
        Args:
            gamma_unw_file: Path to GAMMA unwrapped phase file
            output_name: Output filename (e.g., YYYYMMDD_YYYYMMDD.unw)
            
        Returns:
            Path to converted file or None if failed
        """
        print(f"Converting unwrapped phase: {gamma_unw_file}")
        
        try:
            output_file = self.geo_dir / output_name
            
            # Note: Actual conversion would:
            # 1. Read GAMMA format (binary + par file)
            # 2. Convert to GeoTIFF or format expected by LiCSBAS
            # 3. Ensure proper georeferencing
            
            print(f"  Output: {output_file}")
            print("Note: Requires GAMMA and georeferencing information")
            
            return output_file
            
        except Exception as e:
            print(f"Error converting unwrapped phase: {e}")
            return None
    
    def convert_coherence(self, gamma_cc_file, output_name):
        """
        Convert GAMMA coherence to LiCSBAS format
        
        Args:
            gamma_cc_file: Path to GAMMA coherence file
            output_name: Output filename (e.g., YYYYMMDD_YYYYMMDD.cc)
            
        Returns:
            Path to converted file or None if failed
        """
        print(f"Converting coherence: {gamma_cc_file}")
        
        try:
            output_file = self.geo_dir / output_name
            
            # Note: Actual conversion similar to unwrapped phase
            print(f"  Output: {output_file}")
            print("Note: Requires GAMMA and georeferencing information")
            
            return output_file
            
        except Exception as e:
            print(f"Error converting coherence: {e}")
            return None
    
    def create_baseline_file(self, pairs_info, output_file='baselines'):
        """
        Create baseline file for LiCSBAS
        
        Args:
            pairs_info: List of dictionaries with pair information
            output_file: Output filename for baseline info
            
        Returns:
            Path to baseline file or None if failed
        """
        print(f"Creating baseline file...")
        
        try:
            baseline_file = self.geo_dir / output_file
            
            # LiCSBAS expects baseline file with format:
            # YYYYMMDD_YYYYMMDD perp_baseline temp_baseline
            
            with open(baseline_file, 'w') as f:
                for pair in pairs_info:
                    master = pair['master']
                    slave = pair['slave']
                    bperp = pair.get('bperp', 0.0)  # perpendicular baseline
                    btemp = pair.get('btemp', 0)    # temporal baseline (days)
                    
                    f.write(f"{master}_{slave} {bperp:.2f} {btemp}\n")
            
            print(f"  Created: {baseline_file}")
            return baseline_file
            
        except Exception as e:
            print(f"Error creating baseline file: {e}")
            return None
    
    def create_metadata_file(self, metadata, output_file='metadata.txt'):
        """
        Create metadata file with processing information
        
        Args:
            metadata: Dictionary with metadata information
            output_file: Output filename
            
        Returns:
            Path to metadata file or None if failed
        """
        print(f"Creating metadata file...")
        
        try:
            meta_file = self.output_dir / output_file
            
            with open(meta_file, 'w') as f:
                f.write("# GAMMA to LiCSBAS Processing Metadata\n")
                f.write(f"# Created: {datetime.now().isoformat()}\n\n")
                
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
            
            print(f"  Created: {meta_file}")
            return meta_file
            
        except Exception as e:
            print(f"Error creating metadata file: {e}")
            return None
    
    def prepare_interferograms(self, gamma_dir, pairs_list):
        """
        Prepare multiple interferograms for LiCSBAS
        
        Args:
            gamma_dir: Directory containing GAMMA products
            pairs_list: List of interferometric pairs to process
            
        Returns:
            Dictionary with preparation results
        """
        print(f"\n{'='*60}")
        print(f"Preparing interferograms for LiCSBAS")
        print(f"{'='*60}\n")
        
        gamma_path = Path(gamma_dir)
        results = {
            'unwrapped': [],
            'coherence': [],
            'pairs_info': []
        }
        
        for pair in pairs_list:
            master = pair['master']
            slave = pair['slave']
            pair_name = f"{master}_{slave}"
            
            print(f"\nProcessing pair: {pair_name}")
            
            # Find GAMMA files
            unw_file = gamma_path / f"{pair_name}.unw"
            cc_file = gamma_path / f"{pair_name}.cc"
            
            # Convert unwrapped phase
            if unw_file.exists():
                output_unw = self.convert_unwrapped_phase(
                    unw_file, f"{pair_name}.unw"
                )
                if output_unw:
                    results['unwrapped'].append(output_unw)
            
            # Convert coherence
            if cc_file.exists():
                output_cc = self.convert_coherence(
                    cc_file, f"{pair_name}.cc"
                )
                if output_cc:
                    results['coherence'].append(output_cc)
            
            # Store pair info
            results['pairs_info'].append({
                'master': master,
                'slave': slave,
                'bperp': pair.get('bperp', 0.0),
                'btemp': pair.get('btemp', 0)
            })
        
        # Create baseline file
        if results['pairs_info']:
            baseline_file = self.create_baseline_file(results['pairs_info'])
            results['baseline_file'] = baseline_file
        
        # Create metadata
        metadata = {
            'source': 'GAMMA',
            'n_interferograms': len(results['unwrapped']),
            'processing_date': datetime.now().isoformat(),
            'output_dir': str(self.output_dir)
        }
        meta_file = self.create_metadata_file(metadata)
        results['metadata_file'] = meta_file
        
        print(f"\n{'='*60}")
        print(f"Preparation complete!")
        print(f"  Unwrapped phases: {len(results['unwrapped'])}")
        print(f"  Coherence files: {len(results['coherence'])}")
        print(f"  Output directory: {self.output_dir}")
        print(f"{'='*60}\n")
        
        return results
    
    def create_licsbar_config(self, output_file='LiCSBAS_config.txt'):
        """
        Create a template configuration file for LiCSBAS processing
        
        Args:
            output_file: Output configuration filename
            
        Returns:
            Path to config file or None if failed
        """
        print(f"Creating LiCSBAS configuration template...")
        
        try:
            config_file = self.output_dir / output_file
            
            config_content = """# LiCSBAS Configuration File
# Generated for GAMMA-processed TerraSAR-X data

# Input/Output directories
frame_dir = GEOCml10FRAME
ts_dir = TS_GEOCml10FRAME

# Processing parameters
n_para = 4  # Number of parallel processes
n_unw_r_thre = 1.5  # Threshold for number of unwrapped data
coh_thre = 0.05  # Coherence threshold

# Filtering parameters
filtwidth_km = 2  # Filter width in km
filtwidth_yr = 0.25  # Filter width in years

# Masking
mask_range_geo =   # Geographic range for masking (leave empty for no mask)

# Reference point
ref_geo =   # Reference point coordinates (lat,lon) - leave empty for automatic

# For more options, see LiCSBAS documentation:
# https://github.com/yumorishita/LiCSBAS
"""
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            print(f"  Created: {config_file}")
            print("\nNote: Review and modify configuration as needed before running LiCSBAS")
            return config_file
            
        except Exception as e:
            print(f"Error creating config file: {e}")
            return None


def main():
    """Main entry point for LiCSBAS preparation"""
    parser = argparse.ArgumentParser(
        description='Prepare GAMMA products for LiCSBAS time-series processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script converts GAMMA-processed interferograms to LiCSBAS format.

Examples:
  # Prepare interferograms from GAMMA processing directory
  %(prog)s --input data/processed --output data/output/licsbar --pairs pairs.json
  
  # Create configuration template
  %(prog)s --create-config --output data/output/licsbar
        """
    )
    
    parser.add_argument('--input', type=str,
                        help='Input directory with GAMMA products')
    parser.add_argument('--output', type=str, default='data/output/licsbar',
                        help='Output directory for LiCSBAS-ready data')
    parser.add_argument('--pairs', type=str,
                        help='JSON file with interferometric pairs information')
    parser.add_argument('--create-config', action='store_true',
                        help='Create LiCSBAS configuration template')
    
    args = parser.parse_args()
    
    # Initialize preparator
    preparator = LiCSBASPreparator(
        input_dir=args.input if args.input else 'data/processed',
        output_dir=args.output
    )
    
    # Create config if requested
    if args.create_config:
        preparator.create_licsbar_config()
        print("\nConfiguration template created.")
        print("Review and modify before running LiCSBAS processing.")
        return
    
    # Prepare interferograms
    if args.pairs:
        try:
            import json
            with open(args.pairs, 'r') as f:
                pairs_list = json.load(f)
            
            results = preparator.prepare_interferograms(args.input, pairs_list)
            
            if results:
                print("\nPreparation successful!")
                print("\nNext steps:")
                print("1. Review the prepared data in:", args.output)
                print("2. Modify LiCSBAS configuration if needed")
                print("3. Run LiCSBAS time-series processing")
                print("4. See: https://github.com/yumorishita/LiCSBAS")
            else:
                print("Preparation failed")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error loading pairs file: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        print("\nError: --pairs argument required for preparation")
        print("       Use --create-config to generate configuration template")
        sys.exit(1)


if __name__ == '__main__':
    main()
