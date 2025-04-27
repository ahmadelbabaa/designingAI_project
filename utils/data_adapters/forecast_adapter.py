"""
Forecast Data Adapter
------------------
Adapter for transforming raw forecast data into standardized format
conforming to our defined forecast schema.
"""

import pandas as pd
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

class ForecastAdapter:
    """
    Adapter for converting forecast data from various sources
    into a standardized format conforming to our forecast schema.
    """
    
    def __init__(self, schema_path: str = "config/data_schemas/forecast_schema.json"):
        """
        Initialize the adapter with schema validation
        
        Args:
            schema_path: Path to the JSON schema file for forecasts
        """
        self.schema_path = schema_path
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the forecast schema from file"""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load forecast schema: {e}")
            self.schema = None
    
    def transform_csv_to_standard(self, csv_path: str, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform forecast data from CSV format to standardized JSON format
        
        Args:
            csv_path: Path to the CSV file containing forecast data
            mapping: Optional mapping of CSV columns to schema properties
            
        Returns:
            List of standardized forecast objects
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
        Transform forecast data from JSON format to standardized JSON format
        
        Args:
            json_path: Path to the JSON file containing forecast data
            mapping: Optional mapping of JSON fields to schema properties
            
        Returns:
            List of standardized forecast objects
        """
        # Load JSON data
        with open(json_path, 'r') as f:
            raw_data = json.load(f)
        
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Transform the JSON to standardized format
        standardized_forecasts = []
        
        if isinstance(raw_data, list):
            # If raw_data is a list of forecasts
            for item in raw_data:
                forecast = self._transform_dict(item, mapping)
                if forecast:
                    standardized_forecasts.append(forecast)
        elif 'forecasts' in raw_data and isinstance(raw_data['forecasts'], list):
            # If raw_data has a 'forecasts' key with a list
            for item in raw_data['forecasts']:
                forecast = self._transform_dict(item, mapping)
                if forecast:
                    standardized_forecasts.append(forecast)
        else:
            # If raw_data is a single forecast or has a different structure
            forecast = self._transform_dict(raw_data, mapping)
            if forecast:
                standardized_forecasts.append(forecast)
        
        return standardized_forecasts
    
    def transform_df_to_standard(self, df: pd.DataFrame, mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Transform forecast data from DataFrame to standardized JSON format
        
        Args:
            df: DataFrame containing forecast data
            mapping: Optional mapping of DataFrame columns to schema properties
            
        Returns:
            List of standardized forecast objects
        """
        # Apply default mapping if none provided
        if mapping is None:
            mapping = self._get_default_mapping()
        
        # Check if the DataFrame contains time series forecast data for multiple stations
        # or if it's metadata for a single forecast
        if 'timestamp' in df.columns and 'station_id' in df.columns and 'predicted_value' in df.columns:
            # This looks like a time series dataframe with forecasted values for multiple stations
            return self._transform_time_series_df(df, mapping)
        else:
            # Assume this is a dataframe with one row per forecast
            standardized_forecasts = []
            
            for _, row in df.iterrows():
                forecast = self._transform_row(row, mapping)
                if forecast:
                    standardized_forecasts.append(forecast)
            
            return standardized_forecasts
    
    def _transform_time_series_df(self, df: pd.DataFrame, mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Transform a time series DataFrame to standardized forecast objects
        
        Args:
            df: DataFrame containing time series forecast data
            mapping: Mapping of DataFrame columns to schema properties
            
        Returns:
            List of standardized forecast objects
        """
        # Group by station_id and other metadata columns
        # to create separate forecasts for each station
        station_col = 'station_id'
        timestamp_col = 'timestamp'
        value_col = mapping.get('predicted_demand_kwh', 'predicted_value')
        
        # Identify metadata columns (not time series data)
        metadata_cols = [col for col in df.columns if col != timestamp_col and not col.startswith('predicted_')]
        
        # Group by station and other metadata
        grouped = df.groupby(station_col)
        
        forecasts = []
        
        for station_id, group in grouped:
            # Create a forecast object for this station
            forecast = {
                'station_id': station_id,
                'forecast_id': f"forecast-{station_id}-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
                'forecast_timestamp': self._format_datetime(pd.Timestamp.now()),
                'forecasted_values': []
            }
            
            # Set the prediction horizon
            timestamps = pd.to_datetime(group[timestamp_col])
            
            if not timestamps.empty:
                forecast['prediction_horizon'] = {
                    'start_time': self._format_datetime(timestamps.min()),
                    'end_time': self._format_datetime(timestamps.max()),
                }
                
                # Try to determine the resolution
                if len(timestamps) > 1:
                    diffs = timestamps.sort_values().diff().dropna()
                    if not diffs.empty:
                        most_common_diff = diffs.value_counts().idxmax()
                        minutes = most_common_diff.total_seconds() / 60
                        
                        if minutes == 15:
                            resolution = '15min'
                        elif minutes == 30:
                            resolution = '30min'
                        elif minutes == 60:
                            resolution = '1hour'
                        elif minutes == 180:
                            resolution = '3hour'
                        elif minutes == 360:
                            resolution = '6hour'
                        elif minutes == 720:
                            resolution = '12hour'
                        elif minutes == 1440:
                            resolution = '1day'
                        else:
                            resolution = f"{int(minutes)}min"
                        
                        forecast['prediction_horizon']['resolution'] = resolution
                
                # Add forecasted values
                for _, row in group.iterrows():
                    value_dict = {
                        'timestamp': self._format_datetime(row[timestamp_col])
                    }
                    
                    # Add all predicted values
                    for col in [c for c in group.columns if c.startswith('predicted_')]:
                        # Convert from column name like 'predicted_demand' to schema key like 'predicted_demand_kwh'
                        schema_key = col
                        if col == 'predicted_value':
                            schema_key = 'predicted_demand_kwh'
                        elif col == 'predicted_occupancy':
                            schema_key = 'predicted_occupancy_rate'
                        elif col == 'predicted_sessions':
                            schema_key = 'predicted_sessions_count'
                        
                        if not pd.isna(row[col]):
                            value_dict[schema_key] = float(row[col])
                    
                    # Add confidence intervals if available
                    if 'lower_bound' in row and 'upper_bound' in row and not pd.isna(row['lower_bound']) and not pd.isna(row['upper_bound']):
                        value_dict['prediction_interval'] = {
                            'lower_bound': float(row['lower_bound']),
                            'upper_bound': float(row['upper_bound'])
                        }
                        
                        # Add confidence percentage if available
                        if 'confidence_percentage' in row and not pd.isna(row['confidence_percentage']):
                            value_dict['prediction_interval']['confidence_percentage'] = float(row['confidence_percentage'])
                    
                    forecast['forecasted_values'].append(value_dict)
            
            # Add metadata
            for col in metadata_cols:
                if col != station_col and col in mapping:
                    schema_key = mapping[col]
                    value = group[col].iloc[0]
                    if not pd.isna(value):
                        nested_keys = schema_key.split('.')
                        curr_dict = forecast
                        for i, key in enumerate(nested_keys):
                            if i == len(nested_keys) - 1:
                                curr_dict[key] = value
                            else:
                                if key not in curr_dict:
                                    curr_dict[key] = {}
                                curr_dict = curr_dict[key]
            
            # Add model metrics if available
            metrics = ['mape', 'rmse', 'mae', 'r_squared', 'calibration_score']
            if any(metric in group.columns for metric in metrics):
                forecast['model_metrics'] = {}
                for metric in metrics:
                    if metric in group.columns and not pd.isna(group[metric].iloc[0]):
                        forecast['model_metrics'][metric] = float(group[metric].iloc[0])
            
            # Set forecast type if possible
            if 'forecast_type' not in forecast and 'prediction_horizon' in forecast:
                horizon_start = pd.to_datetime(forecast['prediction_horizon']['start_time'].replace('Z', '+00:00'))
                horizon_end = pd.to_datetime(forecast['prediction_horizon']['end_time'].replace('Z', '+00:00'))
                horizon_days = (horizon_end - horizon_start).total_seconds() / (24 * 3600)
                
                if horizon_days <= 1:
                    forecast['forecast_type'] = 'short_term'
                elif horizon_days <= 7:
                    forecast['forecast_type'] = 'medium_term'
                else:
                    forecast['forecast_type'] = 'long_term'
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _transform_row(self, row: pd.Series, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a single DataFrame row to a standardized forecast object
        
        Args:
            row: DataFrame row containing forecast metadata
            mapping: Mapping of DataFrame columns to schema properties
            
        Returns:
            Standardized forecast object
        """
        forecast = {}
        
        # Map basic properties
        for schema_key, df_key in mapping.items():
            if df_key in row and not pd.isna(row[df_key]):
                # Handle date-time fields
                if schema_key in ['forecast_timestamp', 'last_updated']:
                    forecast[schema_key] = self._format_datetime(row[df_key])
                # Handle nested properties (dot notation)
                elif '.' in schema_key:
                    parts = schema_key.split('.')
                    curr = forecast
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            curr[part] = row[df_key]
                        else:
                            if part not in curr:
                                curr[part] = {}
                            curr = curr[part]
                else:
                    forecast[schema_key] = row[df_key]
        
        # If this row contains a reference to a separate forecast time series file, load it
        if 'forecast_file' in row and not pd.isna(row['forecast_file']):
            try:
                file_path = row['forecast_file']
                if not os.path.isabs(file_path):
                    # Try relative to the working directory
                    if os.path.exists(file_path):
                        pass
                    # Try relative to the data directory
                    elif os.path.exists(os.path.join('data', file_path)):
                        file_path = os.path.join('data', file_path)
                    # Try relative to the forecast directory
                    elif os.path.exists(os.path.join('data', 'forecasts', file_path)):
                        file_path = os.path.join('data', 'forecasts', file_path)
                
                # Load the forecast time series data
                if file_path.endswith('.csv'):
                    time_series_df = pd.read_csv(file_path)
                elif file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        time_series_data = json.load(f)
                    if isinstance(time_series_data, list):
                        time_series_df = pd.DataFrame(time_series_data)
                    else:
                        time_series_df = pd.DataFrame([time_series_data])
                
                # Process the time series data
                forecast['forecasted_values'] = []
                
                for _, ts_row in time_series_df.iterrows():
                    value_dict = {}
                    
                    # Get timestamp
                    if 'timestamp' in ts_row:
                        value_dict['timestamp'] = self._format_datetime(ts_row['timestamp'])
                    elif 'datetime' in ts_row:
                        value_dict['timestamp'] = self._format_datetime(ts_row['datetime'])
                    elif 'date' in ts_row and 'time' in ts_row:
                        value_dict['timestamp'] = self._format_datetime(f"{ts_row['date']} {ts_row['time']}")
                    
                    # Get predicted values
                    if 'predicted_value' in ts_row:
                        value_dict['predicted_demand_kwh'] = float(ts_row['predicted_value'])
                    elif 'demand_kwh' in ts_row:
                        value_dict['predicted_demand_kwh'] = float(ts_row['demand_kwh'])
                    elif 'demand' in ts_row:
                        value_dict['predicted_demand_kwh'] = float(ts_row['demand'])
                    
                    # Get prediction intervals if available
                    if 'lower_bound' in ts_row and 'upper_bound' in ts_row:
                        value_dict['prediction_interval'] = {
                            'lower_bound': float(ts_row['lower_bound']),
                            'upper_bound': float(ts_row['upper_bound'])
                        }
                        if 'confidence_percentage' in ts_row:
                            value_dict['prediction_interval']['confidence_percentage'] = float(ts_row['confidence_percentage'])
                    
                    forecast['forecasted_values'].append(value_dict)
                
                # Add prediction horizon
                if forecast['forecasted_values']:
                    timestamps = [pd.to_datetime(v['timestamp'].replace('Z', '+00:00')) for v in forecast['forecasted_values']]
                    forecast['prediction_horizon'] = {
                        'start_time': self._format_datetime(min(timestamps)),
                        'end_time': self._format_datetime(max(timestamps))
                    }
                    
                    # Determine resolution
                    if len(timestamps) > 1:
                        sorted_timestamps = sorted(timestamps)
                        diffs = [(sorted_timestamps[i+1] - sorted_timestamps[i]).total_seconds() / 60 for i in range(len(sorted_timestamps)-1)]
                        if diffs:
                            most_common_diff = pd.Series(diffs).value_counts().idxmax()
                            
                            if most_common_diff == 15:
                                resolution = '15min'
                            elif most_common_diff == 30:
                                resolution = '30min'
                            elif most_common_diff == 60:
                                resolution = '1hour'
                            elif most_common_diff == 180:
                                resolution = '3hour'
                            elif most_common_diff == 360:
                                resolution = '6hour'
                            elif most_common_diff == 720:
                                resolution = '12hour'
                            elif most_common_diff == 1440:
                                resolution = '1day'
                            else:
                                resolution = f"{int(most_common_diff)}min"
                            
                            forecast['prediction_horizon']['resolution'] = resolution
            except Exception as e:
                print(f"Warning: Failed to process forecast file {row.get('forecast_file', 'unknown')}: {e}")
        
        # Ensure forecast ID is present
        if 'forecast_id' not in forecast:
            # Generate a forecast ID if not present
            if 'station_id' in forecast and 'forecast_timestamp' in forecast:
                forecast['forecast_id'] = f"{forecast['station_id']}-{forecast['forecast_timestamp'].replace(':', '-').replace('.', '-')}"
            else:
                # Generate a random forecast ID
                import uuid
                forecast['forecast_id'] = f"forecast-{uuid.uuid4()}"
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else [
            'forecast_id', 'station_id', 'forecast_timestamp', 'forecasted_values'
        ]
        
        if all(field in forecast for field in required_fields):
            return forecast
        else:
            missing = [field for field in required_fields if field not in forecast]
            print(f"Warning: Missing required fields {missing} for forecast {forecast.get('forecast_id', 'unknown')}")
            return None
    
    def _transform_dict(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a dictionary to a standardized forecast object
        
        Args:
            data: Dictionary containing forecast data
            mapping: Mapping of dictionary keys to schema properties
            
        Returns:
            Standardized forecast object
        """
        forecast = {}
        
        # Map basic properties
        for schema_key, data_key in mapping.items():
            if data_key in data and data[data_key] is not None:
                # Handle date-time fields
                if schema_key in ['forecast_timestamp', 'last_updated']:
                    forecast[schema_key] = self._format_datetime(data[data_key])
                # Handle nested properties (dot notation)
                elif '.' in schema_key:
                    parts = schema_key.split('.')
                    curr = forecast
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            curr[part] = data[data_key]
                        else:
                            if part not in curr:
                                curr[part] = {}
                            curr = curr[part]
                else:
                    forecast[schema_key] = data[data_key]
        
        # Handle forecasted values array specially
        if 'forecast_data' in data and isinstance(data['forecast_data'], list):
            forecast['forecasted_values'] = []
            for point in data['forecast_data']:
                value_dict = {}
                
                # Map the standard fields
                if 'timestamp' in point:
                    value_dict['timestamp'] = self._format_datetime(point['timestamp'])
                
                if 'predicted_value' in point:
                    value_dict['predicted_demand_kwh'] = float(point['predicted_value'])
                
                # Map other possible fields
                if 'predicted_occupancy' in point:
                    value_dict['predicted_occupancy_rate'] = float(point['predicted_occupancy'])
                
                if 'predicted_sessions' in point:
                    value_dict['predicted_sessions_count'] = float(point['predicted_sessions'])
                
                # Map confidence/prediction intervals
                if 'lower_bound' in point and 'upper_bound' in point:
                    value_dict['prediction_interval'] = {
                        'lower_bound': float(point['lower_bound']),
                        'upper_bound': float(point['upper_bound'])
                    }
                    if 'confidence_percentage' in point:
                        value_dict['prediction_interval']['confidence_percentage'] = float(point['confidence_percentage'])
                
                forecast['forecasted_values'].append(value_dict)
        
        # Add prediction horizon if not already present
        if 'forecasted_values' in forecast and 'prediction_horizon' not in forecast:
            timestamps = [pd.to_datetime(v['timestamp'].replace('Z', '+00:00')) for v in forecast['forecasted_values']]
            if timestamps:
                forecast['prediction_horizon'] = {
                    'start_time': self._format_datetime(min(timestamps)),
                    'end_time': self._format_datetime(max(timestamps))
                }
                
                # Determine resolution
                if len(timestamps) > 1:
                    sorted_timestamps = sorted(timestamps)
                    diffs = [(sorted_timestamps[i+1] - sorted_timestamps[i]).total_seconds() / 60 for i in range(len(sorted_timestamps)-1)]
                    if diffs:
                        most_common_diff = pd.Series(diffs).value_counts().idxmax()
                        
                        if most_common_diff == 15:
                            resolution = '15min'
                        elif most_common_diff == 30:
                            resolution = '30min'
                        elif most_common_diff == 60:
                            resolution = '1hour'
                        elif most_common_diff == 180:
                            resolution = '3hour'
                        elif most_common_diff == 360:
                            resolution = '6hour'
                        elif most_common_diff == 720:
                            resolution = '12hour'
                        elif most_common_diff == 1440:
                            resolution = '1day'
                        else:
                            resolution = f"{int(most_common_diff)}min"
                        
                        forecast['prediction_horizon']['resolution'] = resolution
        
        # Ensure forecast ID is present
        if 'forecast_id' not in forecast:
            # Generate a forecast ID if not present
            if 'station_id' in forecast and 'forecast_timestamp' in forecast:
                forecast['forecast_id'] = f"{forecast['station_id']}-{forecast['forecast_timestamp'].replace(':', '-').replace('.', '-')}"
            else:
                # Generate a random forecast ID
                import uuid
                forecast['forecast_id'] = f"forecast-{uuid.uuid4()}"
        
        # Ensure required fields are present
        required_fields = self.schema.get('required', []) if self.schema else [
            'forecast_id', 'station_id', 'forecast_timestamp', 'forecasted_values'
        ]
        
        if all(field in forecast for field in required_fields):
            return forecast
        else:
            missing = [field for field in required_fields if field not in forecast]
            print(f"Warning: Missing required fields {missing} for forecast {forecast.get('forecast_id', 'unknown')}")
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
            'forecast_id': 'forecast_id',
            'station_id': 'station_id',
            'forecast_timestamp': 'creation_timestamp',
            'forecast_type': 'forecast_type',
            'model_version': 'model_version',
            'model_name': 'model_name',
            'model_metrics.mape': 'mape',
            'model_metrics.rmse': 'rmse',
            'model_metrics.mae': 'mae',
            'model_metrics.r_squared': 'r_squared',
            'model_metrics.calibration_score': 'calibration_score',
            'last_updated': 'last_updated'
        } 