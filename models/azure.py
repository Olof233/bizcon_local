"""
OpenAI model client for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
import openai
import tiktoken

from .base import ModelClient


class AzureClient(ModelClient):
    """Client for Azure OpenAI models."""
    
    
    def __init__(self, 
                 model_name: str, 
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 endpoint: Optional[str] = None,
                 api_version: Optional[str] = None,
                 **kwargs):
        """
        Initialize the Azure OpenAI model client.
        
        Args:
            model_name: Name of the Azure OpenAI model to use
            api_key: Azure OpenAI API key (uses environment variable if None)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        # Set API key
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.version = api_version or os.environ.get("API_VERSION")
        self.endpoint = endpoint or os.environ.get("AZURE_ENDPOINT")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
        
        # Initialize client
        self.client = openai.AzureOpenAI(
            api_version=self.version,
            azure_endpoint = self.endpoint, # type: ignore
            api_key=self.api_key
            )
        
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Default tokenizer
    
        self.input = ""

    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the Azure OpenAI model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Prepare API call parameters
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.params
            }
            
            # Add tools if provided
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            
            # Make the API call
            self.input = params["messages"]
            response = self.client.chat.completions.create(**params)
            
            # Extract response content
            message = response.choices[0].message
            result = {"content": message.content or ""}
            
            # # Add tool calls if present
            # if hasattr(message, "tool_calls") and message.tool_calls:
            #     result["tool_calls"] = [
            #         {
            #             "id": tool_call.id,
            #             "type": "function",
            #             "function": {
            #                 "name": tool_call.function.name,
            #                 "arguments": tool_call.function.arguments
            #             }
            #         }
            #         for tool_call in message.tool_calls
            #     ]
            
          
            return result
            
        except Exception as e:
            # Handle API errors
            return {
                "content": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def get_token_count(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        return len(self.tokenizer.encode(text))
    

    def get_input(self) -> str:
        """
        Get the input text used for the last generation.
        
        Returns:
            Input text
        """
        return self.input