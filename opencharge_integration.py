#!/usr/bin/env python3
"""
OpenChargeMap Integration Module

This module provides functions to fetch and process data from the OpenChargeMap API.
"""

import os
import json
import time
import pandas as pd
import requests
from tqdm import tqdm
import logging

# Import configuration
from opencharge_config import (
    OPENCHARGE_API_KEY,
    OPENCHARGE_POI_ENDPOINT,
    DEFAULT_PARAMS,
    RATE_LIMIT_INTERVAL
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('opencharge_integration')

def fetch_charging_stations(
    country_code=None,
    latitude=None,
    longitude=None,
    distance=10,
    max_results=100,
    output_file="data/charging_stations.csv",
    cache=True
):
    """
    Fetch charging stations from OpenChargeMap API.
    
    Args:
        country_code (str, optional): ISO country code (e.g., 'US', 'GB')
        latitude (float, optional): Center latitude for radius search
        longitude (float, optional): Center longitude for radius search
        distance (int, optional): Search radius in miles
        max_results (int, optional): Maximum number of results to return
        output_file (str, optional): Path to save CSV output
        cache (bool, optional): Whether to use cached data if available
        
    Returns:
        pandas.DataFrame: DataFrame containing charging station data
    """
    # Check if cached data exists and is requested
    if cache and os.path.exists(output_file):
        logger.info(f"Loading cached data from {output_file}")
        return pd.read_csv(output_file)
    
    # Build query parameters
    params = DEFAULT_PARAMS.copy()
    params["maxresults"] = max_results
    
    if country_code:
        params["countrycode"] = country_code
    
    if latitude is not None and longitude is not None:
        params["latitude"] = latitude
        params["longitude"] = longitude
        params["distance"] = distance
        params["distanceunit"] = "miles"
    
    # Make API request
    logger.info(f"Fetching charging station data from OpenChargeMap API")
    logger.info(f"API Key: {OPENCHARGE_API_KEY[:6]}...{OPENCHARGE_API_KEY[-4:]}")
    logger.info(f"Parameters: {params}")
    
    try:
        response = requests.get(OPENCHARGE_POI_ENDPOINT, params=params)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} charging stations")
            
            # Create folder for output if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Save raw data
            raw_output = output_file.replace('.csv', '_raw.json')
            with open(raw_output, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved raw data to {raw_output}")
            
            # Process and save to DataFrame
            df = process_charging_stations(data)
            df.to_csv(output_file, index=False)
            logger.info(f"Saved processed data to {output_file}")
            
            return df
        else:
            logger.error(f"API request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"Error fetching charging station data: {str(e)}")
        return None

def process_charging_stations(data):
    """
    Process raw charging station data from OpenChargeMap API.
    
    Args:
        data (list): Raw data from OpenChargeMap API
        
    Returns:
        pandas.DataFrame: Processed DataFrame
    """
    records = []
    
    for station in data:
        # Extract address info
        address = station.get('AddressInfo', {})
        
        # Extract connections information
        connections = []
        power_kw = 0
        connector_types = []
        
        for conn in station.get('Connections', []):
            if conn.get('PowerKW'):
                power_kw = max(power_kw, conn.get('PowerKW', 0))
            
            if conn.get('ConnectionType', {}).get('Title'):
                connector_types.append(conn.get('ConnectionType', {}).get('Title'))
        
        # Create record
        record = {
            'id': station.get('ID'),
            'name': station.get('AddressInfo', {}).get('Title', 'Unknown'),
            'latitude': address.get('Latitude'),
            'longitude': address.get('Longitude'),
            'address': address.get('AddressLine1', ''),
            'city': address.get('Town', ''),
            'state': address.get('StateOrProvince', ''),
            'postcode': address.get('Postcode', ''),
            'country': address.get('Country', {}).get('Title', ''),
            'power_kw': power_kw,
            'connector_types': ', '.join(set(connector_types)),
            'access_type': station.get('UsageType', {}).get('Title', 'Unknown'),
            'operator': station.get('OperatorInfo', {}).get('Title', 'Unknown'),
            'network': station.get('OperatorInfo', {}).get('Title', 'Unknown'),
            'status': station.get('StatusType', {}).get('Title', 'Unknown'),
        }
        
        records.append(record)
    
    return pd.DataFrame(records)

def fetch_charging_stations_batch(locations, output_dir="data/charging_stations"):
    """
    Fetch charging stations for multiple locations.
    
    Args:
        locations (list): List of dicts with location info:
            - name: Name of the location
            - latitude: Latitude
            - longitude: Longitude
            - country_code: Country code (optional)
            - distance: Search radius in miles (optional)
        output_dir (str): Directory to save output files
        
    Returns:
        dict: Dict mapping location names to DataFrames
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    
    for location in tqdm(locations, desc="Fetching charging stations"):
        name = location['name']
        output_file = f"{output_dir}/{name.lower().replace(' ', '_')}.csv"
        
        logger.info(f"Fetching data for {name}")
        
        # Respect rate limiting
        time.sleep(RATE_LIMIT_INTERVAL)
        
        df = fetch_charging_stations(
            country_code=location.get('country_code'),
            latitude=location.get('latitude'),
            longitude=location.get('longitude'),
            distance=location.get('distance', 10),
            output_file=output_file
        )
        
        if df is not None:
            results[name] = df
    
    return results

def load_multiple_regions(regions, data_dir="data/charging_stations"):
    """
    Load data for multiple regions from CSV files.
    
    Args:
        regions (list): List of region names
        data_dir (str): Directory containing CSV files
        
    Returns:
        pandas.DataFrame: Combined DataFrame with region column
    """
    dfs = []
    
    for region in regions:
        file_path = f"{data_dir}/{region.lower().replace(' ', '_')}.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['region'] = region
            dfs.append(df)
        else:
            logger.warning(f"Data file not found for region: {region}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None

if __name__ == "__main__":
    # Example usage - fetch charging stations in major cities
    cities = [
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "country_code": "US"},
        {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437, "country_code": "US"},
        {"name": "Chicago", "latitude": 41.8781, "longitude": -87.6298, "country_code": "US"},
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278, "country_code": "GB"},
        {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522, "country_code": "FR"},
    ]
    
    # Fetch data for all cities
    result = fetch_charging_stations_batch(cities)
    print(f"Fetched data for {len(result)} cities")
    
    # Load combined data
    city_names = [city["name"] for city in cities]
    combined_df = load_multiple_regions(city_names)
    
    if combined_df is not None:
        combined_df.to_csv("data/all_charging_stations.csv", index=False)
        print(f"Saved combined data with {len(combined_df)} stations") 