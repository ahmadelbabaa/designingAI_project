"""
Station Data Adapter
------------------
Adapter for transforming raw station data into standardized format
conforming to our defined station schema.
"""

import pandas as pd
import json
import os
from typing import Dict, Any, List, Optional, Union

class StationAdapter:
    """
    Adapter for converting charging station data from various sources
    into a standardized format conforming to our station schema.
    """
    
    def __init__(self, schema_path: str = "config/data_schemas/station_schema.json"):
        """
        Initialize the adapter with schema validation
        
        Args:
            schema_path: Path to the JSON schema file for stations
        """
        self.schema_path = schema_path
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the station schema from file"""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load station schema: {e}")
            self.schema = None
    
    def transform_csv_to_standard(self, csv_path: str, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform station data from CSV format to standardized JSON format
        
        Args:
            csv_path: Path to the CSV file containing station data
            mapping: Optional mapping of CSV columns to schema properties
            
        Returns:
            List of standardized station objects
        """
        # Load CSV data
        df = pd.read_csv(csv_path)
        
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the dataframe to standardized format
        standardized_stations = []
        
        for _, row in df.iterrows():
            station = self._transform_row(row, mapping)
            if station:
                standardized_stations.append(station)
        
        return standardized_stations
    
    def transform_json_to_standard(self, json_path: str, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform station data from JSON format to standardized JSON format
        
        Args:
            json_path: Path to the JSON file containing station data
            mapping: Optional mapping of JSON fields to schema properties
            
        Returns:
            List of standardized station objects
        """
        # Load JSON data
        with open(json_path, 'r') as f:
            raw_data = json.load(f)
        
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the JSON to standardized format
        standardized_stations = []
        
        if isinstance(raw_data, list):
            # If raw_data is a list of stations
            for item in raw_data:
                station = self._transform_dict(item, mapping)
                if station:
                    standardized_stations.append(station)
        else:
            # If raw_data is a single station or has a different structure
            station = self._transform_dict(raw_data, mapping)
            if station:
                standardized_stations.append(station)
        
        return standardized_stations
    
    def transform_df_to_standard(self, df: pd.DataFrame, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform station data from DataFrame to standardized JSON format
        
        Args:
            df: DataFrame containing station data
            mapping: Optional mapping of DataFrame columns to schema properties
            
        Returns:
            List of standardized station objects
        """
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the dataframe to standardized format
        standardized_stations = []
        
        for _, row in df.iterrows():
            station = self._transform_row(row, mapping)
            if station:
                standardized_stations.append(station)
        
        return standardized_stations
    
    def _transform_row(self, row: pd.Series, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a single DataFrame row to a standardized station object
        
        Args:
            row: DataFrame row containing station data
            mapping: Mapping of DataFrame columns to schema properties
            
        Returns:
            Standardized station object
        """
        station = {}
        
        # Map basic properties
        for schema_key, df_key in mapping.items():
            if df_key in row and not pd.isna(row[df_key]):
                station[schema_key] = row[df_key]
        
        # Special handling for nested objects
        if 'latitude' in row and 'longitude' in row and not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
            if 'location' not in station:
                station['location'] = {}
            
            station['location']['latitude'] = float(row['latitude'])
            station['location']['longitude'] = float(row['longitude'])
            
            # Add address information if available
            for address_field in ['address', 'city', 'state', 'state_province', 'postal_code', 'zip_code', 'country']:
                mapped_field = next((k for k, v in mapping.items() if v == address_field), address_field)
                if mapped_field in row and not pd.isna(row[mapped_field]):
                    field_name = 'state_province' if mapped_field in ['state', 'state_province'] else mapped_field
                    field_name = 'postal_code' if mapped_field in ['postal_code', 'zip_code'] else field_name
                    station['location'][field_name] = row[mapped_field]
        
        # Process chargers if available
        if 'chargers' in station and isinstance(station['chargers'], str):
            try:
                station['chargers'] = json.loads(station['chargers'])
            except:
                # If chargers is not valid JSON, remove it
                del station['chargers']
        
        # If no chargers field exists but we have charger count or type information, create it
        if 'chargers' not in station:
            if 'charger_count' in row and not pd.isna(row['charger_count']):
                charger_count = int(row['charger_count'])
                station['chargers'] = []
                
                # Default values for chargers if specific info not available
                for i in range(charger_count):
                    charger = {
                        "charger_id": f"{station.get('station_id', 'unknown')}-{i+1}",
                        "max_power_kw": 50.0,  # Default value
                        "connectors": [
                            {
                                "connector_id": f"{station.get('station_id', 'unknown')}-{i+1}-1",
                                "type": "Type2"  # Default value
                            }
                        ]
                    }
                    
                    # Add charger type if available
                    if 'charger_type' in row and not pd.isna(row['charger_type']):
                        charger['power_type'] = "DC" if "DC" in str(row['charger_type']) else "AC"
                        
                    # Add connector types if available
                    if 'connector_types' in row and not pd.isna(row['connector_types']):
                        try:
                            connector_types = row['connector_types'].split(',')
                            charger['connectors'] = [
                                {
                                    "connector_id": f"{station.get('station_id', 'unknown')}-{i+1}-{j+1}",
                                    "type": ctype.strip()
                                }
                                for j, ctype in enumerate(connector_types)
                            ]
                        except:
                            pass
                    
                    station['chargers'].append(charger)
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else ['station_id', 'location', 'chargers']
        if all(field in station for field in required_fields):
            return station
        else:
            missing = [field for field in required_fields if field not in station]
            print(f"Warning: Missing required fields {missing} for station {station.get('station_id', 'unknown')}")
            return None
    
    def _transform_dict(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a dictionary to a standardized station object
        
        Args:
            data: Dictionary containing station data
            mapping: Mapping of dictionary keys to schema properties
            
        Returns:
            Standardized station object
        """
        station = {}
        
        # Map basic properties
        for schema_key, data_key in mapping.items():
            if data_key in data and data[data_key] is not None:
                station[schema_key] = data[data_key]
        
        # Special handling for nested objects (similar to _transform_row)
        if 'latitude' in data and 'longitude' in data and data['latitude'] is not None and data['longitude'] is not None:
            if 'location' not in station:
                station['location'] = {}
            
            station['location']['latitude'] = float(data['latitude'])
            station['location']['longitude'] = float(data['longitude'])
            
            # Add address information if available
            for address_field in ['address', 'city', 'state', 'state_province', 'postal_code', 'zip_code', 'country']:
                mapped_field = next((k for k, v in mapping.items() if v == address_field), address_field)
                if mapped_field in data and data[mapped_field] is not None:
                    field_name = 'state_province' if mapped_field in ['state', 'state_province'] else mapped_field
                    field_name = 'postal_code' if mapped_field in ['postal_code', 'zip_code'] else field_name
                    station['location'][field_name] = data[mapped_field]
        
        # Process chargers if available (similar to _transform_row)
        # ... (implementation similar to _transform_row)
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else ['station_id', 'location', 'chargers']
        if all(field in station for field in required_fields):
            return station
        else:
            missing = [field for field in required_fields if field not in station]
            print(f"Warning: Missing required fields {missing} for station {station.get('station_id', 'unknown')}")
            return None
    
    def _get_default_mapping(self) -> Dict[str, str]:
        """
        Get the default mapping from common field names to schema properties
        
        Returns:
            Dictionary mapping schema keys to common field names
        """
        return {
            'station_id': 'station_id',
            'name': 'name',
            'operator': 'operator',
            'owner': 'owner_operator',
            'charger_count': 'charger_count',
            'chargers': 'chargers',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'address': 'address',
            'city': 'city',
            'state_province': 'state',
            'postal_code': 'zip_code',
            'country': 'country',
            'installation_date': 'installation_date',
            'last_maintenance_date': 'last_maintenance_date',
            'network_provider': 'network_provider',
            'charger_type': 'charger_type',
            'connector_types': 'connector_types'
        } 