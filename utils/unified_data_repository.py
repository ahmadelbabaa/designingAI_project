"""
Unified Data Repository
----------------------
Central data repository for accessing and managing all datasets across components.
Acts as a unified access point for all data operations throughout the application.
"""

import os
import json
import time
import pandas as pd
from typing import Dict, Any, Optional, List, Union

class UnifiedDataRepository:
    """
    Central data repository for accessing and managing all datasets across components.
    Implements the Singleton pattern to ensure a single global data repository.
    """
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedDataRepository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the repository with default empty containers"""
        self.datasets = {}  # Main data storage
        self.metadata = {}  # Metadata for each dataset
        self.cache = {}     # Cache for expensive computations
        self.subscriptions = {}  # Event subscriptions for data changes
        self._load_config()
    
    def _load_config(self):
        """Load configuration settings for the repository"""
        self.config = {
            'cache_expiry': 3600,  # Default cache expiry time in seconds
            'auto_validate': True   # Validate datasets against schemas by default
        }
        
        # Load from config file if it exists
        config_path = 'config/data_repository_config.json'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                print(f"Warning: Failed to load repository config: {e}")
    
    def get_dataset(self, dataset_id: str, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Retrieve a dataset with optional filtering
        
        Args:
            dataset_id: Identifier for the dataset
            filters: Optional dictionary of filter conditions
            
        Returns:
            The requested dataset (usually a DataFrame)
        """
        if dataset_id not in self.datasets:
            raise KeyError(f"Dataset not found: {dataset_id}")
        
        data = self.datasets[dataset_id]
        
        # Apply filters if provided
        if filters and isinstance(data, pd.DataFrame):
            for column, value in filters.items():
                if column in data.columns:
                    if isinstance(value, list):
                        data = data[data[column].isin(value)]
                    else:
                        data = data[data[column] == value]
        
        return data
    
    def register_dataset(self, dataset_id: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a new dataset or update an existing one
        
        Args:
            dataset_id: Identifier for the dataset
            data: The dataset to register
            metadata: Optional metadata about the dataset
        """
        # Store the dataset
        self.datasets[dataset_id] = data
        
        # Update metadata
        if metadata:
            if dataset_id not in self.metadata:
                self.metadata[dataset_id] = {}
            self.metadata[dataset_id].update(metadata)
        
        # Add timestamp if not provided
        if dataset_id in self.metadata and 'last_updated' not in self.metadata[dataset_id]:
            self.metadata[dataset_id]['last_updated'] = time.time()
        
        # Notify subscribers (to be implemented with EventBus)
        self._notify_subscribers(dataset_id)
    
    def _notify_subscribers(self, dataset_id: str) -> None:
        """Notify subscribers about dataset updates"""
        if dataset_id in self.subscriptions:
            for callback in self.subscriptions[dataset_id]:
                try:
                    callback(self.datasets[dataset_id])
                except Exception as e:
                    print(f"Error notifying subscriber for {dataset_id}: {e}")
    
    def subscribe(self, dataset_id: str, callback: callable) -> None:
        """
        Subscribe to changes in a specific dataset
        
        Args:
            dataset_id: Identifier for the dataset to subscribe to
            callback: Function to call when the dataset is updated
        """
        if dataset_id not in self.subscriptions:
            self.subscriptions[dataset_id] = []
        
        if callback not in self.subscriptions[dataset_id]:
            self.subscriptions[dataset_id].append(callback)
    
    def unsubscribe(self, dataset_id: str, callback: callable) -> bool:
        """
        Unsubscribe from changes in a specific dataset
        
        Args:
            dataset_id: Identifier for the dataset
            callback: Function to remove from subscribers
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        if dataset_id in self.subscriptions and callback in self.subscriptions[dataset_id]:
            self.subscriptions[dataset_id].remove(callback)
            return True
        return False
    
    def get_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific dataset
        
        Args:
            dataset_id: Identifier for the dataset
            
        Returns:
            Metadata dictionary or None if dataset doesn't exist
        """
        if dataset_id not in self.metadata:
            return None
        return self.metadata[dataset_id]
    
    def list_datasets(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available datasets with basic metadata
        
        Returns:
            Dictionary of dataset IDs mapped to their metadata
        """
        return {
            dataset_id: {
                'rows': len(data) if hasattr(data, '__len__') else None,
                'last_updated': self.metadata.get(dataset_id, {}).get('last_updated', None),
                'schema': self.metadata.get(dataset_id, {}).get('schema', None)
            }
            for dataset_id, data in self.datasets.items()
        } 