"""
Base class for business conversation scenarios.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import uuid
import json


class BusinessScenario(ABC):
    """Base class for all business conversation scenarios."""
    
    def __init__(self, 
                 scenario_id: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 industry: Optional[str] = None,
                 complexity: str = "medium",
                 tools_required: Optional[List[str]] = None):
        """
        Initialize the business scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
            name: Human-readable name
            description: Detailed description
            industry: Industry category (finance, healthcare, etc.)
            complexity: Scenario complexity (simple, medium, complex)
            tools_required: List of tool IDs that may be needed for this scenario
        """
        self.scenario_id = scenario_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description
        self.industry = industry
        self.complexity = complexity
        self.tools_required = tools_required or []
        self._conversation_flow = self._initialize_conversation()
        self._ground_truth = self._initialize_ground_truth()
    
    @abstractmethod
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow for this scenario.
        
        Returns:
            List of conversation turns, each containing user messages and expected bot actions
        """
        pass
    
    @abstractmethod
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information for evaluating responses.
        
        Returns:
            Dictionary with ground truth data
        """
        pass
    
    def get_conversation(self) -> List[Dict[str, Any]]:
        """
        Get the conversation flow for this scenario.
        
        Returns:
            List of conversation turns
        """
        return self._conversation_flow
    
    def get_initial_message(self) -> Dict[str, str]:
        """
        Get the initial user message to start the conversation.
        
        Returns:
            Message in the format {"role": "user", "content": "..."}
        """
        if not self._conversation_flow:
            raise ValueError(f"Conversation flow not initialized for scenario {self.scenario_id}")
        
        return {"role": "user", "content": self._conversation_flow[0]["user_message"]}
    
    def get_ground_truth(self) -> Dict[str, Any]:
        """
        Get ground truth data for evaluation.
        
        Returns:
            Dictionary with ground truth information
        """
        return self._ground_truth
    
    def get_follow_up_message(self, turn_index: int) -> Optional[Dict[str, str]]:
        """
        Get follow-up user message for a multi-turn conversation.
        
        Args:
            turn_index: Index of the current turn
            
        Returns:
            Message in the format {"role": "user", "content": "..."} or None if no more turns
        """
        if turn_index + 1 >= len(self._conversation_flow):
            return None
        
        return {"role": "user", "content": self._conversation_flow[turn_index + 1]["user_message"]}
    
    def get_expected_tool_calls(self, turn_index: int) -> List[Dict[str, Any]]:
        """
        Get the expected tool calls for a given conversation turn.
        
        Args:
            turn_index: Index of the current turn
            
        Returns:
            List of expected tool calls with parameters
        """
        if turn_index >= len(self._conversation_flow):
            return []
        
        return self._conversation_flow[turn_index].get("expected_tool_calls", [])
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get scenario metadata.
        
        Returns:
            Dictionary with scenario metadata
        """
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "industry": self.industry,
            "complexity": self.complexity,
            "tools_required": self.tools_required,
            "num_turns": len(self._conversation_flow)
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.scenario_id})"