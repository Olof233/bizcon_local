"""
Models package for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
from os.path import isdir

from .base import ModelClient
from .openai import OpenAIClient
from .anthropic import AnthropicClient
from .mistral import MistralAIClient
from .local import LocalClient



def get_model_client(provider: str, model_name: str, **kwargs) -> ModelClient:
    """
    Get a model client for the specified provider and model.
    
    Args:
        provider: Model provider name (openai, anthropic, mistral)
        model_name: Name of the model
        **kwargs: Additional model parameters
        
    Returns:
        ModelClient instance
        
    Raises:
        ValueError: If the provider is not supported
    """
    if provider.lower() == "openai":
        return OpenAIClient(model_name=model_name, **kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicClient(model_name=model_name, **kwargs)
    elif provider.lower() in ["mistral", "mistralai"]:
        return MistralAIClient(model_name=model_name, **kwargs)
    elif isdir(provider):
        return LocalClient(model_name=model_name, **kwargs)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def list_supported_models() -> Dict[str, List[str]]:
    """
    Get a list of supported models by provider.
    
    Returns:
        Dictionary with provider names as keys and lists of model names as values
    """
    return {
        "openai": [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        "anthropic": [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "claude-2",
            "claude-instant"
        ],
        "mistral": [
            "mistral-large",
            "mistral-medium",
            "mistral-small",
            "mistral-tiny"
        ]
    }