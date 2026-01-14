"""
Configuration Loader Module

This module loads configuration from YAML files and environment variables.
It provides a centralized way to manage application settings.
"""

import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_config(config_path: str = 'config/config.yaml'):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration YAML file
    
    Returns:
        Dictionary containing configuration settings
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Return default configuration if file doesn't exist
        return get_default_config()
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Override with environment variables if they exist
    config = override_with_env(config)
    
    return config


def get_default_config():
    """Return default configuration if config file is missing."""
    return {
        'database': {
            'type': 'sqlite',
            'path': 'data/pipeline_metrics.db'
        },
        'server': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False
        },
        'logging': {
            'level': 'INFO',
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'file': 'logs/monitoring.log'
        }
    }


def override_with_env(config: dict):
    """
    Override configuration values with environment variables.
    
    Environment variables take precedence over config file values.
    Format: SECTION_KEY (e.g., SERVER_PORT overrides config['server']['port'])
    """
    # Database URL
    if os.getenv('DATABASE_URL'):
        config['database']['path'] = os.getenv('DATABASE_URL')
    
    # Server settings
    if os.getenv('FLASK_ENV'):
        config['server']['debug'] = os.getenv('FLASK_ENV') == 'development'
    
    if os.getenv('SERVER_PORT'):
        config['server']['port'] = int(os.getenv('SERVER_PORT'))
    
    return config
