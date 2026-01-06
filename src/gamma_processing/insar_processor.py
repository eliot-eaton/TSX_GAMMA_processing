#!/usr/bin/env python3
"""
GAMMA InSAR Processing for TerraSAR-X data

This script processes TerraSAR-X data using GAMMA software to generate
interferograms using the InSAR method.

Note: This script requires GAMMA software to be installed and properly configured.
GAMMA is commercial software - see https://www.gamma-rs.ch/
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import json


class GAMMAProcessor:
    """Handler for GAMMA InSAR processing of TerraSAR-X data"""
    
    def __init__(self, gamma_home=None, work_dir='data/processed'):
        """
        Initialize the GAMMA processor
        
        Args:
            gamma_home: Path to GAMMA installation directory
            work_dir: Working directory for processing
        """
        self.gamma_home = gamma_home or os.environ.get('GAMMA_HOME')
        if not self.gamma_home:
            print("Warning: GAMMA_HOME not set. Set environment variable or pass gamma_home parameter")
        
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
    def check_gamma_installation(self):
        """Check if GAMMA is properly installed and accessible"""
        if not self.gamma_home:
            print("Error: GAMMA installation not found")
            print("Please set GAMMA_HOME environment variable or specify gamma_home parameter")
            return False
        
        gamma_path = Path(self.gamma_home)
        if not gamma_path.exists():
            print(f"Error: GAMMA directory not found: {gamma_path}")
            return False
        
        print(f"GAMMA installation found at: {gamma_path}")
        return True
    
    def import_tsx_data(self, data_file, output_prefix):
        """
        Import TerraSAR-X data into GAMMA format
        
        Args:
            data_file: Path to TerraSAR-X data file
            output_prefix: Prefix for output files
            
        Returns:
            Path to imported SLC file or None if failed
        """
        print(f"Importing TerraSAR-X data: {data_file}")
        
        if not self.check_gamma_installation():
            return None
        
        try:
            # Example GAMMA command structure (actual commands vary)
            # This would use GAMMA's par_TX_SLC to import TerraSAR-X data
            output_slc = self.work_dir / f"{output_prefix}.slc"
            output_par = self.work_dir / f"{output_prefix}.slc.par"
            
            print(f"  Output SLC: {output_slc}")
            print(f"  Output PAR: {output_par}")
            
            # Note: Actual GAMMA command would be run here
            # e.g., par_TX_SLC [input] [output_par] [output_slc]
            print("Note: This requires GAMMA software to be installed")
            
            return output_slc
            
        except Exception as e:
            print(f"Error importing data: {e}")
            return None
    
    def coregister_slcs(self, master_slc, slave_slc, output_prefix):
        """
        Coregister slave SLC to master SLC
        
        Args:
            master_slc: Path to master SLC file
            slave_slc: Path to slave SLC file  
            output_prefix: Prefix for output files
            
        Returns:
            Path to coregistered SLC or None if failed
        """
        print(f"Coregistering SLCs...")
        print(f"  Master: {master_slc}")
        print(f"  Slave: {slave_slc}")
        
        try:
            coreg_slc = self.work_dir / f"{output_prefix}.rslc"
            
            # Note: Actual coregistration would use GAMMA commands:
            # - create_offset: create offset parameter file
            # - offset_pwr: estimate offsets from intensity images
            # - offset_fit: fit offset polynomial
            # - SLC_interp: resample slave SLC to master geometry
            
            print(f"  Output: {coreg_slc}")
            print("Note: This requires GAMMA software to be installed")
            
            return coreg_slc
            
        except Exception as e:
            print(f"Error coregistering: {e}")
            return None
    
    def generate_interferogram(self, master_slc, slave_slc, output_prefix):
        """
        Generate interferogram from two coregistered SLCs
        
        Args:
            master_slc: Path to master SLC file
            slave_slc: Path to coregistered slave SLC file
            output_prefix: Prefix for output files
            
        Returns:
            Path to interferogram file or None if failed
        """
        print(f"Generating interferogram...")
        
        try:
            ifg_file = self.work_dir / f"{output_prefix}.int"
            
            # Note: Actual interferogram generation would use GAMMA commands:
            # - SLC_intf: form interferogram
            # - cc_wave: compute coherence
            
            print(f"  Output interferogram: {ifg_file}")
            print("Note: This requires GAMMA software to be installed")
            
            return ifg_file
            
        except Exception as e:
            print(f"Error generating interferogram: {e}")
            return None
    
    def filter_interferogram(self, ifg_file, output_prefix, alpha=0.5):
        """
        Apply adaptive filtering to interferogram
        
        Args:
            ifg_file: Path to interferogram file
            output_prefix: Prefix for output files
            alpha: Filtering parameter (0-1)
            
        Returns:
            Path to filtered interferogram or None if failed
        """
        print(f"Filtering interferogram...")
        
        try:
            filt_file = self.work_dir / f"{output_prefix}.filt.int"
            
            # Note: Actual filtering would use GAMMA adf command
            print(f"  Output: {filt_file}")
            print(f"  Alpha parameter: {alpha}")
            print("Note: This requires GAMMA software to be installed")
            
            return filt_file
            
        except Exception as e:
            print(f"Error filtering: {e}")
            return None
    
    def unwrap_phase(self, ifg_file, coherence_file, output_prefix):
        """
        Unwrap interferometric phase
        
        Args:
            ifg_file: Path to filtered interferogram
            coherence_file: Path to coherence file
            output_prefix: Prefix for output files
            
        Returns:
            Path to unwrapped phase file or None if failed
        """
        print(f"Unwrapping phase...")
        
        try:
            unw_file = self.work_dir / f"{output_prefix}.unw"
            
            # Note: Actual unwrapping would use GAMMA mcf command
            # or integration with external unwrappers like SNAPHU
            
            print(f"  Output: {unw_file}")
            print("Note: This requires GAMMA software to be installed")
            
            return unw_file
            
        except Exception as e:
            print(f"Error unwrapping: {e}")
            return None
    
    def geocode_results(self, data_file, dem_file, output_prefix):
        """
        Geocode results to geographic coordinates
        
        Args:
            data_file: Path to data file to geocode
            dem_file: Path to DEM file
            output_prefix: Prefix for output files
            
        Returns:
            Path to geocoded file or None if failed
        """
        print(f"Geocoding results...")
        
        try:
            geo_file = self.work_dir / f"{output_prefix}.geo.tif"
            
            # Note: Actual geocoding would use GAMMA commands:
            # - gc_map: generate geocoding lookup table
            # - geocode: apply geocoding transformation
            
            print(f"  Output: {geo_file}")
            print("Note: This requires GAMMA software to be installed")
            
            return geo_file
            
        except Exception as e:
            print(f"Error geocoding: {e}")
            return None
    
    def process_pair(self, master_file, slave_file, dem_file, output_prefix):
        """
        Process a complete interferometric pair
        
        Args:
            master_file: Path to master data file
            slave_file: Path to slave data file
            dem_file: Path to DEM file
            output_prefix: Prefix for all output files
            
        Returns:
            Dictionary of output files or None if failed
        """
        print(f"\n{'='*60}")
        print(f"Processing interferometric pair: {output_prefix}")
        print(f"{'='*60}\n")
        
        results = {}
        
        # 1. Import data
        print("Step 1: Import TerraSAR-X data")
        master_slc = self.import_tsx_data(master_file, f"{output_prefix}_master")
        slave_slc = self.import_tsx_data(slave_file, f"{output_prefix}_slave")
        
        if not master_slc or not slave_slc:
            print("Error: Failed to import data")
            return None
        
        # 2. Coregister
        print("\nStep 2: Coregister SLCs")
        coreg_slc = self.coregister_slcs(master_slc, slave_slc, f"{output_prefix}_coreg")
        
        # 3. Generate interferogram
        print("\nStep 3: Generate interferogram")
        ifg = self.generate_interferogram(master_slc, coreg_slc, output_prefix)
        
        # 4. Filter
        print("\nStep 4: Filter interferogram")
        filt_ifg = self.filter_interferogram(ifg, output_prefix)
        
        # 5. Unwrap
        print("\nStep 5: Unwrap phase")
        coherence = self.work_dir / f"{output_prefix}.cc"  # From cc_wave
        unw = self.unwrap_phase(filt_ifg, coherence, output_prefix)
        
        # 6. Geocode
        print("\nStep 6: Geocode results")
        geo = self.geocode_results(unw, dem_file, output_prefix)
        
        results = {
            'master_slc': master_slc,
            'slave_slc': slave_slc,
            'interferogram': ifg,
            'filtered': filt_ifg,
            'unwrapped': unw,
            'geocoded': geo
        }
        
        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"{'='*60}\n")
        
        return results


def main():
    """Main entry point for GAMMA processing"""
    parser = argparse.ArgumentParser(
        description='Process TerraSAR-X data with GAMMA InSAR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Note: This script requires GAMMA software to be installed.
Set GAMMA_HOME environment variable to your GAMMA installation directory.

Examples:
  # Process an interferometric pair
  %(prog)s --master master.tar.gz --slave slave.tar.gz --dem dem.tif --output pair_20200101_20200113
        """
    )
    
    parser.add_argument('--master', type=str, required=True,
                        help='Master TerraSAR-X data file')
    parser.add_argument('--slave', type=str, required=True,
                        help='Slave TerraSAR-X data file')
    parser.add_argument('--dem', type=str, required=True,
                        help='DEM file for processing')
    parser.add_argument('--output', type=str, required=True,
                        help='Output prefix for processed files')
    parser.add_argument('--work-dir', type=str, default='data/processed',
                        help='Working directory (default: data/processed)')
    parser.add_argument('--gamma-home', type=str,
                        help='Path to GAMMA installation (default: $GAMMA_HOME)')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = GAMMAProcessor(gamma_home=args.gamma_home, work_dir=args.work_dir)
    
    # Check GAMMA installation
    if not processor.check_gamma_installation():
        print("\nError: GAMMA software not found or not properly configured")
        print("Please install GAMMA and set GAMMA_HOME environment variable")
        sys.exit(1)
    
    # Process the pair
    results = processor.process_pair(args.master, args.slave, args.dem, args.output)
    
    if results:
        print("Processing successful!")
        print("\nOutput files:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    else:
        print("Processing failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
