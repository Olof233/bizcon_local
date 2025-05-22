"""
Performance evaluator for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import time
import statistics
import json

from .base import BaseEvaluator


class PerformanceEvaluator(BaseEvaluator):
    """
    Evaluator for assessing operational performance of model responses.
    
    Measures response time, token efficiency, and computational resource usage
    to evaluate the operational efficiency of models in business scenarios.
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the performance evaluator.
        
        Args:
            weight: Weight of this evaluator in the overall score (0-1)
        """
        super().__init__(name="Performance", weight=weight)
    
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the operational performance of a model response.
        
        Scoring criteria:
        - Response time (0-4 points)
        - Token efficiency (0-3 points)
        - Tool usage efficiency (0-3 points)
        
        Args:
            response: Model response
            scenario: Business scenario object
            turn_index: Current turn index
            conversation_history: Previous turns in the conversation
            tool_calls: List of tool calls made during this turn
            
        Returns:
            Dictionary with scores and explanation
        """
        # Extract performance metrics from the response
        metrics = response.get("metrics", {})
        response_time_ms = metrics.get("response_time_ms", 0)
        prompt_tokens = metrics.get("prompt_tokens", 0)
        completion_tokens = metrics.get("completion_tokens", 0)
        total_tokens = metrics.get("total_tokens", 0) or (prompt_tokens + completion_tokens)
        
        # Initialize scores and explanations
        response_time_score = 0.0
        response_time_explanation = ""
        
        token_efficiency_score = 0.0
        token_efficiency_explanation = ""
        
        tool_efficiency_score = 0.0
        tool_efficiency_explanation = ""
        
        # 1. Evaluate response time
        response_time_score, response_time_explanation = self._evaluate_response_time(
            response_time_ms,
            scenario.get_complexity()
        )
        
        # 2. Evaluate token efficiency
        token_efficiency_score, token_efficiency_explanation = self._evaluate_token_efficiency(
            prompt_tokens,
            completion_tokens,
            scenario.get_complexity()
        )
        
        # 3. Evaluate tool usage efficiency
        tool_efficiency_score, tool_efficiency_explanation = self._evaluate_tool_efficiency(
            tool_calls,
            scenario.get_ground_truth()
        )
        
        # Calculate total score
        total_score = response_time_score + token_efficiency_score + tool_efficiency_score
        
        # Normalize to 0-10 scale
        normalized_score = self.normalize_score(total_score)
        
        return {
            "score": normalized_score,
            "breakdown": {
                "response_time_score": response_time_score,
                "token_efficiency_score": token_efficiency_score,
                "tool_efficiency_score": tool_efficiency_score
            },
            "explanation": {
                "response_time": response_time_explanation,
                "token_efficiency": token_efficiency_explanation,
                "tool_efficiency": tool_efficiency_explanation
            },
            "metrics": {
                "response_time_ms": response_time_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "tool_calls_count": len(tool_calls)
            },
            "max_possible": 10.0
        }
    
    def _evaluate_response_time(self, response_time_ms: int, scenario_complexity: str) -> tuple:
        """
        Evaluate the response time.
        
        Args:
            response_time_ms: Response time in milliseconds
            scenario_complexity: Complexity of the scenario
            
        Returns:
            Tuple of (score, explanation)
        """
        # Define response time thresholds based on scenario complexity
        thresholds = {
            "simple": {
                "excellent": 1500,
                "good": 3000,
                "adequate": 5000
            },
            "medium": {
                "excellent": 2500,
                "good": 5000,
                "adequate": 8000
            },
            "complex": {
                "excellent": 4000,
                "good": 8000,
                "adequate": 12000
            }
        }
        
        # Use medium complexity thresholds as default
        complexity_thresholds = thresholds.get(scenario_complexity, thresholds["medium"])
        
        # Score based on response time
        if response_time_ms <= complexity_thresholds["excellent"]:
            score = 4.0
            explanation = f"Excellent response time of {response_time_ms}ms, well under the {complexity_thresholds['excellent']}ms threshold for {scenario_complexity} scenarios"
        elif response_time_ms <= complexity_thresholds["good"]:
            score = 3.0
            explanation = f"Good response time of {response_time_ms}ms, under the {complexity_thresholds['good']}ms threshold for {scenario_complexity} scenarios"
        elif response_time_ms <= complexity_thresholds["adequate"]:
            score = 2.0
            explanation = f"Adequate response time of {response_time_ms}ms for {scenario_complexity} scenarios"
        elif response_time_ms <= complexity_thresholds["adequate"] * 1.5:
            score = 1.0
            explanation = f"Slow response time of {response_time_ms}ms, above the {complexity_thresholds['adequate']}ms threshold for {scenario_complexity} scenarios"
        else:
            score = 0.0
            explanation = f"Very slow response time of {response_time_ms}ms, far above acceptable thresholds for {scenario_complexity} scenarios"
        
        return score, explanation
    
    def _evaluate_token_efficiency(self, prompt_tokens: int, completion_tokens: int, scenario_complexity: str) -> tuple:
        """
        Evaluate token efficiency.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            scenario_complexity: Complexity of the scenario
            
        Returns:
            Tuple of (score, explanation)
        """
        # Define token thresholds based on scenario complexity
        thresholds = {
            "simple": {
                "excellent_completion": 200,
                "good_completion": 400,
                "adequate_completion": 600
            },
            "medium": {
                "excellent_completion": 400,
                "good_completion": 800,
                "adequate_completion": 1200
            },
            "complex": {
                "excellent_completion": 800,
                "good_completion": 1500,
                "adequate_completion": 2500
            }
        }
        
        # Use medium complexity thresholds as default
        complexity_thresholds = thresholds.get(scenario_complexity, thresholds["medium"])
        
        # Calculate completion-to-prompt ratio (a lower ratio is generally better)
        ratio = completion_tokens / prompt_tokens if prompt_tokens > 0 else float('inf')
        
        # Score based on completion tokens and ratio
        if completion_tokens <= complexity_thresholds["excellent_completion"] and ratio < 0.5:
            score = 3.0
            explanation = f"Excellent token efficiency with {completion_tokens} completion tokens and 1:{1/ratio:.1f} prompt-to-completion ratio"
        elif completion_tokens <= complexity_thresholds["good_completion"] and ratio < 0.8:
            score = 2.0
            explanation = f"Good token efficiency with {completion_tokens} completion tokens and 1:{1/ratio:.1f} prompt-to-completion ratio"
        elif completion_tokens <= complexity_thresholds["adequate_completion"]:
            score = 1.0
            explanation = f"Adequate token efficiency with {completion_tokens} completion tokens"
        else:
            score = 0.0
            explanation = f"Poor token efficiency with {completion_tokens} completion tokens, exceeding the {complexity_thresholds['adequate_completion']} threshold"
        
        return score, explanation
    
    def _evaluate_tool_efficiency(self, tool_calls: List[Dict[str, Any]], ground_truth: Dict[str, Any]) -> tuple:
        """
        Evaluate tool usage efficiency.
        
        Args:
            tool_calls: List of tool calls made
            ground_truth: Ground truth for the current turn
            
        Returns:
            Tuple of (score, explanation)
        """
        # Get expected tool usage
        expected_tools = ground_truth.get("expected_tools", [])
        expected_tool_count = len(expected_tools)
        
        # If no tools are expected, return full score
        if expected_tool_count == 0:
            if not tool_calls:
                return 3.0, "Correctly used no tools when none were needed"
            else:
                return 0.0, f"Unnecessarily used {len(tool_calls)} tools when none were needed"
        
        # Count actual tool usage
        actual_tool_count = len(tool_calls)
        
        # Calculate over/underuse
        tool_difference = abs(actual_tool_count - expected_tool_count)
        
        # Check which expected tools were actually used
        actual_tool_ids = [call.get("tool_id", "") for call in tool_calls]
        expected_tools_used = sum(1 for tool in expected_tools if tool in actual_tool_ids)
        
        # Calculate precision and recall
        precision = expected_tools_used / actual_tool_count if actual_tool_count > 0 else 0
        recall = expected_tools_used / expected_tool_count if expected_tool_count > 0 else 0
        
        # Calculate F1 score (harmonic mean of precision and recall)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Score based on tool usage efficiency
        if f1_score >= 0.9 and tool_difference <= 1:
            score = 3.0
            explanation = f"Excellent tool usage efficiency with {expected_tools_used}/{expected_tool_count} expected tools used correctly"
        elif f1_score >= 0.7 and tool_difference <= 2:
            score = 2.0
            explanation = f"Good tool usage efficiency with {expected_tools_used}/{expected_tool_count} expected tools used"
        elif f1_score >= 0.5:
            score = 1.0
            explanation = f"Adequate tool usage with {expected_tools_used}/{expected_tool_count} expected tools used but some inefficiency"
        else:
            score = 0.0
            explanation = f"Poor tool usage efficiency with only {expected_tools_used}/{expected_tool_count} expected tools used correctly"
        
        return score, explanation