"""
Data Loader
----------
Module for loading and transforming various data sources into standardized formats
using our adapters and registering them with the unified data repository.
"""

import os
import pandas as pd
import json
import glob
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from utils.unified_data_repository import UnifiedDataRepository
from utils.data_adapters.station_adapter import StationAdapter
from utils.data_adapters.session_adapter import SessionAdapter
from utils.data_adapters.forecast_adapter import ForecastAdapter

class DataLoader:
    """
    Data loader for transforming and loading various data sources
    into the unified data repository.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data loader
        
        Args:
            data_dir: Base directory containing the data files
        """
        self.data_dir = data_dir
        self.repository = UnifiedDataRepository()
        
        # Initialize adapters
        self.station_adapter = StationAdapter()
        self.session_adapter = SessionAdapter()
        self.forecast_adapter = ForecastAdapter()
    
    def load_all_data(self) -> None:
        """Load all available data from the data directory"""
        self.load_stations()
        self.load_sessions()
        self.load_forecasts()
    
    def load_stations(self) -> None:
        """Load and transform charging station data"""
        print("Loading charging station data...")
        
        # Look for station data files
        station_files = []
        station_files.extend(glob.glob(os.path.join(self.data_dir, "*stations*.csv")))
        station_files.extend(glob.glob(os.path.join(self.data_dir, "*stations*.json")))
        station_files.extend(glob.glob(os.path.join(self.data_dir, "charging_stations", "*.csv")))
        station_files.extend(glob.glob(os.path.join(self.data_dir, "charging_stations", "*.json")))
        station_files.extend(glob.glob(os.path.join(self.data_dir, "stations", "*.csv")))
        station_files.extend(glob.glob(os.path.join(self.data_dir, "stations", "*.json")))
        
        if not station_files:
            print("No station data files found.")
            return
        
        all_stations = []
        
        for file_path in station_files:
            print(f"  Processing {file_path}...")
            
            try:
                if file_path.endswith(".csv"):
                    stations = self.station_adapter.transform_csv_to_standard(file_path)
                elif file_path.endswith(".json"):
                    stations = self.station_adapter.transform_json_to_standard(file_path)
                else:
                    print(f"  Unsupported file format: {file_path}")
                    continue
                
                print(f"  Transformed {len(stations)} stations from {file_path}")
                all_stations.extend(stations)
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")
        
        if all_stations:
            # Create a DataFrame from the standardized stations
            stations_df = pd.DataFrame(all_stations)
            
            # Register the dataset with the repository
            self.repository.register_dataset(
                "stations", 
                stations_df, 
                metadata={
                    "description": "Standardized charging station data",
                    "source_files": station_files,
                    "record_count": len(stations_df),
                    "schema": "station_schema.json",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            print(f"Registered {len(stations_df)} stations in the repository.")
        else:
            print("No station data was successfully processed.")
    
    def load_sessions(self) -> None:
        """Load and transform charging session data"""
        print("Loading charging session data...")
        
        # Look for session data files
        session_files = []
        session_files.extend(glob.glob(os.path.join(self.data_dir, "*session*.csv")))
        session_files.extend(glob.glob(os.path.join(self.data_dir, "*session*.json")))
        session_files.extend(glob.glob(os.path.join(self.data_dir, "*charging*.csv")))
        session_files.extend(glob.glob(os.path.join(self.data_dir, "*usage*.csv")))
        session_files.extend(glob.glob(os.path.join(self.data_dir, "sessions", "*.csv")))
        session_files.extend(glob.glob(os.path.join(self.data_dir, "sessions", "*.json")))
        
        if not session_files:
            print("No session data files found.")
            return
        
        all_sessions = []
        
        for file_path in session_files:
            print(f"  Processing {file_path}...")
            
            try:
                if file_path.endswith(".csv"):
                    sessions = self.session_adapter.transform_csv_to_standard(file_path)
                elif file_path.endswith(".json"):
                    sessions = self.session_adapter.transform_json_to_standard(file_path)
                else:
                    print(f"  Unsupported file format: {file_path}")
                    continue
                
                print(f"  Transformed {len(sessions)} sessions from {file_path}")
                all_sessions.extend(sessions)
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")
        
        if all_sessions:
            # Create a DataFrame from the standardized sessions
            sessions_df = pd.DataFrame(all_sessions)
            
            # Register the dataset with the repository
            self.repository.register_dataset(
                "sessions", 
                sessions_df, 
                metadata={
                    "description": "Standardized charging session data",
                    "source_files": session_files,
                    "record_count": len(sessions_df),
                    "schema": "session_schema.json",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            print(f"Registered {len(sessions_df)} sessions in the repository.")
        else:
            print("No session data was successfully processed.")
    
    def load_forecasts(self) -> None:
        """Load and transform forecast data"""
        print("Loading forecast data...")
        
        # Look for forecast data files
        forecast_files = []
        forecast_files.extend(glob.glob(os.path.join(self.data_dir, "*forecast*.csv")))
        forecast_files.extend(glob.glob(os.path.join(self.data_dir, "*forecast*.json")))
        forecast_files.extend(glob.glob(os.path.join(self.data_dir, "forecasts", "*.csv")))
        forecast_files.extend(glob.glob(os.path.join(self.data_dir, "forecasts", "*.json")))
        
        if not forecast_files:
            print("No forecast data files found.")
            return
        
        all_forecasts = []
        
        for file_path in forecast_files:
            print(f"  Processing {file_path}...")
            
            try:
                if file_path.endswith(".csv"):
                    forecasts = self.forecast_adapter.transform_csv_to_standard(file_path)
                elif file_path.endswith(".json"):
                    forecasts = self.forecast_adapter.transform_json_to_standard(file_path)
                else:
                    print(f"  Unsupported file format: {file_path}")
                    continue
                
                print(f"  Transformed {len(forecasts)} forecasts from {file_path}")
                all_forecasts.extend(forecasts)
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")
        
        if all_forecasts:
            # Create a DataFrame from the standardized forecasts
            # For forecasts, we'll keep the list of dictionaries format since each forecast
            # may have a different structure with nested arrays
            
            # Register the dataset with the repository
            self.repository.register_dataset(
                "forecasts", 
                all_forecasts, 
                metadata={
                    "description": "Standardized forecast data",
                    "source_files": forecast_files,
                    "record_count": len(all_forecasts),
                    "schema": "forecast_schema.json",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            print(f"Registered {len(all_forecasts)} forecasts in the repository.")
        else:
            print("No forecast data was successfully processed.")
    
    def load_specific_file(self, file_path: str, dataset_id: str, data_type: str) -> None:
        """
        Load and transform a specific file
        
        Args:
            file_path: Path to the file to load
            dataset_id: ID to use when registering the dataset
            data_type: Type of data ('station', 'session', or 'forecast')
        """
        print(f"Loading {data_type} data from {file_path}...")
        
        try:
            if data_type.lower() == 'station':
                adapter = self.station_adapter
                schema = "station_schema.json"
                description = "Standardized charging station data"
            elif data_type.lower() == 'session':
                adapter = self.session_adapter
                schema = "session_schema.json"
                description = "Standardized charging session data"
            elif data_type.lower() == 'forecast':
                adapter = self.forecast_adapter
                schema = "forecast_schema.json"
                description = "Standardized forecast data"
            else:
                print(f"Unsupported data type: {data_type}")
                return
            
            if file_path.endswith(".csv"):
                transformed_data = adapter.transform_csv_to_standard(file_path)
            elif file_path.endswith(".json"):
                transformed_data = adapter.transform_json_to_standard(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                return
            
            if data_type.lower() in ['station', 'session']:
                # Convert to DataFrame for stations and sessions
                transformed_data = pd.DataFrame(transformed_data)
            
            # Register the dataset with the repository
            self.repository.register_dataset(
                dataset_id, 
                transformed_data, 
                metadata={
                    "description": description,
                    "source_file": file_path,
                    "record_count": len(transformed_data),
                    "schema": schema,
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            print(f"Registered {len(transformed_data)} {data_type}s as '{dataset_id}' in the repository.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load and transform data into the unified data repository")
    parser.add_argument("--data-dir", type=str, default="data", help="Base directory containing the data files")
    parser.add_argument("--all", action="store_true", help="Load all available data")
    parser.add_argument("--stations", action="store_true", help="Load charging station data")
    parser.add_argument("--sessions", action="store_true", help="Load charging session data")
    parser.add_argument("--forecasts", action="store_true", help="Load forecast data")
    parser.add_argument("--file", type=str, help="Load a specific file")
    parser.add_argument("--type", type=str, choices=["station", "session", "forecast"], help="Type of data when loading a specific file")
    parser.add_argument("--dataset-id", type=str, help="Dataset ID to use when loading a specific file")
    
    args = parser.parse_args()
    
    loader = DataLoader(data_dir=args.data_dir)
    
    if args.all:
        loader.load_all_data()
    else:
        if args.stations:
            loader.load_stations()
        if args.sessions:
            loader.load_sessions()
        if args.forecasts:
            loader.load_forecasts()
        if args.file:
            if not args.type:
                print("Error: --type is required when loading a specific file")
            elif not args.dataset_id:
                print("Error: --dataset-id is required when loading a specific file")
            else:
                loader.load_specific_file(args.file, args.dataset_id, args.type) 