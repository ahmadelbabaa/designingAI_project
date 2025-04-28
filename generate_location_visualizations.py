#!/usr/bin/env python3
"""
Generate Location-Based EV Charging Visualizations
This script is a simple command-line tool to generate visualizations for a specific location.
"""

import argparse
import sys
import subprocess

def main():
    """Main entry point for the location-based visualization generator"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate EV charging pattern visualizations for a specific location',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Add command line arguments
    parser.add_argument(
        'location', 
        type=str, 
        help='Location to analyze (city name, region, or station ID)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Display detailed progress information'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.location:
        print("Error: Location must be specified")
        parser.print_help()
        sys.exit(1)
    
    # Run the analysis for the specified location
    print(f"Generating visualizations for location: {args.location}")
    try:
        cmd = ["python3", "test_charging_patterns.py", "--location", args.location]
        if args.verbose:
            # The test script already has detailed output
            pass
            
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=not args.verbose)
        
        if not args.verbose:
            print(f"Analysis for {args.location} completed successfully. Check output/charging_patterns/ for visualization files.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating visualizations: {e}")
        if e.stdout:
            print(f"Output: {e.stdout.decode('utf-8')}")
        if e.stderr:
            print(f"Error: {e.stderr.decode('utf-8')}")
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 