"""
Mistral model client for bizCon framework.
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
from mistralai.client import MistralClient
from mistralai.models.chatcompletionrequest import ChatCompletionRequest
import tiktoken

from .base import ModelClient


class MistralAIClient(ModelClient):
    """Client for Mistral AI models."""
    
    # Cost per 1000 tokens (as of May 2024)
    PRICING = {
        "mistral-large": {"input": 0.008, "output": 0.024},
        "mistral-medium": {"input": 0.0027, "output": 0.0081},
        "mistral-small": {"input": 0.002, "output": 0.006},
        "mistral-tiny": {"input": 0.00014, "output": 0.00042},
    }
    
    def __init__(self, 
                 model_name: str, 
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 **kwargs):
        """
        Initialize the Mistral AI model client.
        
        Args:
            model_name: Name of the Mistral AI model to use
            api_key: Mistral AI API key (uses environment variable if None)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        # Set API key
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral AI API key not provided and not found in environment variables")
        
        # Initialize client
        self.client = MistralClient(api_key=self.api_key)
        
        # Initialize tokenizer (Mistral uses cl100k_base)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response from the Mistral AI model.
        
        Args:
            messages: List of message objects in the format 
                     [{"role": "user", "content": "Hello"}, ...]
            tools: Optional list of tool definitions
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Convert messages format to Mistral format
            mistral_messages = []
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "user":
                    mistral_messages.append(ChatCompletionRequest(role="user", content=content))
                elif role == "assistant":
                    mistral_messages.append(ChatCompletionRequest(role="assistant", content=content))
                elif role == "system":
                    mistral_messages.append(ChatCompletionRequest(role="system", content=content))
                elif role == "tool":
                    # Handle tool responses by appending to the previous assistant message
                    if mistral_messages and mistral_messages[-1].role == "assistant":
                        tool_name = msg.get("name", "unknown_tool")
                        tool_content = msg.get("content", "{}")
                        append_text = f"\nTool {tool_name} returned: {tool_content}"
                        mistral_messages[-1].content += append_text
            
            # Count tokens in the prompt
            prompt_text = json.dumps([{"role": m.role, "content": m.content} for m in mistral_messages])
            prompt_tokens = self.get_token_count(prompt_text)
            
            # Prepare API call parameters
            params = {
                "model": self.model_name,
                "messages": mistral_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.params
            }
            
            # Add tools if provided
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
                
            # Make the API call
            response = self.client.chat(
                **params
            )
            
            # Extract response content
            result = {"content": response.choices[0].message.content}
            
            # Add tool calls if present
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in response.choices[0].message.tool_calls
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