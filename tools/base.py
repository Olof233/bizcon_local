"""
Base class for business tools.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
import json
import random


class BusinessTool(ABC):
    """Base class for all business tools."""
    
    def __init__(self, 
                 tool_id: str,
                 name: str,
                 description: str,
                 parameters: Dict[str, Any],
                 error_rate: float = 0.05):
        """
        Initialize the business tool.
        
        Args:
            tool_id: Unique identifier for the tool
            name: Human-readable name
            description: Detailed description
            parameters: Dictionary describing expected parameters
            error_rate: Probability of simulating a tool error (0-1)
        """
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.parameters = parameters
        self.error_rate = error_rate
        self.call_count = 0
        self.error_count = 0
    
    def get_definition(self) -> Dict[str, Any]:
        """
        Get the tool definition for LLM function calling.
        
        Returns:
            Dictionary with tool definition
        """
        return {
            "type": "function",
            "function": {
                "name": self.tool_id,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": [k for k, v in self.parameters.items() 
                               if v.get("required", False)]
                }
            }
        }
    
    def call(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the tool with the given parameters.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Result of the tool call
        """
        self.call_count += 1
        
        # Validate parameters
        missing_params = []
        for param_name, param_def in self.parameters.items():
            if param_def.get("required", False) and param_name not in parameters:
                missing_params.append(param_name)
        
        if missing_params:
            self.error_count += 1
            return {
                "error": "MissingParameters",
                "message": f"Missing required parameters: {', '.join(missing_params)}",
                "status": "error"
            }
        
        # Simulate random errors if error_rate > 0
        if self.error_rate > 0 and random.random() < self.error_rate:
            self.error_count += 1
            return self._generate_random_error()
        
        # Call the actual implementation
        try:
            result = self._execute(parameters)
            return {
                "result": result,
                "status": "success"
            }
        except Exception as e:
            self.error_count += 1
            return {
                "error": type(e).__name__,
                "message": str(e),
                "status": "error"
            }
    
    @abstractmethod
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the tool functionality.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Result of the tool execution
        """
        pass
    
    def _generate_random_error(self) -> Dict[str, str]:
        """
        Generate a random business-related error response.
        
        Returns:
            Error response dictionary
        """
        errors = [
            {"error": "ServiceUnavailable", "message": "Service temporarily unavailable. Please try again later."},
            {"error": "DatabaseTimeout", "message": "Database query timed out. Please try with more specific parameters."},
            {"error": "RateLimitExceeded", "message": "API rate limit exceeded. Please wait before making more requests."},
            {"error": "PermissionDenied", "message": "Insufficient permissions to access this resource."},
            {"error": "InvalidData", "message": "The provided data is invalid or in an incorrect format."}
        ]
        error = random.choice(errors)
        error["status"] = "error"
        return error
    
    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get tool usage statistics.
        
        Returns:
            Dictionary with usage information
        """
        return {
            "tool_id": self.tool_id,
            "calls": self.call_count,
            "errors": self.error_count,
            "success_rate": (self.call_count - self.error_count) / self.call_count if self.call_count > 0 else 0
        } # type: ignore
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.call_count = 0
        self.error_count = 0
    
    def __str__(self) -> str:
        return f"{self.name} ({self.tool_id})"