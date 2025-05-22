"""
Scenario runner for executing business conversation scenarios.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import time

from models.base import ModelClient
from scenarios.base import BusinessScenario
from evaluators.base import BaseEvaluator
from tools.base import BusinessTool


class ScenarioRunner:
    """Runner for executing a business scenario with a model."""
    
    def __init__(self, 
                 model: ModelClient,
                 scenario: BusinessScenario,
                 evaluators: List[BaseEvaluator],
                 tools: Dict[str, BusinessTool]):
        """
        Initialize the scenario runner.
        
        Args:
            model: Model client to use
            scenario: Business scenario to run
            evaluators: List of evaluators to apply
            tools: Dictionary of available tools
        """
        self.model = model
        self.scenario = scenario
        self.evaluators = evaluators
        self.tools = tools
        self.conversation_history = []
        self.tool_calls_history = []
    
    def run(self) -> Dict[str, Any]:
        """
        Run the scenario and evaluate the model's performance.
        
        Returns:
            Dictionary with evaluation results
        """
        # Initialize results
        results = {
            "scenario": self.scenario.get_metadata(),
            "model": self.model.model_name,
            "start_time": time.time(),
            "turns": [],
            "category_scores": {},
            "overall_score": 0.0
        }
        
        # Reset conversation history
        self.conversation_history = []
        self.tool_calls_history = []
        
        # Get tool definitions for the model
        tool_definitions = []
        for tool_id in self.scenario.tools_required:
            if tool_id in self.tools:
                tool_definitions.append(self.tools[tool_id].get_definition())
        
        # Start the conversation with the initial message
        initial_message = self.scenario.get_initial_message()
        self.conversation_history.append(initial_message)
        
        # Run each turn of the conversation
        current_turn = 0
        max_turns = len(self.scenario.get_conversation())
        
        while current_turn < max_turns:
            # Generate model response
            response = self._generate_response(tool_definitions)
            
            # Handle tool calls if present
            tool_calls = []
            if "tool_calls" in response:
                tool_calls = self._process_tool_calls(response["tool_calls"])
                self.tool_calls_history.append(tool_calls)
            
            # Evaluate the response
            turn_evaluation = self._evaluate_response(response, current_turn, tool_calls)
            
            # Add to results
            results["turns"].append({
                "turn_index": current_turn,
                "user_message": self.conversation_history[-2]["content"] if len(self.conversation_history) >= 2 else "",
                "model_response": response,
                "tool_calls": tool_calls,
                "evaluation": turn_evaluation
            })
            
            # Get follow-up message if available
            follow_up = self.scenario.get_follow_up_message(current_turn)
            if follow_up:
                self.conversation_history.append(follow_up)
                current_turn += 1
            else:
                break
        
        # Calculate final scores
        results["category_scores"] = self._calculate_category_scores(results["turns"])
        results["overall_score"] = self._calculate_overall_score(results["category_scores"])
        results["duration"] = time.time() - results["start_time"]
        
        return results
    
    def _generate_response(self, tool_definitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            tool_definitions: List of tool definitions
            
        Returns:
            Model response
        """
        response = self.model.generate_response(
            messages=self.conversation_history,
            tools=tool_definitions if tool_definitions else None
        )
        
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.get("content", ""),
            **({} if "tool_calls" not in response else {"tool_calls": response["tool_calls"]})
        })
        
        return response
    
    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process tool calls from the model response.
        
        Args:
            tool_calls: List of tool calls from the model
            
        Returns:
            List of processed tool calls with results
        """
        processed_calls = []
        
        for call in tool_calls:
            tool_id = call.get("function", {}).get("name")
            parameters = json.loads(call.get("function", {}).get("arguments", "{}"))
            
            # Find the tool
            if tool_id in self.tools:
                # Execute the tool
                result = self.tools[tool_id].call(parameters)
                
                # Add to processed calls
                processed_calls.append({
                    "tool_id": tool_id,
                    "parameters": parameters,
                    "result": result
                })
                
                # Add tool result to conversation history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "name": tool_id,
                    "content": json.dumps(result)
                })
            else:
                # Tool not found
                error_result = {
                    "error": "ToolNotFound",
                    "message": f"Tool '{tool_id}' is not available",
                    "status": "error"
                }
                
                processed_calls.append({
                    "tool_id": tool_id,
                    "parameters": parameters,
                    "result": error_result
                })
                
                # Add error to conversation history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "name": tool_id,
                    "content": json.dumps(error_result)
                })
        
        return processed_calls
    
    def _evaluate_response(self, 
                          response: Dict[str, Any], 
                          turn_index: int,
                          tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a model response using all evaluators.
        
        Args:
            response: Model response
            turn_index: Current turn index
            tool_calls: List of tool calls made during this turn
            
        Returns:
            Dictionary with evaluation results
        """
        evaluation = {}
        
        for evaluator in self.evaluators:
            evaluation[evaluator.name] = evaluator.evaluate(
                response=response,
                scenario=self.scenario,
                turn_index=turn_index,
                conversation_history=self.conversation_history,
                tool_calls=tool_calls
            )
        
        return evaluation
    
    def _calculate_category_scores(self, turns: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average scores for each evaluation category.
        
        Args:
            turns: List of conversation turns with evaluations
            
        Returns:
            Dictionary with category scores
        """
        category_scores = {}
        
        # Organize all scores by category
        all_scores = {}
        for turn in turns:
            for category, evaluation in turn["evaluation"].items():
                if category not in all_scores:
                    all_scores[category] = []
                all_scores[category].append(evaluation["score"])
        
        # Calculate average score for each category
        for category, scores in all_scores.items():
            category_scores[category] = sum(scores) / len(scores) if scores else 0.0
        
        return category_scores
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """
        Calculate overall weighted score.
        
        Args:
            category_scores: Dictionary with category scores
            
        Returns:
            Overall weighted score
        """
        total_score = 0.0
        total_weight = 0.0
        
        for evaluator in self.evaluators:
            if evaluator.name in category_scores:
                total_score += category_scores[evaluator.name] * evaluator.weight
                total_weight += evaluator.weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight