"""
Base class for evaluators.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import json


class BaseEvaluator(ABC):
    """Base class for all response evaluators."""
    
    def __init__(self, name: str, weight: float = 1.0):
        """
        Initialize the evaluator.
        
        Args:
            name: Evaluator name
            weight: Weight of this evaluator in the overall score (0-1)
        """
        self.name = name
        self.weight = weight
        self.min_score = 0.0
        self.max_score = 10.0
    
    @abstractmethod
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a model response.
        
        Args:
            response: Model response
            scenario: Business scenario object
            turn_index: Current turn index
            conversation_history: Previous turns in the conversation
            tool_calls: List of tool calls made during this turn
            
        Returns:
            Dictionary with scores and explanation
        """
        pass
    
    def normalize_score(self, score: float) -> float:
        """
        Normalize a score to be between min_score and max_score.
        
        Args:
            score: Raw score
            
        Returns:
            Normalized score
        """
        if score < self.min_score:
            return self.min_score
        elif score > self.max_score:
            return self.max_score
        return score
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get evaluator metadata.
        
        Returns:
            Dictionary with evaluator metadata
        """
        return {
            "name": self.name,
            "weight": self.weight,
            "min_score": self.min_score,
            "max_score": self.max_score
        }
    
    def __str__(self) -> str:
        return f"{self.name} (weight: {self.weight})"