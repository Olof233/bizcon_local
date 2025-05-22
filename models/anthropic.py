"""
Anthropic model client for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
import anthropic
import tiktoken

from .base import ModelClient


class AnthropicClient(ModelClient):
    """Client for Anthropic Claude models."""
    
    # Cost per 1000 tokens (as of May 2024)
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-2": {"input": 0.008, "output": 0.024},
        "claude-instant": {"input": 0.0008, "output": 0.0024}
    }
    
    def __init__(self, 
                 model_name: str, 
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 **kwargs):
        """
        Initialize the Anthropic model client.
        
        Args:
            model_name: Name of the Anthropic model to use
            api_key: Anthropic API key (uses environment variable if None)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        # Set API key
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and not found in environment variables")
        
        # Initialize client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Initialize tokenizer (Anthropic uses cl100k_base)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the Anthropic model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Convert messages format to Anthropic format
            anthropic_messages = []
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "user":
                    anthropic_messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    anthropic_messages.append({"role": "assistant", "content": content})
                elif role == "system":
                    # System message is handled separately in Anthropic API
                    system_message = content
                elif role == "tool":
                    # Anthropic handles tool responses by appending to the previous assistant message
                    if anthropic_messages and anthropic_messages[-1]["role"] == "assistant":
                        tool_name = msg.get("name", "unknown_tool")
                        tool_content = msg.get("content", "{}")
                        append_text = f"\nTool {tool_name} returned: {tool_content}"
                        anthropic_messages[-1]["content"] += append_text
            
            # Count tokens in the prompt
            prompt_text = json.dumps(anthropic_messages)
            prompt_tokens = self.get_token_count(prompt_text)
            
            # Prepare API call parameters
            params = {
                "model": self.model_name,
                "messages": anthropic_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.params
            }
            
            # Add system message if present
            if "system_message" in locals():
                params["system"] = system_message
            
            # Add tools if provided
            if tools:
                params["tools"] = tools
                
            # Make the API call
            response = self.client.messages.create(**params)
            
            # Extract response content
            result = {"content": response.content[0].text}
            
            # Add tool calls if present
            if hasattr(response, "tool_calls") and response.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.parameters)
                        }
                    }
                    for i, tool_call in enumerate(response.tool_calls)
                ]
            
            # Update token usage
            completion_tokens = response.usage.output_tokens
            prompt_tokens = response.usage.input_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            self.total_tokens_used += total_tokens
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Update cost calculation
            model_base = "-".join(self.model_name.split("-")[:3])  # Extract base model name
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