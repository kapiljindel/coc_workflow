"""
Settings Loader
Loads, validates, and manages configuration from config.json
"""

import json
import os
from typing import Dict, Any
from . import constants

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json file
    
    Returns:
        Dictionary with configuration values
        
    Raises:
        FileNotFoundError: If config.json doesn't exist
        json.JSONDecodeError: If config.json is invalid JSON
    """
    config_path = constants.CONFIG_FILE
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that all required configuration keys exist
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises exception otherwise
    """
    required_keys = [
        "ADB_PORT",
        "MINIMUM_GOLD",
        "MINIMUM_ELIXIR",
        "TOTAL_TROOPS",
        "MAX_GOLD",
        "MAX_ELIXIR",
        "MY_ARMY",
        "IS_UPGRADE_WALL",
        "deploy_strategy"
    ]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    return True

def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config.json
    
    Args:
        config: Configuration dictionary to save
    """
    config_path = constants.CONFIG_FILE
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def initialize_constants_from_config(config: Dict[str, Any]) -> None:
    """
    Update module constants from loaded configuration
    
    Args:
        config: Configuration dictionary from load_config()
    """
    constants.MINIMUM_GOLD = config.get("MINIMUM_GOLD", 400000)
    constants.MINIMUM_ELIXIR = config.get("MINIMUM_ELIXIR", 400000)
    constants.MAX_GOLD = config.get("MAX_GOLD", 9250000)
    constants.MAX_ELIXIR = config.get("MAX_ELIXIR", 9250000)
    constants.TOTAL_TROOPS = config.get("TOTAL_TROOPS", 120)
    constants.MY_ARMY = config.get("MY_ARMY", [])

def get_config() -> Dict[str, Any]:
    """
    Convenience function to load and validate config in one call
    
    Returns:
        Validated configuration dictionary
    """
    config = load_config()
    validate_config(config)
    initialize_constants_from_config(config)
    return config
