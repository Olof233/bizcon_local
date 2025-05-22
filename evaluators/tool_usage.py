# filepath: /Users/ahstanin/GitHub/Olib-AI/bizcon/evaluators/tool_usage.py
"""
Tool usage evaluator for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import re

from .base import BaseEvaluator


class ToolUsageEvaluator(BaseEvaluator):
    """
    Evaluator for assessing how effectively a model uses available tools.
    
    Measures whether the model selects appropriate tools, uses correct parameters,
    makes efficient calls, and correctly interprets tool results.
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the tool usage evaluator.
        
        Args:
            weight: Weight of this evaluator in the overall score (0-1)
        """
        super().__init__(name="Tool Usage", weight=weight)
    
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the model's tool usage effectiveness.
        
        Scoring criteria:
        - Tool selection appropriateness (0-3 points)
        - Parameter quality (0-3 points)
        - Call efficiency (0-2 points)
        - Interpretation of tool results (0-2 points)
        
        Args:
            response: Model response
            scenario: Business scenario object
            turn_index: Current turn index
            conversation_history: Previous turns in the conversation
            tool_calls: List of tool calls made during this turn
            
        Returns:
            Dictionary with scores and explanation
        """
        # Get response text
        response_text = response.get("content", "")
        
        # Get expected tool calls from scenario's ground truth
        ground_truth = scenario.get_ground_truth()
        expected_tool_calls = ground_truth.get("expected_tool_calls", [])
        
        # Initialize scores and explanations
        selection_score = 0.0
        selection_explanation = ""
        
        parameter_score = 0.0
        parameter_explanation = ""
        
        efficiency_score = 0.0
        efficiency_explanation = ""
        
        interpretation_score = 0.0
        interpretation_explanation = ""
        
        # Skip evaluation if no tools were expected for this turn
        if not expected_tool_calls:
            if not tool_calls:
                # Correctly didn't use tools when none were expected
                return {
                    "score": self.max_score,
                    "normalized_score": self.normalize_score(self.max_score),
                    "explanation": "No tools were expected or used for this turn.",
                    "details": {
                        "selection": {"score": 3.0, "explanation": "Correctly didn't use tools when none were expected"},
                        "parameters": {"score": 3.0, "explanation": "N/A - No tools used"},
                        "efficiency": {"score": 2.0, "explanation": "N/A - No tools used"},
                        "interpretation": {"score": 2.0, "explanation": "N/A - No tools used"}
                    }
                }
            else:
                # Used tools when none were expected
                return {
                    "score": 0.0,
                    "normalized_score": self.normalize_score(0.0),
                    "explanation": "Used tools when none were expected for this turn.",
                    "details": {
                        "selection": {"score": 0.0, "explanation": "Unnecessarily used tools when none were expected"},
                        "parameters": {"score": 0.0, "explanation": "N/A - No tools should have been used"},
                        "efficiency": {"score": 0.0, "explanation": "N/A - No tools should have been used"},
                        "interpretation": {"score": 0.0, "explanation": "N/A - No tools should have been used"}
                    }
                }
        
        # Handle case where tools were expected but none were used
        if expected_tool_calls and not tool_calls:
            return {
                "score": 0.0,
                "normalized_score": self.normalize_score(0.0),
                "explanation": "Failed to use tools when they were expected for this turn.",
                "details": {
                    "selection": {"score": 0.0, "explanation": "Failed to use any tools when they were expected"},
                    "parameters": {"score": 0.0, "explanation": "N/A - No tools used"},
                    "efficiency": {"score": 0.0, "explanation": "N/A - No tools used"},
                    "interpretation": {"score": 0.0, "explanation": "N/A - No tools used"}
                }
            }
        
        # 1. Evaluate tool selection appropriateness
        selection_score, selection_explanation = self._evaluate_tool_selection(
            tool_calls, 
            expected_tool_calls
        )
        
        # 2. Evaluate parameter quality
        parameter_score, parameter_explanation = self._evaluate_parameter_quality(
            tool_calls, 
            expected_tool_calls
        )
        
        # 3. Evaluate call efficiency
        efficiency_score, efficiency_explanation = self._evaluate_call_efficiency(
            tool_calls, 
            expected_tool_calls
        )
        
        # 4. Evaluate interpretation of tool results
        interpretation_score, interpretation_explanation = self._evaluate_tool_interpretation(
            response_text, 
            tool_calls
        )
        
        # Calculate total score
        total_score = selection_score + parameter_score + efficiency_score + interpretation_score
        
        return {
            "score": total_score,
            "normalized_score": self.normalize_score(total_score),
            "explanation": self._generate_summary_explanation(
                selection_explanation,
                parameter_explanation,
                efficiency_explanation,
                interpretation_explanation
            ),
            "details": {
                "selection": {"score": selection_score, "explanation": selection_explanation},
                "parameters": {"score": parameter_score, "explanation": parameter_explanation},
                "efficiency": {"score": efficiency_score, "explanation": efficiency_explanation},
                "interpretation": {"score": interpretation_score, "explanation": interpretation_explanation}
            }
        }
    
    def _evaluate_tool_selection(self, 
                               tool_calls: List[Dict[str, Any]], 
                               expected_tool_calls: List[Dict[str, Any]]) -> tuple:
        """
        Evaluate whether appropriate tools were selected.
        
        Args:
            tool_calls: Actual tool calls made
            expected_tool_calls: Expected tool calls from ground truth
            
        Returns:
            Tuple of (score, explanation)
        """
        # Extract tool IDs from actual and expected tool calls
        actual_tool_ids = [call.get("tool_id") for call in tool_calls]
        expected_tool_ids = [call.get("tool_id") for call in expected_tool_calls]
        
        # Count how many expected tools were used
        correct_tools = 0
        for tool_id in expected_tool_ids:
            if tool_id in actual_tool_ids:
                correct_tools += 1
        
        # Count unnecessary tools
        unnecessary_tools = 0
        for tool_id in actual_tool_ids:
            if tool_id not in expected_tool_ids:
                unnecessary_tools += 1
        
        # Calculate score based on correctness and precision
        if len(expected_tool_ids) == 0:
            expected_tool_coverage = 1.0  # No tools expected, so coverage is perfect
        else:
            expected_tool_coverage = correct_tools / len(expected_tool_ids)
        
        unnecessary_penalty = min(1.0, unnecessary_tools * 0.33)  # Penalty for each unnecessary tool
        
        # Calculate final score (max 3.0)
        score = 3.0 * expected_tool_coverage - unnecessary_penalty
        score = max(0.0, min(3.0, score))
        
        # Generate explanation
        if score >= 3.0:
            explanation = "Selected all appropriate tools without unnecessary ones"
        elif score >= 2.0:
            explanation = f"Selected most appropriate tools with {unnecessary_tools} unnecessary ones"
        elif score >= 1.0:
            explanation = f"Selected some appropriate tools but missed others or made unnecessary calls"
        else:
            explanation = "Failed to select appropriate tools or made many unnecessary tool calls"
        
        return score, explanation
    
    def _evaluate_parameter_quality(self, 
                                  tool_calls: List[Dict[str, Any]], 
                                  expected_tool_calls: List[Dict[str, Any]]) -> tuple:
        """
        Evaluate the quality of parameters used in tool calls.
        
        Args:
            tool_calls: Actual tool calls made
            expected_tool_calls: Expected tool calls from ground truth
            
        Returns:
            Tuple of (score, explanation)
        """
        # If no tool calls were made, return minimum score
        if not tool_calls:
            return 0.0, "No tool calls were made"
        
        # Map tool calls by tool_id for easier comparison
        actual_by_id = {call.get("tool_id"): call.get("parameters", {}) 
                       for call in tool_calls}
        expected_by_id = {call.get("tool_id"): call.get("parameters", {}) 
                         for call in expected_tool_calls}
        
        # Track parameter quality scores for each tool call
        parameter_scores = []
        
        # Evaluate each actual tool call
        for tool_id, actual_params in actual_by_id.items():
            # If this tool wasn't expected, skip parameter evaluation
            if tool_id not in expected_by_id:
                continue
                
            expected_params = expected_by_id[tool_id]
            
            # Calculate parameter match score for this tool
            if not expected_params:
                # If no specific parameters were expected, give full score
                parameter_scores.append(1.0)
            else:
                # Check each expected parameter
                param_matches = 0
                total_params = len(expected_params)
                
                for param_name, expected_value in expected_params.items():
                    actual_value = actual_params.get(param_name)
                    
                    # Parameter is missing
                    if param_name not in actual_params:
                        continue
                        
                    # Parameter values match exactly or are both non-empty
                    if actual_value == expected_value or (actual_value and expected_value):
                        param_matches += 1
                    # Parameter values are different
                    else:
                        param_matches += 0.5  # Partial credit for having the parameter
                
                # Calculate match ratio for this tool
                match_ratio = param_matches / total_params
                parameter_scores.append(match_ratio)
        
        # Calculate average parameter quality score
        if parameter_scores:
            avg_param_score = sum(parameter_scores) / len(parameter_scores)
            # Scale to 0-3 range
            score = 3.0 * avg_param_score
        else:
            score = 0.0
        
        # Generate explanation
        if score >= 2.5:
            explanation = "Excellent parameter selection with all required fields"
        elif score >= 1.5:
            explanation = "Good parameter selection with most required fields"
        elif score >= 0.5:
            explanation = "Fair parameter selection with some missing or incorrect fields"
        else:
            explanation = "Poor parameter selection with many missing or incorrect fields"
        
        return score, explanation
    
    def _evaluate_call_efficiency(self, 
                                tool_calls: List[Dict[str, Any]], 
                                expected_tool_calls: List[Dict[str, Any]]) -> tuple:
        """
        Evaluate the efficiency of tool calls (avoiding redundant or unnecessary calls).
        
        Args:
            tool_calls: Actual tool calls made
            expected_tool_calls: Expected tool calls from ground truth
            
        Returns:
            Tuple of (score, explanation)
        """
        # Count total expected and actual calls
        n_expected = len(expected_tool_calls)
        n_actual = len(tool_calls)
        
        # Calculate efficiency ratio
        if n_expected == 0:
            efficiency_ratio = 0.0 if n_actual > 0 else 1.0
        else:
            # Ideal case: n_actual = n_expected
            efficiency_ratio = 1.0 - min(1.0, abs(n_actual - n_expected) / max(1, n_expected))
        
        # Check for duplicate calls to the same tool
        tool_id_counts = {}
        for call in tool_calls:
            tool_id = call.get("tool_id")
            tool_id_counts[tool_id] = tool_id_counts.get(tool_id, 0) + 1
        
        # Penalize for duplicate calls
        duplicate_penalty = 0.0
        for tool_id, count in tool_id_counts.items():
            # More than 2 calls to same tool is considered inefficient
            if count > 2:
                duplicate_penalty = min(1.0, duplicate_penalty + 0.25 * (count - 2))
        
        # Calculate final score (max 2.0)
        score = 2.0 * efficiency_ratio - duplicate_penalty
        score = max(0.0, min(2.0, score))
        
        # Generate explanation
        if score >= 1.75:
            explanation = "Highly efficient tool usage with optimal number of calls"
        elif score >= 1.25:
            explanation = "Efficient tool usage with minimal redundancy"
        elif score >= 0.75:
            explanation = "Moderately efficient tool usage with some redundancy"
        elif score >= 0.25:
            explanation = "Inefficient tool usage with unnecessary or duplicate calls"
        else:
            explanation = "Very inefficient tool usage with many unnecessary or duplicate calls"
        
        return score, explanation
    
    def _evaluate_tool_interpretation(self, 
                                    response_text: str, 
                                    tool_calls: List[Dict[str, Any]]) -> tuple:
        """
        Evaluate how well the model interprets and incorporates tool results.
        
        Args:
            response_text: Model's response text
            tool_calls: Tool calls with their results
            
        Returns:
            Tuple of (score, explanation)
        """
        # If no tool calls were made, return minimum score
        if not tool_calls:
            return 0.0, "No tool calls were made to interpret"
        
        # Track which tool results were incorporated in the response
        tool_incorporations = []
        
        for call in tool_calls:
            tool_id = call.get("tool_id")
            result = call.get("result", {})
            
            # Skip calls without results
            if not result:
                continue
                
            # Convert result to string if it's a dict/list
            if isinstance(result, (dict, list)):
                result_str = json.dumps(result)
            else:
                result_str = str(result)
            
            # Check if key information from the result appears in the response
            # We'll look for distinctive parts of the result
            incorporated = False
            
            # For dict results, check if key-value pairs are mentioned
            if isinstance(result, dict):
                for key, value in result.items():
                    # Skip empty values or complex nested structures
                    if not value or isinstance(value, (dict, list)):
                        continue
                        
                    # Check if both key and value are mentioned in proximity
                    key_str = str(key)
                    value_str = str(value)
                    
                    # Skip very short or common values
                    if len(value_str) < 3 or value_str.lower() in ["yes", "no", "true", "false"]:
                        continue
                    
                    # Check for key-value pair in response
                    if key_str in response_text and value_str in response_text:
                        incorporated = True
                        break
            
            # For simple results, check if distinctive parts are mentioned
            else:
                # Extract distinctive parts (longer number sequences, IDs, etc.)
                distinctive_parts = re.findall(r'\b[A-Za-z0-9_-]{4,}\b', result_str)
                
                for part in distinctive_parts:
                    if part in response_text:
                        incorporated = True
                        break
            
            tool_incorporations.append(incorporated)
        
        # Calculate incorporation ratio
        if tool_incorporations:
            incorporation_ratio = sum(1 for inc in tool_incorporations if inc) / len(tool_incorporations)
        else:
            incorporation_ratio = 0.0
        
        # Calculate final score (max 2.0)
        score = 2.0 * incorporation_ratio
        
        # Generate explanation
        if score >= 1.75:
            explanation = "Excellent incorporation of tool results into response"
        elif score >= 1.25:
            explanation = "Good incorporation of most tool results into response"
        elif score >= 0.75:
            explanation = "Partial incorporation of tool results into response"
        elif score >= 0.25:
            explanation = "Limited incorporation of tool results into response"
        else:
            explanation = "Failed to incorporate tool results into response"
        
        return score, explanation
    
    def _generate_summary_explanation(self, 
                                     selection_explanation: str,
                                     parameter_explanation: str,
                                     efficiency_explanation: str,
                                     interpretation_explanation: str) -> str:
        """
        Generate a summary explanation from the individual criteria explanations.
        
        Args:
            selection_explanation: Explanation for tool selection
            parameter_explanation: Explanation for parameter quality
            efficiency_explanation: Explanation for call efficiency
            interpretation_explanation: Explanation for result interpretation
            
        Returns:
            Summary explanation
        """
        return (f"Tool Usage Assessment: {selection_explanation}. "
                f"{parameter_explanation}. {efficiency_explanation}. "
                f"{interpretation_explanation}.")