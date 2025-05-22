"""
Business value evaluator for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import re
import json

from .base import BaseEvaluator


class BusinessValueEvaluator(BaseEvaluator):
    """
    Evaluator for assessing business value of model responses.
    
    Measures whether the model's response addresses the core business need,
    provides actionable information, and demonstrates business acumen.
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the business value evaluator.
        
        Args:
            weight: Weight of this evaluator in the overall score (0-1)
        """
        super().__init__(name="Business Value", weight=weight)
    
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate business value of a model response.
        
        Scoring criteria:
        - Addresses core business objective (0-4 points)
        - Provides actionable information (0-3 points)
        - Demonstrates business acumen/domain knowledge (0-3 points)
        
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
        
        # Get expected business value from scenario's ground truth
        ground_truth = scenario.get_ground_truth()
        expected_business_objective = ground_truth.get("business_objective", "")
        expected_action_items = ground_truth.get("action_items", [])
        expected_domain_knowledge = ground_truth.get("domain_knowledge", [])
        
        # Initialize scores and explanations
        objective_score = 0.0
        objective_explanation = ""
        
        actionable_score = 0.0
        actionable_explanation = ""
        
        acumen_score = 0.0
        acumen_explanation = ""
        
        # 1. Evaluate addressing core business objective
        if expected_business_objective:
            # Calculate relevance to business objective
            if self._contains_key_elements(response_text, expected_business_objective):
                objective_score = 4.0
                objective_explanation = "Response fully addresses the core business objective"
            elif self._partial_match(response_text, expected_business_objective, 0.7):
                objective_score = 3.0
                objective_explanation = "Response mostly addresses the core business objective"
            elif self._partial_match(response_text, expected_business_objective, 0.5):
                objective_score = 2.0
                objective_explanation = "Response partially addresses the core business objective"
            elif self._partial_match(response_text, expected_business_objective, 0.3):
                objective_score = 1.0
                objective_explanation = "Response minimally addresses the core business objective"
            else:
                objective_score = 0.0
                objective_explanation = "Response does not address the core business objective"
        
        # 2. Evaluate providing actionable information
        if expected_action_items:
            action_items_found = 0
            
            # Count how many expected action items are covered
            for item in expected_action_items:
                if self._contains_key_elements(response_text, item):
                    action_items_found += 1
            
            # Calculate score based on percentage of action items covered
            coverage_ratio = action_items_found / len(expected_action_items)
            
            if coverage_ratio >= 0.8:
                actionable_score = 3.0
                actionable_explanation = "Response provides comprehensive actionable information"
            elif coverage_ratio >= 0.5:
                actionable_score = 2.0
                actionable_explanation = "Response provides some actionable information"
            elif coverage_ratio > 0:
                actionable_score = 1.0
                actionable_explanation = "Response provides minimal actionable information"
            else:
                actionable_score = 0.0
                actionable_explanation = "Response provides no actionable information"
        
        # 3. Evaluate business acumen/domain knowledge
        if expected_domain_knowledge:
            knowledge_items_found = 0
            
            # Count how many expected knowledge points are covered
            for item in expected_domain_knowledge:
                if self._contains_key_elements(response_text, item):
                    knowledge_items_found += 1
            
            # Calculate score based on percentage of knowledge points covered
            knowledge_ratio = knowledge_items_found / len(expected_domain_knowledge)
            
            if knowledge_ratio >= 0.8:
                acumen_score = 3.0
                acumen_explanation = "Response demonstrates excellent business acumen and domain knowledge"
            elif knowledge_ratio >= 0.5:
                acumen_score = 2.0
                acumen_explanation = "Response demonstrates good business acumen and domain knowledge"
            elif knowledge_ratio > 0:
                acumen_score = 1.0
                acumen_explanation = "Response demonstrates minimal business acumen and domain knowledge"
            else:
                acumen_score = 0.0
                acumen_explanation = "Response demonstrates no relevant business acumen or domain knowledge"
        
        # Tool usage bonus: Check if the model used business-relevant tools effectively
        tool_usage_bonus = 0.0
        tool_usage_explanation = ""
        
        if tool_calls:
            business_value_tools = self._count_business_value_tools(tool_calls, ground_truth.get("relevant_tools", []))
            
            if business_value_tools > 0:
                tool_usage_bonus = min(business_value_tools, 1.0)  # Cap bonus at 1.0
                tool_usage_explanation = f"Model effectively used {business_value_tools} business-relevant tools"
        
        # Calculate total score
        total_score = objective_score + actionable_score + acumen_score + tool_usage_bonus
        
        # Normalize to 0-10 scale
        normalized_score = self.normalize_score(total_score)
        
        return {
            "score": normalized_score,
            "breakdown": {
                "objective_score": objective_score,
                "actionable_score": actionable_score,
                "acumen_score": acumen_score,
                "tool_usage_bonus": tool_usage_bonus
            },
            "explanation": {
                "objective": objective_explanation,
                "actionable": actionable_explanation,
                "acumen": acumen_explanation,
                "tool_usage": tool_usage_explanation
            },
            "max_possible": 10.0
        }
    
    def _contains_key_elements(self, text: str, target: str) -> bool:
        """
        Check if text contains the key elements from target.
        
        Args:
            text: Text to check
            target: Target text with key elements
            
        Returns:
            True if text contains key elements, False otherwise
        """
        # Extract key elements (nouns, main verbs, specific terms) from target
        key_terms = self._extract_key_terms(target)
        
        # Check if text contains all key terms
        text_lower = text.lower()
        for term in key_terms:
            if term.lower() not in text_lower:
                return False
        
        return True
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text.
        
        In a real implementation, this would use NLP to extract nouns, verbs, and specific terms.
        This simplified version extracts words that are likely to be significant.
        
        Args:
            text: Text to extract terms from
            
        Returns:
            List of key terms
        """
        # Simplified implementation - in production, use NLP
        # Remove common words and keep important ones
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as"}
        
        key_terms = [word for word in words if len(word) > 3 and word not in stopwords]
        
        # Keep only unique terms
        return list(set(key_terms))
    
    def _partial_match(self, text: str, target: str, threshold: float) -> bool:
        """
        Check if text partially matches target based on key term coverage.
        
        Args:
            text: Text to check
            target: Target text
            threshold: Minimum ratio of key terms that must be present
            
        Returns:
            True if partial match threshold is met, False otherwise
        """
        key_terms = self._extract_key_terms(target)
        
        if not key_terms:
            return False
        
        # Count how many key terms are in the text
        text_lower = text.lower()
        matches = sum(1 for term in key_terms if term.lower() in text_lower)
        
        # Calculate match ratio
        match_ratio = matches / len(key_terms)
        
        return match_ratio >= threshold
    
    def _count_business_value_tools(self, tool_calls: List[Dict[str, Any]], relevant_tools: List[str]) -> int:
        """
        Count how many business-relevant tools were used effectively.
        
        Args:
            tool_calls: List of tool calls made
            relevant_tools: List of tool IDs that are relevant for this scenario
            
        Returns:
            Number of business-relevant tools used effectively
        """
        if not relevant_tools:
            return 0
        
        business_value_tools = 0
        
        for tool_call in tool_calls:
            tool_id = tool_call.get("tool_id", "")
            
            if tool_id in relevant_tools:
                # In a more sophisticated implementation, also check if the tool was used correctly
                business_value_tools += 1
        
        return business_value_tools