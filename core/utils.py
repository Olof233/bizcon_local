"""
Utility functions for bizCon framework.
"""
from typing import Dict, List, Any, Optional, Union
import json
import os
import re
import yaml
import datetime
import time


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with the loaded data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
        indent: Indentation level for JSON formatting
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load data from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary with the loaded data
        
    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the file is not valid YAML
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save data to a YAML file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format a timestamp as an ISO 8601 string.
    
    Args:
        timestamp: UNIX timestamp (uses current time if None)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.datetime.fromtimestamp(timestamp).isoformat()


def parse_timestamp(timestamp_str: str) -> float:
    """
    Parse an ISO 8601 timestamp string to a UNIX timestamp.
    
    Args:
        timestamp_str: ISO 8601 timestamp string
        
    Returns:
        UNIX timestamp
    """
    dt = datetime.datetime.fromisoformat(timestamp_str)
    return dt.timestamp()


def clean_text_for_metrics(text: str) -> str:
    """
    Clean text for metrics calculation.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove markdown formatting
    text = re.sub(r'[*_~`#]', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '[URL]', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if needed.
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + '...'


def anonymize_api_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anonymize API keys in configuration data.
    
    Args:
        data: Input data
        
    Returns:
        Data with API keys anonymized
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = anonymize_api_keys(value)
        elif isinstance(value, list):
            result[key] = [
                anonymize_api_keys(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(key, str) and ('api_key' in key.lower() or 'apikey' in key.lower()):
            if value and isinstance(value, str):
                # Replace all but the first and last 4 characters with asterisks
                prefix = value[:4]
                suffix = value[-4:] if len(value) > 8 else ''
                result[key] = f"{prefix}{'*' * (len(value) - len(prefix) - len(suffix))}{suffix}"
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result