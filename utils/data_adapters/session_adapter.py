"""
Session Data Adapter
------------------
Adapter for transforming raw charging session data into standardized format
conforming to our defined session schema.
"""

import pandas as pd
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class SessionAdapter:
    """
    Adapter for converting charging session data from various sources
    into a standardized format conforming to our session schema.
    """
    
    def __init__(self, schema_path: str = "config/data_schemas/session_schema.json"):
        """
        Initialize the adapter with schema validation
        
        Args:
            schema_path: Path to the JSON schema file for sessions
        """
        self.schema_path = schema_path
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the session schema from file"""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load session schema: {e}")
            self.schema = None
    
    def transform_csv_to_standard(self, csv_path: str, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform session data from CSV format to standardized JSON format
        
        Args:
            csv_path: Path to the CSV file containing session data
            mapping: Optional mapping of CSV columns to schema properties
            
        Returns:
            List of standardized session objects
        """
        # Load CSV data
        df = pd.read_csv(csv_path)
        
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the dataframe to standardized format
        return self.transform_df_to_standard(df, mapping)
    
    def transform_json_to_standard(self, json_path: str, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform session data from JSON format to standardized JSON format
        
        Args:
            json_path: Path to the JSON file containing session data
            mapping: Optional mapping of JSON fields to schema properties
            
        Returns:
            List of standardized session objects
        """
        # Load JSON data
        with open(json_path, 'r') as f:
            raw_data = json.load(f)
        
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the JSON to standardized format
        standardized_sessions = []
        
        if isinstance(raw_data, list):
            # If raw_data is a list of sessions
            for item in raw_data:
                session = self._transform_dict(item, mapping)
                if session:
                    standardized_sessions.append(session)
        else:
            # If raw_data is a single session or has a different structure
            session = self._transform_dict(raw_data, mapping)
            if session:
                standardized_sessions.append(session)
        
        return standardized_sessions
    
    def transform_df_to_standard(self, df: pd.DataFrame, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform session data from DataFrame to standardized JSON format
        
        Args:
            df: DataFrame containing session data
            mapping: Optional mapping of DataFrame columns to schema properties
            
        Returns:
            List of standardized session objects
        """
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the dataframe to standardized format
        standardized_sessions = []
        
        for _, row in df.iterrows():
            session = self._transform_row(row, mapping)
            if session:
                standardized_sessions.append(session)
        
        return standardized_sessions
    
    def _transform_row(self, row: pd.Series, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a single DataFrame row to a standardized session object
        
        Args:
            row: DataFrame row containing session data
            mapping: Mapping of DataFrame columns to schema properties
            
        Returns:
            Standardized session object
        """
        session = {}
        
        # Map basic properties
        for schema_key, df_key in mapping.items():
            if df_key in row and not pd.isna(row[df_key]):
                # Handle date-time fields
                if schema_key in ['start_time', 'end_time', 'created_at', 'updated_at']:
                    session[schema_key] = self._format_datetime(row[df_key])
                # Handle numeric fields
                elif schema_key in ['duration_minutes', 'energy_delivered_kwh']:
                    session[schema_key] = float(row[df_key])
                else:
                    session[schema_key] = row[df_key]
        
        # Calculate duration if not present but start and end times are available
        if 'duration_minutes' not in session and 'start_time' in session and 'end_time' in session:
            try:
                start = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(session['end_time'].replace('Z', '+00:00'))
                duration = (end - start).total_seconds() / 60
                session['duration_minutes'] = duration
            except Exception as e:
                print(f"Warning: Failed to calculate duration: {e}")
        
        # If energy data points are available, process them
        energy_keys = [k for k in row.index if 'energy_' in k and '_time' in k]
        power_keys = [k for k in row.index if 'power_' in k and '_time' in k]
        
        if energy_keys or power_keys:
            energy_measurements = []
            
            # Process energy measurement time series if available
            for key in energy_keys:
                if not pd.isna(row[key]):
                    timestamp_key = key
                    value_key = key.replace('_time', '_value')
                    
                    if value_key in row and not pd.isna(row[value_key]):
                        measurement = {
                            "timestamp": self._format_datetime(row[timestamp_key]),
                            "energy_kwh": float(row[value_key])
                        }
                        energy_measurements.append(measurement)
            
            # Process power measurement time series if available
            for key in power_keys:
                if not pd.isna(row[key]):
                    timestamp_key = key
                    value_key = key.replace('_time', '_value')
                    
                    if value_key in row and not pd.isna(row[value_key]):
                        # Try to find a matching measurement or create a new one
                        timestamp = self._format_datetime(row[timestamp_key])
                        found = False
                        
                        for measurement in energy_measurements:
                            if measurement["timestamp"] == timestamp:
                                measurement["power_kw"] = float(row[value_key])
                                found = True
                                break
                        
                        if not found:
                            measurement = {
                                "timestamp": timestamp,
                                "power_kw": float(row[value_key])
                            }
                            energy_measurements.append(measurement)
            
            if energy_measurements:
                session['energy_measurements'] = sorted(
                    energy_measurements, 
                    key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00'))
                )
        
        # Process SoC data if available
        soc_keys = [k for k in row.index if 'soc_' in k and '_time' in k]
        if soc_keys:
            soc_estimates = []
            
            for key in soc_keys:
                if not pd.isna(row[key]):
                    timestamp_key = key
                    value_key = key.replace('_time', '_value')
                    
                    if value_key in row and not pd.isna(row[value_key]):
                        soc_estimate = {
                            "timestamp": self._format_datetime(row[timestamp_key]),
                            "soc_percent": float(row[value_key])
                        }
                        soc_estimates.append(soc_estimate)
            
            if soc_estimates:
                if 'charging_curves' not in session:
                    session['charging_curves'] = {}
                
                session['charging_curves']['soc_estimates'] = sorted(
                    soc_estimates, 
                    key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00'))
                )
        
        # Add vehicle information if available
        vehicle_keys = ['vehicle_make', 'vehicle_model', 'vehicle_year', 'battery_capacity_kwh', 'vehicle_type']
        vehicle_info = {}
        
        for key in vehicle_keys:
            mapped_key = key.replace('vehicle_', '') if key != 'battery_capacity_kwh' else key
            if key in row and not pd.isna(row[key]):
                vehicle_info[mapped_key] = int(row[key]) if mapped_key == 'year' else row[key]
        
        if vehicle_info:
            session['vehicle_info'] = vehicle_info
        
        # Add weather conditions if available
        weather_keys = ['temperature_celsius', 'humidity_percent', 'weather_condition', 'wind_speed_kmh']
        weather_info = {}
        
        for key in weather_keys:
            if key in row and not pd.isna(row[key]):
                weather_info[key] = float(row[key]) if 'percent' in key or 'celsius' in key or 'kmh' in key else row[key]
        
        if weather_info:
            session['weather_conditions'] = weather_info
        
        # Ensure session ID is present
        if 'session_id' not in session:
            # Generate a session ID if not present
            if 'station_id' in session and 'start_time' in session:
                session['session_id'] = f"{session['station_id']}-{session['start_time'].replace(':', '-').replace('.', '-')}"
            else:
                # Generate a random session ID
                import uuid
                session['session_id'] = f"session-{uuid.uuid4()}"
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else [
            'session_id', 'station_id', 'charger_id', 'start_time', 'end_time', 'energy_delivered_kwh'
        ]
        
        if all(field in session for field in required_fields):
            return session
        else:
            missing = [field for field in required_fields if field not in session]
            print(f"Warning: Missing required fields {missing} for session {session.get('session_id', 'unknown')}")
            return None
    
    def _transform_dict(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a dictionary to a standardized session object
        
        Args:
            data: Dictionary containing session data
            mapping: Mapping of dictionary keys to schema properties
            
        Returns:
            Standardized session object
        """
        session = {}
        
        # Map basic properties
        for schema_key, data_key in mapping.items():
            if data_key in data and data[data_key] is not None:
                # Handle date-time fields
                if schema_key in ['start_time', 'end_time', 'created_at', 'updated_at']:
                    session[schema_key] = self._format_datetime(data[data_key])
                # Handle numeric fields
                elif schema_key in ['duration_minutes', 'energy_delivered_kwh']:
                    session[schema_key] = float(data[data_key])
                else:
                    session[schema_key] = data[data_key]
        
        # Handle nested objects and arrays based on the source format
        # The implementation depends on the specific structure of the source data
        # This is a simplified example
        
        # Process energy measurements if they exist in the source data
        if 'energy_data' in data and isinstance(data['energy_data'], list):
            session['energy_measurements'] = []
            for measurement in data['energy_data']:
                if 'timestamp' in measurement and ('power' in measurement or 'energy' in measurement):
                    entry = {"timestamp": self._format_datetime(measurement['timestamp'])}
                    if 'power' in measurement:
                        entry['power_kw'] = float(measurement['power'])
                    if 'energy' in measurement:
                        entry['energy_kwh'] = float(measurement['energy'])
                    session['energy_measurements'].append(entry)
        
        # Process SoC data if it exists in the source data
        if 'soc_data' in data and isinstance(data['soc_data'], list):
            if 'charging_curves' not in session:
                session['charging_curves'] = {}
            
            session['charging_curves']['soc_estimates'] = []
            for soc_point in data['soc_data']:
                if 'timestamp' in soc_point and 'value' in soc_point:
                    session['charging_curves']['soc_estimates'].append({
                        "timestamp": self._format_datetime(soc_point['timestamp']),
                        "soc_percent": float(soc_point['value'])
                    })
        
        # Ensure session ID is present
        if 'session_id' not in session:
            # Generate a session ID if not present
            if 'station_id' in session and 'start_time' in session:
                session['session_id'] = f"{session['station_id']}-{session['start_time'].replace(':', '-').replace('.', '-')}"
            else:
                # Generate a random session ID
                import uuid
                session['session_id'] = f"session-{uuid.uuid4()}"
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else [
            'session_id', 'station_id', 'charger_id', 'start_time', 'end_time', 'energy_delivered_kwh'
        ]
        
        if all(field in session for field in required_fields):
            return session
        else:
            missing = [field for field in required_fields if field not in session]
            print(f"Warning: Missing required fields {missing} for session {session.get('session_id', 'unknown')}")
            return None
    
    def _format_datetime(self, dt_value: Any) -> str:
        """
        Format a datetime value to ISO 8601 format
        
        Args:
            dt_value: Datetime value (string, datetime object, or timestamp)
            
        Returns:
            ISO 8601 formatted datetime string
        """
        if isinstance(dt_value, str):
            # Try parsing the string as a datetime
            try:
                dt = pd.to_datetime(dt_value)
                return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                return dt_value
        elif isinstance(dt_value, (datetime, pd.Timestamp)):
            return dt_value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            # Try converting to datetime
            try:
                dt = pd.to_datetime(dt_value)
                return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                return str(dt_value)
    
    def _get_default_mapping(self) -> Dict[str, str]:
        """
        Get the default mapping from common field names to schema properties
        
        Returns:
            Dictionary mapping schema keys to common field names
        """
        return {
            'session_id': 'session_id',
            'station_id': 'station_id',
            'charger_id': 'charger_id',
            'connector_id': 'connector_id',
            'user_id': 'user_id',
            'vehicle_id': 'vehicle_id',
            'start_time': 'start_time',
            'end_time': 'end_time',
            'duration_minutes': 'duration_minutes',
            'energy_delivered_kwh': 'energy_delivered_kwh',
            'session_status': 'status',
            'authentication_method': 'auth_method',
            'vehicle_make': 'vehicle_make',
            'vehicle_model': 'vehicle_model',
            'vehicle_year': 'vehicle_year',
            'battery_capacity_kwh': 'battery_capacity_kwh',
            'temperature_celsius': 'temperature',
            'humidity_percent': 'humidity',
            'weather_condition': 'weather',
            'wind_speed_kmh': 'wind_speed'
        } 