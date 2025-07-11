"""
Base class for LLM model clients.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import json


class ModelClient(ABC):
    """Base class for all LLM model clients."""
    
    def __init__(self, 
                 model_name: str, 
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 **kwargs):
        """
        Initialize the model client.
        
        Args:
            model_name: Name of the model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model-specific parameters
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.params = kwargs
        self.total_tokens_used = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
        self.input = ""
    
    @abstractmethod
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions that the model can use
            
        Returns:
            Dictionary with response content and metadata
        """
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.total_tokens_used = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
    
    def get_usage_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get usage statistics.
        
        Returns:
            Dictionary with token usage and cost information
        """
        return {
            "model": self.model_name,
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens_used,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_cost": self.total_cost
        }
    
    def get_input(self) -> str:
        """
        Get the input text used for the last generation.
        
        Returns:
            Input text
        """
        return self.input
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.model_name})"