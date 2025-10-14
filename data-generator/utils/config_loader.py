"""
Configuration Loader Utility
============================

Loads and validates configuration from YAML files for the EuroStyle Fashion 
data generation system.
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    """Loads and validates configuration from YAML files."""
    
    def __init__(self, config_path: str):
        """Initialize the config loader with a path to the configuration file."""
        self.config_path = Path(config_path)
        self.config = None
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                
            if self.config is None:
                raise ValueError("Configuration file is empty or invalid")
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        if self.config is None:
            raise RuntimeError("Configuration not loaded")
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value by key path (e.g., 'database.host')."""
        if self.config is None:
            raise RuntimeError("Configuration not loaded")
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate_required_keys(self, required_keys: list) -> None:
        """Validate that required configuration keys exist."""
        missing_keys = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration with validation."""
        db_config = self.get('database', {})
        
        # Validate required database keys
        required_keys = ['host', 'port', 'database', 'username', 'password']
        for key in required_keys:
            if key not in db_config:
                raise ValueError(f"Missing required database configuration: {key}")
        
        return db_config
    
    def get_data_volumes(self) -> Dict[str, int]:
        """Get data volume configuration with validation."""
        volumes = self.get('data_volumes', {})
        
        # Validate that all volumes are integers
        for key, value in volumes.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid data volume for {key}: must be non-negative integer")
        
        return volumes
    
    def get_geographic_distribution(self) -> Dict[str, Dict[str, Any]]:
        """Get geographic distribution configuration."""
        geo_dist = self.get('geographic_distribution', {})
        
        # Validate percentages sum to 100
        total_percentage = sum(
            country_config.get('percentage', 0) 
            for country_config in geo_dist.values()
        )
        
        if abs(total_percentage - 100) > 0.1:  # Allow small floating point errors
            raise ValueError(f"Geographic distribution percentages must sum to 100, got {total_percentage}")
        
        return geo_dist
    
    def get_business_metrics(self) -> Dict[str, float]:
        """Get business metrics configuration."""
        return self.get('business_metrics', {})
    
    def get_seasonality_config(self) -> Dict[str, Any]:
        """Get seasonality configuration."""
        return self.get('seasonality', {})
    
    def get_time_range(self) -> Dict[str, str]:
        """Get time range configuration."""
        time_range = self.get('time_range', {})
        
        required_keys = ['start_date', 'end_date', 'current_date']
        for key in required_keys:
            if key not in time_range:
                raise ValueError(f"Missing required time range configuration: {key}")
        
        return time_range