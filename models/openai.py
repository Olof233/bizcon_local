"""
OpenAI model client for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
import openai
import tiktoken

from .base import ModelClient


class OpenAIClient(ModelClient):
    """Client for OpenAI models."""
    
    # Cost per 1000 tokens (as of May 2024)
    PRICING = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002}
    }
    
    def __init__(self, 
                 model_name: str, 
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 **kwargs):
        """
        Initialize the OpenAI model client.
        
        Args:
            model_name: Name of the OpenAI model to use
            api_key: OpenAI API key (uses environment variable if None)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        # Set API key
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
        
        # Initialize client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Default tokenizer
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the OpenAI model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Count tokens in the prompt
            prompt_tokens = sum(self.get_token_count(msg.get("content", "")) for msg in messages)
            
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
            response = self.client.chat.completions.create(**params)
            
            # Extract response content
            message = response.choices[0].message
            result = {"content": message.content or ""}
            
            # Add tool calls if present
            if hasattr(message, "tool_calls") and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in message.tool_calls
                ]
            
            # Update token usage
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_tokens = response.usage.total_tokens
            
            self.total_tokens_used += total_tokens
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Update cost calculation
            model_base = self.model_name.split("-")[0] + "-" + self.model_name.split("-")[1]
            if model_base in self.PRICING:
                input_cost = (prompt_tokens / 1000) * self.PRICING[model_base]["input"]
                output_cost = (completion_tokens / 1000) * self.PRICING[model_base]["output"]
                self.total_cost += input_cost + output_cost
            
            self.api_calls += 1
            
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