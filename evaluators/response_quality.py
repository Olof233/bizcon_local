"""
Response quality evaluator for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import re
import difflib
import json

from .base import BaseEvaluator


class ResponseQualityEvaluator(BaseEvaluator):
    """
    Evaluator for assessing factual accuracy and completeness of model responses.
    
    Measures accuracy, completeness, relevance, and consistency with
    business facts and requirements.
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the response quality evaluator.
        
        Args:
            weight: Weight of this evaluator in the overall score (0-1)
        """
        super().__init__(name="Response Quality", weight=weight)
    
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the factual accuracy and completeness of a model response.
        
        Scoring criteria:
        - Factual accuracy (0-4 points)
        - Completeness (0-3 points)
        - Relevance (0-2 points)
        - Consistency (0-1 point)
        
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
        
        # Get ground truth data for this turn
        ground_truth = scenario.get_ground_truth()
        expected_facts = ground_truth.get("expected_facts", [])
        required_elements = ground_truth.get("required_elements", [])
        
        # Get additional context
        customer_query = None
        for i in range(len(conversation_history) - 1, -1, -1):
            if conversation_history[i].get("role") == "user":
                customer_query = conversation_history[i].get("content", "")
                break
        
        # Extract tool outputs for fact checking
        tool_outputs = {}
        for call in tool_calls:
            tool_id = call.get("tool_id", "")
            tool_output = call.get("output", {})
            tool_outputs[tool_id] = tool_output
        
        # Initialize scores and explanations
        accuracy_score = 0.0
        accuracy_explanation = ""
        
        completeness_score = 0.0
        completeness_explanation = ""
        
        relevance_score = 0.0
        relevance_explanation = ""
        
        consistency_score = 0.0
        consistency_explanation = ""
        
        # 1. Evaluate factual accuracy
        accuracy_score, accuracy_explanation, errors = self._evaluate_accuracy(
            response_text, 
            expected_facts,
            tool_outputs
        )
        
        # 2. Evaluate completeness
        completeness_score, completeness_explanation = self._evaluate_completeness(
            response_text,
            required_elements
        )
        
        # 3. Evaluate relevance
        relevance_score, relevance_explanation = self._evaluate_relevance(
            response_text,
            customer_query,
            ground_truth.get("query_intent", "")
        )
        
        # 4. Evaluate consistency
        consistency_score, consistency_explanation = self._evaluate_consistency(
            response_text,
            conversation_history,
            errors
        )
        
        # Calculate total score
        total_score = accuracy_score + completeness_score + relevance_score + consistency_score
        
        # Normalize to 0-10 scale
        normalized_score = self.normalize_score(total_score)
        
        return {
            "score": normalized_score,
            "breakdown": {
                "accuracy_score": accuracy_score,
                "completeness_score": completeness_score,
                "relevance_score": relevance_score,
                "consistency_score": consistency_score
            },
            "explanation": {
                "accuracy": accuracy_explanation,
                "completeness": completeness_explanation,
                "relevance": relevance_explanation,
                "consistency": consistency_explanation
            },
            "errors": errors,
            "max_possible": 10.0
        }
    
    def _evaluate_accuracy(self, text: str, expected_facts: List[str], tool_outputs: Dict[str, Any]) -> tuple:
        """
        Evaluate the factual accuracy of text.
        
        Args:
            text: Text to evaluate
            expected_facts: List of facts that should be included
            tool_outputs: Dictionary of tool outputs to verify facts against
            
        Returns:
            Tuple of (score, explanation, errors)
        """
        if not expected_facts:
            return 4.0, "No specific facts to verify in this response", []
        
        # Count correct, incorrect, and missing facts
        correct_facts = 0
        incorrect_facts = 0
        missing_facts = 0
        errors = []
        
        for fact in expected_facts:
            fact_key = fact.split(":")[0].strip() if ":" in fact else fact
            fact_value = fact.split(":", 1)[1].strip() if ":" in fact else None
            
            # Check if the fact key is mentioned
            if self._contains_key_elements(text.lower(), fact_key.lower()):
                # If there's a specific value to check
                if fact_value:
                    # Check if the value is correctly stated
                    if self._contains_key_elements(text.lower(), fact_value.lower()):
                        correct_facts += 1
                    else:
                        # Try to extract the actual value provided
                        actual_value = self._extract_value_for_key(text, fact_key)
                        incorrect_facts += 1
                        errors.append({
                            "type": "incorrect_fact",
                            "expected": fact,
                            "provided": f"{fact_key}: {actual_value}" if actual_value else f"{fact_key}: [value not found]"
                        })
                else:
                    # Just mentioning the fact is sufficient
                    correct_facts += 1
            else:
                missing_facts += 1
                errors.append({
                    "type": "missing_fact",
                    "expected": fact,
                    "provided": None
                })
        
        # Check for additional factual errors based on tool outputs
        for tool_id, output in tool_outputs.items():
            additional_errors = self._check_against_tool_output(text, tool_id, output)
            errors.extend(additional_errors)
            incorrect_facts += len(additional_errors)
        
        # Calculate accuracy score
        total_facts = len(expected_facts)
        accuracy_ratio = correct_facts / total_facts if total_facts > 0 else 1.0
        
        if incorrect_facts == 0 and accuracy_ratio >= 0.9:
            accuracy_score = 4.0
            explanation = f"Excellent factual accuracy with {correct_facts}/{total_facts} expected facts correctly stated and no errors"
        elif incorrect_facts <= 1 and accuracy_ratio >= 0.8:
            accuracy_score = 3.0
            explanation = f"Good factual accuracy with {correct_facts}/{total_facts} expected facts correctly stated and minimal errors"
        elif incorrect_facts <= 2 and accuracy_ratio >= 0.6:
            accuracy_score = 2.0
            explanation = f"Adequate factual accuracy with {correct_facts}/{total_facts} expected facts correctly stated"
        elif accuracy_ratio >= 0.4:
            accuracy_score = 1.0
            explanation = f"Poor factual accuracy with only {correct_facts}/{total_facts} expected facts correctly stated"
        else:
            accuracy_score = 0.0
            explanation = f"Very poor factual accuracy with {correct_facts}/{total_facts} expected facts correctly stated and {incorrect_facts} incorrect facts"
        
        return accuracy_score, explanation, errors
    
    def _evaluate_completeness(self, text: str, required_elements: List[str]) -> tuple:
        """
        Evaluate the completeness of text.
        
        Args:
            text: Text to evaluate
            required_elements: List of elements that must be included
            
        Returns:
            Tuple of (score, explanation)
        """
        if not required_elements:
            return 3.0, "No specific elements required in this response"
        
        # Count included required elements
        included_elements = 0
        missing_elements = []
        
        for element in required_elements:
            if self._contains_key_elements(text.lower(), element.lower()):
                included_elements += 1
            else:
                missing_elements.append(element)
        
        # Calculate completeness score
        total_elements = len(required_elements)
        completeness_ratio = included_elements / total_elements if total_elements > 0 else 1.0
        
        if completeness_ratio == 1.0:
            completeness_score = 3.0
            explanation = "Response includes all required elements"
        elif completeness_ratio >= 0.8:
            completeness_score = 2.0
            explanation = f"Response includes most required elements ({included_elements}/{total_elements})"
        elif completeness_ratio >= 0.5:
            completeness_score = 1.0
            explanation = f"Response is missing several required elements (only {included_elements}/{total_elements} included)"
        else:
            completeness_score = 0.0
            explanation = f"Response is highly incomplete with only {included_elements}/{total_elements} required elements"
        
        if missing_elements:
            explanation += f". Missing: {', '.join(missing_elements[:3])}"
            if len(missing_elements) > 3:
                explanation += f" and {len(missing_elements) - 3} more"
        
        return completeness_score, explanation
    
    def _evaluate_relevance(self, text: str, customer_query: str, query_intent: str) -> tuple:
        """
        Evaluate the relevance of text to the customer query.
        
        Args:
            text: Text to evaluate
            customer_query: Customer's original query
            query_intent: Interpreted intent of the query
            
        Returns:
            Tuple of (score, explanation)
        """
        if not customer_query and not query_intent:
            return 2.0, "Relevance could not be evaluated without customer query context"
        
        # Use either actual query or interpreted intent for relevance checking
        reference = customer_query if customer_query else query_intent
        
        # Extract key terms from query/intent
        query_terms = self._extract_key_terms(reference.lower())
        
        # Count how many query terms are addressed in the response
        addressed_terms = sum(1 for term in query_terms if term in text.lower())
        
        # Calculate relevance ratio
        relevance_ratio = addressed_terms / len(query_terms) if query_terms else 1.0
        
        # Check for off-topic content
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        off_topic_sentences = 0
        for sentence in sentences:
            # If a sentence doesn't contain any query terms or their synonyms, it might be off-topic
            if not any(term in sentence.lower() for term in query_terms):
                off_topic_sentences += 1
        
        off_topic_ratio = off_topic_sentences / len(sentences) if sentences else 0
        
        # Calculate relevance score
        if relevance_ratio >= 0.8 and off_topic_ratio <= 0.1:
            relevance_score = 2.0
            explanation = "Response is highly relevant to the customer query"
        elif relevance_ratio >= 0.5 and off_topic_ratio <= 0.3:
            relevance_score = 1.0
            explanation = "Response is mostly relevant to the customer query"
        else:
            relevance_score = 0.0
            explanation = "Response is not sufficiently relevant to the customer query"
        
        return relevance_score, explanation
    
    def _evaluate_consistency(self, text: str, conversation_history: List[Dict[str, Any]], errors: List[Dict[str, Any]]) -> tuple:
        """
        Evaluate the consistency of text with prior conversation.
        
        Args:
            text: Text to evaluate
            conversation_history: Previous turns in the conversation
            errors: List of detected factual errors
            
        Returns:
            Tuple of (score, explanation)
        """
        if not conversation_history or len(conversation_history) <= 1:
            # Not enough history to evaluate consistency
            return 1.0, "No prior conversation to evaluate consistency against"
        
        # Filter for just the assistant's previous responses
        assistant_responses = [turn.get("content", "") for turn in conversation_history 
                               if turn.get("role") == "assistant"]
        
        if not assistant_responses:
            return 1.0, "No prior assistant responses to evaluate consistency against"
        
        # Look for contradictions with previous statements
        contradictions = []
        
        # Simple approach: look for statements that directly contradict previous ones
        statements = re.split(r'[.!?]+', text)
        statements = [s.strip() for s in statements if s.strip()]
        
        for statement in statements:
            # Skip short statements as they're less likely to contain contradictions
            if len(statement.split()) < 5:
                continue
                
            for prev_response in assistant_responses:
                prev_statements = re.split(r'[.!?]+', prev_response)
                prev_statements = [s.strip() for s in prev_statements if s.strip()]
                
                for prev_statement in prev_statements:
                    # Skip short statements
                    if len(prev_statement.split()) < 5:
                        continue
                        
                    # Check for potential contradictions (opposite statements)
                    if self._are_contradictory(statement, prev_statement):
                        contradictions.append({
                            "current": statement,
                            "previous": prev_statement
                        })
        
        # Consider factual errors as consistency issues as well
        consistency_issues = len(contradictions) + min(len(errors), 3)  # Cap influence of errors
        
        # Calculate consistency score
        if consistency_issues == 0:
            consistency_score = 1.0
            explanation = "Response is fully consistent with prior conversation"
        else:
            consistency_score = 0.0
            explanation = f"Response contains {len(contradictions)} contradictions with prior statements"
            if errors:
                explanation += f" and {len(errors)} factual errors"
        
        return consistency_score, explanation
    
    def _contains_key_elements(self, text: str, target: str) -> bool:
        """
        Check if text contains the key elements from target.
        
        Args:
            text: Text to check
            target: Target text with key elements
            
        Returns:
            True if text contains key elements, False otherwise
        """
        # Define semantic synonyms for common business terms
        synonyms = {
            "pricing": ["price", "cost", "costs", "fee", "fees", "rate", "rates", "pricing", "charge"],
            "information": ["info", "details", "data", "information"],
            "timeline": ["timeline", "timeframe", "schedule", "duration", "time", "takes", "timing"],
            "implementation": ["implementation", "setup", "deployment", "installation", "rollout"]
        }
        
        # Extract key elements from target
        key_terms = self._extract_key_terms(target)
        
        # Check if text contains key terms or their synonyms
        matches = 0
        for term in key_terms:
            # Direct match
            if term in text:
                matches += 1
            else:
                # Check synonyms
                term_synonyms = synonyms.get(term, [])
                if any(syn in text for syn in term_synonyms):
                    matches += 1
        
        match_ratio = matches / len(key_terms) if key_terms else 0
        
        return match_ratio >= 0.7  # 70% of key terms (or synonyms) must be present
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text.
        
        Args:
            text: Text to extract terms from
            
        Returns:
            List of key terms
        """
        # Split by spaces and remove common words
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", 
                    "by", "about", "as", "of", "that", "this", "is", "are", "was", "were", "be", 
                    "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", 
                    "shall", "should", "may", "might", "must", "can", "could"}
        
        key_terms = [word for word in words if len(word) > 3 and word not in stopwords]
        
        # Keep only unique terms
        return list(set(key_terms))
    
    def _extract_value_for_key(self, text: str, key: str) -> str:
        """
        Try to extract a value associated with a key in text.
        
        Args:
            text: Text to extract from
            key: Key to look for
            
        Returns:
            Extracted value or None
        """
        # Pattern: key followed by colon, is, are, was, were, etc.
        patterns = [
            rf"{re.escape(key)}:?\s*([^.,;!?]+)",
            rf"{re.escape(key)}\s+is\s+([^.,;!?]+)",
            rf"{re.escape(key)}\s+are\s+([^.,;!?]+)",
            rf"{re.escape(key)}\s+was\s+([^.,;!?]+)",
            rf"{re.escape(key)}\s+were\s+([^.,;!?]+)",
            rf"{re.escape(key)}\s+will be\s+([^.,;!?]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _check_against_tool_output(self, text: str, tool_id: str, output: Any) -> List[Dict[str, Any]]:
        """
        Check response against tool output for factual consistency.
        
        Args:
            text: Text to check
            tool_id: ID of the tool
            output: Tool output data
            
        Returns:
            List of detected errors
        """
        errors = []
        
        # Tool-specific checks
        if tool_id == "scheduler" and isinstance(output, dict):
            # Check if any dates mentioned match available slots
            available_slots = output.get("available_slots", [])
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{2,4}\b'
            dates_in_text = re.findall(date_pattern, text)
            
            for date in dates_in_text:
                if not any(date in slot for slot in available_slots):
                    errors.append({
                        "type": "incorrect_fact",
                        "expected": f"Available appointment dates: {', '.join(available_slots[:3])}...",
                        "provided": f"Mentioned unavailable date: {date}"
                    })
        
        elif tool_id == "pricing_calculator" and isinstance(output, dict):
            # Check if any prices mentioned match calculated prices
            total_price = output.get("total_price", 0)
            price_pattern = r'\$\s*[\d,]+(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|USD)'
            prices_in_text = re.findall(price_pattern, text)
            
            for price_text in prices_in_text:
                # Extract numeric value from price text
                price_value = float(re.sub(r'[^\d.]', '', price_text))
                
                # Allow for some rounding/formatting differences
                if abs(price_value - total_price) > 1.0 and abs(price_value - total_price) / total_price > 0.01:
                    errors.append({
                        "type": "incorrect_fact",
                        "expected": f"Total price: ${total_price:.2f}",
                        "provided": f"Mentioned price: {price_text}"
                    })
        
        return errors
    
    def _are_contradictory(self, statement1: str, statement2: str) -> bool:
        """
        Check if two statements are likely to contradict each other.
        
        Args:
            statement1: First statement
            statement2: Second statement
            
        Returns:
            True if statements appear contradictory, False otherwise
        """
        # Simple approach: look for high similarity but with negation differences
        similarity = difflib.SequenceMatcher(None, statement1.lower(), statement2.lower()).ratio()
        
        # If statements are very similar
        if similarity > 0.6:
            # Check for negation differences
            negations = ["not", "no", "never", "isn't", "aren't", "wasn't", "weren't", 
                        "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't",
                        "won't", "wouldn't", "can't", "cannot", "couldn't", "shouldn't"]
            
            s1_has_negation = any(neg in statement1.lower().split() for neg in negations)
            s2_has_negation = any(neg in statement2.lower().split() for neg in negations)
            
            # If one has negation and the other doesn't, they might be contradictory
            return s1_has_negation != s2_has_negation
        
        return False