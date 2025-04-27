"""
Data Validator
-------------
Utilities for validating data against JSON schemas to ensure data quality
and conformance to expected formats.
"""

import os
import json
import jsonschema
import pandas as pd
from typing import Dict, Any, List, Union, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator

class DataValidator:
    """
    Validator for ensuring data conforms to defined JSON schemas.
    Provides methods for validating different data types and reporting validation issues.
    """
    
    def __init__(self, schema_dir: str = "config/data_schemas"):
        """
        Initialize the validator with schemas
        
        Args:
            schema_dir: Directory containing JSON schema files
        """
        self.schema_dir = schema_dir
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all schemas from the schema directory"""
        if not os.path.exists(self.schema_dir):
            print(f"Warning: Schema directory {self.schema_dir} not found")
            return
        
        for filename in os.listdir(self.schema_dir):
            if filename.endswith('.json'):
                schema_name = filename.replace('.json', '')
                schema_path = os.path.join(self.schema_dir, filename)
                
                try:
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_name] = json.load(f)
                    print(f"Loaded schema: {schema_name}")
                except Exception as e:
                    print(f"Error loading schema {schema_name}: {e}")
    
    def validate_object(self, obj: Dict[str, Any], schema_name: str) -> Tuple[bool, List[str]]:
        """
        Validate a single object against a schema
        
        Args:
            obj: Object to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if schema_name not in self.schemas:
            return False, [f"Schema {schema_name} not found"]
        
        schema = self.schemas[schema_name]
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(obj))
        
        if not errors:
            return True, []
        
        error_messages = []
        for error in errors:
            # Create a friendly error message
            path = '/'.join(str(p) for p in error.path) if error.path else 'root'
            message = f"Error at {path}: {error.message}"
            error_messages.append(message)
        
        return False, error_messages
    
    def validate_data(self, data: Union[List[Dict[str, Any]], pd.DataFrame], 
                     schema_name: str, max_errors: int = 10) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a collection of data objects against a schema
        
        Args:
            data: List of objects or DataFrame to validate
            schema_name: Name of the schema to validate against
            max_errors: Maximum number of errors to report
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        if schema_name not in self.schemas:
            return False, {"error": f"Schema {schema_name} not found"}
        
        # Convert DataFrame to list of dictionaries if needed
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        else:
            data_list = data
        
        # Initialize counters and containers
        total_objects = len(data_list)
        valid_count = 0
        invalid_count = 0
        error_examples = []
        
        # Validate each object
        for i, obj in enumerate(data_list):
            is_valid, errors = self.validate_object(obj, schema_name)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                
                # Only collect detailed errors for a limited number of examples
                if len(error_examples) < max_errors:
                    # Try to include an identifier for easier debugging
                    identifier = None
                    for id_field in ['id', 'station_id', 'session_id', 'forecast_id']:
                        if id_field in obj:
                            identifier = obj[id_field]
                            break
                    
                    error_examples.append({
                        "index": i,
                        "identifier": identifier,
                        "errors": errors
                    })
        
        # Create validation report
        validation_report = {
            "total_objects": total_objects,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validation_success_rate": valid_count / total_objects if total_objects > 0 else 0,
            "has_errors": invalid_count > 0,
            "error_examples": error_examples
        }
        
        return invalid_count == 0, validation_report
    
    def validate_stations(self, stations: Union[List[Dict[str, Any]], pd.DataFrame]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate station data against the station schema
        
        Args:
            stations: List of station objects or DataFrame of stations
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        return self.validate_data(stations, 'station_schema')
    
    def validate_sessions(self, sessions: Union[List[Dict[str, Any]], pd.DataFrame]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate session data against the session schema
        
        Args:
            sessions: List of session objects or DataFrame of sessions
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        return self.validate_data(sessions, 'session_schema')
    
    def validate_forecasts(self, forecasts: Union[List[Dict[str, Any]], pd.DataFrame]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate forecast data against the forecast schema
        
        Args:
            forecasts: List of forecast objects or DataFrame of forecasts
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        return self.validate_data(forecasts, 'forecast_schema')
    
    def print_validation_report(self, report: Dict[str, Any], verbose: bool = False) -> None:
        """
        Print a human-readable validation report
        
        Args:
            report: Validation report from validate_data
            verbose: Whether to print detailed error information
        """
        print(f"Validation Report:")
        print(f"  Total objects: {report['total_objects']}")
        print(f"  Valid objects: {report['valid_count']}")
        print(f"  Invalid objects: {report['invalid_count']}")
        print(f"  Success rate: {report['validation_success_rate']:.2%}")
        
        if report['has_errors']:
            print("\nErrors found:")
            
            if verbose:
                for i, example in enumerate(report['error_examples']):
                    print(f"\nError Example {i+1}:")
                    print(f"  Index: {example['index']}")
                    
                    if example['identifier']:
                        print(f"  Identifier: {example['identifier']}")
                    
                    print(f"  Errors:")
                    for error in example['errors']:
                        print(f"    - {error}")
            else:
                print(f"  Found {report['invalid_count']} invalid objects")
                print(f"  Use verbose=True to see detailed error information")
        else:
            print("\nAll objects are valid!")

# Command line interface
if __name__ == "__main__":
    import argparse
    from utils.unified_data_repository import UnifiedDataRepository
    
    parser = argparse.ArgumentParser(description="Validate data against JSON schemas")
    parser.add_argument("--schema-dir", type=str, default="config/data_schemas", 
                       help="Directory containing JSON schema files")
    parser.add_argument("--dataset", type=str, required=True,
                       help="Name of the dataset to validate (stations, sessions, forecasts)")
    parser.add_argument("--verbose", action="store_true",
                       help="Print detailed validation errors")
    
    args = parser.parse_args()
    
    # Initialize validator and repository
    validator = DataValidator(schema_dir=args.schema_dir)
    repository = UnifiedDataRepository()
    
    # Get the dataset from the repository
    dataset = repository.get_dataset(args.dataset)
    
    if dataset is None:
        print(f"Dataset '{args.dataset}' not found in the repository")
        exit(1)
    
    # Validate the dataset
    if args.dataset == 'stations':
        is_valid, report = validator.validate_stations(dataset)
    elif args.dataset == 'sessions':
        is_valid, report = validator.validate_sessions(dataset)
    elif args.dataset == 'forecasts':
        is_valid, report = validator.validate_forecasts(dataset)
    else:
        print(f"Unsupported dataset type: {args.dataset}")
        exit(1)
    
    # Print the validation report
    validator.print_validation_report(report, verbose=args.verbose) 