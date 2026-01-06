"""
Utility functions for TSX supersite GAMMA processing

Common utilities used across different processing stages.
"""

import os
from pathlib import Path
import yaml
import json


def load_config(config_file):
    """
    Load configuration from YAML or JSON file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary with configuration parameters
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    if config_path.suffix in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    elif config_path.suffix == '.json':
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported configuration format: {config_path.suffix}")


def ensure_dir(directory):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_date_from_filename(filename, format='YYYYMMDD'):
    """
    Extract date from TerraSAR-X filename
    
    Args:
        filename: TerraSAR-X filename
        format: Expected date format
        
    Returns:
        Date string or None if not found
    """
    # TerraSAR-X filenames typically contain acquisition date
    # Example: TSX1_SAR__SSC______SM_S_SRA_20200101T120000_20200101T120010
    import re
    
    # Look for YYYYMMDD pattern
    pattern = r'(\d{8})'
    match = re.search(pattern, filename)
    
    if match:
        return match.group(1)
    return None


def calculate_baseline(master_orbit, slave_orbit):
    """
    Calculate perpendicular baseline between two orbits
    
    Args:
        master_orbit: Master orbit parameters (dict with position/velocity)
        slave_orbit: Slave orbit parameters (dict with position/velocity)
        
    Returns:
        Perpendicular baseline in meters
    """
    # Simplified baseline calculation
    # In practice, this would use full orbital state vectors
    # and compute perpendicular baseline at scene center
    
    # Placeholder implementation
    print("Note: Baseline calculation requires full orbital information")
    return 0.0


def read_gamma_par(par_file):
    """
    Read GAMMA parameter file
    
    Args:
        par_file: Path to GAMMA .par file
        
    Returns:
        Dictionary with parameters
    """
    params = {}
    
    try:
        with open(par_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        params[key] = value
    except Exception as e:
        print(f"Error reading parameter file: {e}")
    
    return params


def format_date_pair(date1, date2):
    """
    Format two dates as an interferometric pair string
    
    Args:
        date1: First date (YYYYMMDD)
        date2: Second date (YYYYMMDD)
        
    Returns:
        Formatted pair string (YYYYMMDD_YYYYMMDD)
    """
    return f"{date1}_{date2}"
