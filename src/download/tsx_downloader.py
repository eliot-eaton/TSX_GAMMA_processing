#!/usr/bin/env python3
"""
Download TerraSAR-X data from EOC Geoservice

This script downloads TerraSAR-X satellite data from the EOC (Earth Observation Center)
Geoservice for specified geographic regions and time periods.
"""

import os
import sys
import argparse
import requests
from datetime import datetime
import json
from pathlib import Path
import time
from tqdm import tqdm


class TSXDownloader:
    """Handler for downloading TerraSAR-X data from EOC Geoservice"""
    
    def __init__(self, username=None, password=None, output_dir='data/raw'):
        """
        Initialize the TSX downloader
        
        Args:
            username: EOC Geoservice username
            password: EOC Geoservice password
            output_dir: Directory to save downloaded files
        """
        self.username = username
        self.password = password
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # EOC Geoservice base URLs (placeholders - actual URLs depend on service)
        self.base_url = "https://download.geoservice.dlr.de"
        self.search_url = f"{self.base_url}/search"
        self.download_url = f"{self.base_url}/download"
        
    def search_data(self, bbox, start_date, end_date, product_type='SSC'):
        """
        Search for available TerraSAR-X data
        
        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            start_date: Start date as string (YYYY-MM-DD)
            end_date: End date as string (YYYY-MM-DD)
            product_type: Product type (SSC, MGD, GEC, EEC)
            
        Returns:
            List of product IDs available for download
        """
        print(f"Searching for TerraSAR-X data...")
        print(f"  Area: {bbox}")
        print(f"  Time: {start_date} to {end_date}")
        print(f"  Product type: {product_type}")
        
        # Query parameters for search
        params = {
            'bbox': ','.join(map(str, bbox)),
            'start': start_date,
            'end': end_date,
            'product': product_type,
            'mission': 'TSX'
        }
        
        try:
            # Note: Actual implementation requires valid EOC credentials and API
            # This is a template that should be adapted to the actual service
            print("Note: This requires valid EOC Geoservice credentials")
            print("Please configure authentication before use")
            
            # Placeholder for actual search logic
            products = []
            print(f"Found {len(products)} products")
            return products
            
        except Exception as e:
            print(f"Error searching for data: {e}")
            return []
    
    def download_product(self, product_id, output_file=None):
        """
        Download a specific TerraSAR-X product
        
        Args:
            product_id: Product identifier
            output_file: Optional output filename
            
        Returns:
            Path to downloaded file or None if failed
        """
        if output_file is None:
            output_file = self.output_dir / f"{product_id}.tar.gz"
        
        print(f"Downloading product: {product_id}")
        print(f"  Output: {output_file}")
        
        try:
            # Note: Actual implementation requires valid EOC credentials and API
            # This is a template that should be adapted to the actual service
            print("Note: This requires valid EOC Geoservice credentials")
            print("Please configure authentication before use")
            
            # Placeholder for actual download logic
            # In a real implementation, this would:
            # 1. Authenticate with the service
            # 2. Request the product
            # 3. Download with progress bar
            # 4. Verify download integrity
            
            return None
            
        except Exception as e:
            print(f"Error downloading product: {e}")
            return None
    
    def download_batch(self, product_ids):
        """
        Download multiple products
        
        Args:
            product_ids: List of product identifiers
            
        Returns:
            List of successfully downloaded file paths
        """
        downloaded_files = []
        
        print(f"Downloading {len(product_ids)} products...")
        for product_id in tqdm(product_ids):
            result = self.download_product(product_id)
            if result:
                downloaded_files.append(result)
            time.sleep(1)  # Be nice to the server
        
        print(f"Successfully downloaded {len(downloaded_files)} products")
        return downloaded_files


def main():
    """Main entry point for the download script"""
    parser = argparse.ArgumentParser(
        description='Download TerraSAR-X data from EOC Geoservice',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for data in a specific area and time range
  %(prog)s --bbox 10.0 45.0 11.0 46.0 --start 2020-01-01 --end 2020-12-31
  
  # Download specific product
  %(prog)s --product TSX1_SAR__SSC______SM_S_SRA_20200101T120000_20200101T120010
        """
    )
    
    parser.add_argument('--bbox', nargs=4, type=float, metavar=('MIN_LON', 'MIN_LAT', 'MAX_LON', 'MAX_LAT'),
                        help='Bounding box for search area')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--product', type=str, help='Specific product ID to download')
    parser.add_argument('--product-type', type=str, default='SSC',
                        choices=['SSC', 'MGD', 'GEC', 'EEC'],
                        help='Product type (default: SSC)')
    parser.add_argument('--output-dir', type=str, default='data/raw',
                        help='Output directory for downloads (default: data/raw)')
    parser.add_argument('--username', type=str, help='EOC Geoservice username')
    parser.add_argument('--password', type=str, help='EOC Geoservice password')
    parser.add_argument('--config', type=str, help='Configuration file with credentials')
    
    args = parser.parse_args()
    
    # Load credentials from config file if provided
    username = args.username
    password = args.password
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                username = config.get('username', username)
                password = config.get('password', password)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Initialize downloader
    downloader = TSXDownloader(username=username, password=password, output_dir=args.output_dir)
    
    # Execute requested operation
    if args.product:
        # Download specific product
        downloader.download_product(args.product)
    elif args.bbox and args.start and args.end:
        # Search and download
        products = downloader.search_data(args.bbox, args.start, args.end, args.product_type)
        if products:
            downloader.download_batch(products)
        else:
            print("No products found matching search criteria")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
