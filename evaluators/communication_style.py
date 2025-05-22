"""
Communication style evaluator for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import re
import json

from .base import BaseEvaluator


class CommunicationStyleEvaluator(BaseEvaluator):
    """
    Evaluator for assessing communication style of model responses.
    
    Measures professionalism, clarity, tone appropriateness, and adaptability
    to the business context and customer expectations.
    """
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the communication style evaluator.
        
        Args:
            weight: Weight of this evaluator in the overall score (0-1)
        """
        super().__init__(name="Communication Style", weight=weight)
    
    def evaluate(self, 
                response: Dict[str, Any], 
                scenario: Any, 
                turn_index: int,
                conversation_history: List[Dict[str, Any]],
                tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the communication style of a model response.
        
        Scoring criteria:
        - Professionalism (0-3 points)
        - Clarity and conciseness (0-2 points)
        - Tone appropriateness (0-3 points)
        - Adaptability to context (0-2 points)
        
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
        
        # Get expected communication style from scenario's ground truth
        ground_truth = scenario.get_ground_truth()
        expected_tone = ground_truth.get("expected_tone", "professional")
        expected_formality = ground_truth.get("expected_formality", "formal")
        communication_guidelines = ground_truth.get("communication_guidelines", [])
        
        # Get scenario context
        context = scenario.get_context()
        customer_type = context.get("customer_type", "enterprise")
        industry = context.get("industry", "general")
        
        # Initialize scores and explanations
        professionalism_score = 0.0
        professionalism_explanation = ""
        
        clarity_score = 0.0
        clarity_explanation = ""
        
        tone_score = 0.0
        tone_explanation = ""
        
        adaptability_score = 0.0
        adaptability_explanation = ""
        
        # 1. Evaluate professionalism
        professionalism_score, professionalism_explanation = self._evaluate_professionalism(
            response_text, 
            expected_formality
        )
        
        # 2. Evaluate clarity and conciseness
        clarity_score, clarity_explanation = self._evaluate_clarity(response_text)
        
        # 3. Evaluate tone appropriateness
        tone_score, tone_explanation = self._evaluate_tone(
            response_text, 
            expected_tone, 
            customer_type,
            industry
        )
        
        # 4. Evaluate adaptability to context
        adaptability_score, adaptability_explanation = self._evaluate_adaptability(
            response_text,
            conversation_history,
            communication_guidelines
        )
        
        # Calculate total score
        total_score = professionalism_score + clarity_score + tone_score + adaptability_score
        
        # Normalize to 0-10 scale
        normalized_score = self.normalize_score(total_score)
        
        return {
            "score": normalized_score,
            "breakdown": {
                "professionalism_score": professionalism_score,
                "clarity_score": clarity_score,
                "tone_score": tone_score,
                "adaptability_score": adaptability_score
            },
            "explanation": {
                "professionalism": professionalism_explanation,
                "clarity": clarity_explanation,
                "tone": tone_explanation,
                "adaptability": adaptability_explanation
            },
            "max_possible": 10.0
        }
    
    def _evaluate_professionalism(self, text: str, expected_formality: str) -> tuple:
        """
        Evaluate the professionalism of text.
        
        Args:
            text: Text to evaluate
            expected_formality: Expected formality level
            
        Returns:
            Tuple of (score, explanation)
        """
        # Check for unprofessional language
        unprofessional_terms = [
            "hey there", "yo", "what's up", "kinda", "sorta", "gonna", "wanna", 
            "dunno", "ya know", "like", "basically", "stuff", "things", "ok", "k"
        ]
        
        # Check for unprofessional terms with word boundaries
        unprofessional_count = 0
        for term in unprofessional_terms:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text.lower()):
                unprofessional_count += 1
        
        # Check for excessive informality if formal is expected
        if expected_formality == "formal":
            excessive_contractions = len(re.findall(r"\b(can't|won't|don't|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|didn't|wouldn't|couldn't|shouldn't)\b", text.lower()))
            excessive_informality = unprofessional_count > 0 or excessive_contractions > 3
        else:
            excessive_informality = unprofessional_count > 2
            
        # Check for proper business language
        business_language_indicators = [
            "thank you", "please", "appreciate", "value", "assist", "help", 
            "provide", "information", "understand", "solution", "service",
            "available", "options", "process", "team", "comprehensive", "training",
            "support", "package", "implementation", "guide", "interest"
        ]
        
        # Check for business language indicators with word boundaries
        business_language_count = 0
        for term in business_language_indicators:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text.lower()):
                business_language_count += 1
        
        # Calculate professionalism score
        if unprofessional_count == 0 and business_language_count >= 3:
            professionalism_score = 3.0
            explanation = "Response demonstrates excellent professionalism with appropriate business language"
        elif unprofessional_count == 0 and business_language_count >= 1:
            professionalism_score = 2.0
            explanation = "Response demonstrates good professionalism"
        elif unprofessional_count <= 1 and business_language_count >= 1:
            professionalism_score = 1.0
            explanation = "Response demonstrates adequate professionalism with minor issues"
        else:
            professionalism_score = 0.0
            explanation = "Response lacks professionalism with inappropriate language or tone"
            
        return professionalism_score, explanation
    
    def _evaluate_clarity(self, text: str) -> tuple:
        """
        Evaluate the clarity and conciseness of text.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Tuple of (score, explanation)
        """
        # Calculate average sentence length
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0, "Could not evaluate clarity due to parsing issues"
        
        avg_sentence_length = sum(len(re.findall(r'\b\w+\b', s)) for s in sentences) / len(sentences)
        
        # Check for complex language
        complex_words = re.findall(r'\b\w{12,}\b', text)
        complex_word_ratio = len(complex_words) / len(re.findall(r'\b\w+\b', text)) if re.findall(r'\b\w+\b', text) else 0
        
        # Check for structure indicators
        has_structure = any(indicator in text.lower() for indicator in ["first", "second", "finally", "in summary", "to summarize", "in conclusion"])
        
        # Calculate clarity score
        if 10 <= avg_sentence_length <= 20 and complex_word_ratio < 0.05:
            clarity_score = 2.0
            explanation = "Response is exceptionally clear, concise, and well-structured"
        elif 8 <= avg_sentence_length <= 30 and complex_word_ratio < 0.15:
            clarity_score = 1.5
            explanation = "Response is clear and well-structured"
        elif avg_sentence_length <= 35 and complex_word_ratio < 0.2:
            clarity_score = 1.0
            explanation = "Response is adequately clear and reasonably concise"
        else:
            clarity_score = 0.0
            explanation = "Response lacks clarity with overly complex or too brief language"
            
        return clarity_score, explanation
    
    def _evaluate_tone(self, text: str, expected_tone: str, customer_type: str, industry: str) -> tuple:
        """
        Evaluate the tone appropriateness of text.
        
        Args:
            text: Text to evaluate
            expected_tone: Expected tone
            customer_type: Type of customer
            industry: Industry context
            
        Returns:
            Tuple of (score, explanation)
        """
        # Define tone indicators
        tone_indicators = {
            "professional": ["would like to", "we recommend", "suggest", "advise", "please consider", 
                           "our team", "we provide", "available", "standard", "typically", 
                           "during which", "through", "for your", "our"],
            "friendly": ["happy to", "glad to", "look forward to", "excited", "wonderful"],
            "formal": ["we regret to inform", "please be advised", "kindly note", "we request", "formally"],
            "empathetic": ["understand", "appreciate", "recognize", "know that", "hear your concern"],
            "direct": ["need to", "must", "should", "require", "necessary"]
        }
        
        # Check for presence of expected tone
        expected_tone_count = 0
        if expected_tone in tone_indicators:
            expected_tone_count = sum(1 for term in tone_indicators[expected_tone] if term in text.lower())
        
        # Check for inappropriate tone based on customer type and industry
        inappropriate_tone = False
        
        if customer_type == "enterprise" and any(term in text.lower() for term in tone_indicators["friendly"]):
            inappropriate_tone = True
            
        if industry == "financial" and not any(term in text.lower() for term in tone_indicators["formal"]):
            inappropriate_tone = True
            
        if industry == "healthcare" and not any(term in text.lower() for term in tone_indicators["empathetic"]):
            inappropriate_tone = True
        
        # Calculate tone score
        if expected_tone_count >= 2 and not inappropriate_tone:
            tone_score = 3.0
            explanation = f"Response perfectly matches the expected {expected_tone} tone for this context"
        elif expected_tone_count >= 1 and not inappropriate_tone:
            tone_score = 2.0
            explanation = f"Response generally maintains an appropriate {expected_tone} tone"
        elif not inappropriate_tone:
            tone_score = 1.0
            explanation = "Response maintains neutral tone appropriate for business"
        else:
            tone_score = 0.0
            explanation = f"Response uses inappropriate tone for {customer_type} customer in {industry} industry"
            
        return tone_score, explanation
    
    def _evaluate_adaptability(self, text: str, conversation_history: List[Dict[str, Any]], guidelines: List[str]) -> tuple:
        """
        Evaluate the adaptability to context.
        
        Args:
            text: Text to evaluate
            conversation_history: Previous turns in the conversation
            guidelines: Communication guidelines
            
        Returns:
            Tuple of (score, explanation)
        """
        # Check if any previous customer messages exist
        customer_messages = [turn for turn in conversation_history if turn.get("role") == "user"]
        
        if not customer_messages:
            # No history to adapt to
            guidelines_followed = sum(1 for guideline in guidelines if self._guideline_followed(text, guideline))
            guideline_ratio = guidelines_followed / len(guidelines) if guidelines else 1.0
            
            if guideline_ratio >= 0.8:
                return 2.0, "Response follows communication guidelines perfectly"
            elif guideline_ratio >= 0.5:
                return 1.5, "Response follows most communication guidelines"
            elif guideline_ratio >= 0.3:
                return 1.0, "Response follows some communication guidelines"
            else:
                return 0.0, "Response does not follow communication guidelines"
        
        # Check if response adapts to customer's language and concerns
        last_customer_message = customer_messages[-1].get("content", "")
        
        # Extract key terms from customer's message
        customer_terms = set(re.findall(r'\b\w{4,}\b', last_customer_message.lower()))
        
        # Check if response incorporates customer's language
        response_terms = set(re.findall(r'\b\w{4,}\b', text.lower()))
        shared_terms = customer_terms.intersection(response_terms)
        
        adaptation_ratio = len(shared_terms) / len(customer_terms) if customer_terms else 0
        
        # Check if guidelines are followed
        guidelines_followed = sum(1 for guideline in guidelines if self._guideline_followed(text, guideline))
        guideline_ratio = guidelines_followed / len(guidelines) if guidelines else 1.0
        
        # Calculate adaptability score
        if adaptation_ratio >= 0.3 and guideline_ratio >= 0.8:
            adaptability_score = 2.0
            explanation = "Response excellently adapts to customer's language and follows guidelines"
        elif adaptation_ratio >= 0.2 and guideline_ratio >= 0.5:
            adaptability_score = 1.5
            explanation = "Response adapts well to context and follows guidelines"
        elif adaptation_ratio >= 0.1 or guideline_ratio >= 0.5:
            adaptability_score = 1.0
            explanation = "Response shows some adaptation to context"
        else:
            adaptability_score = 0.0
            explanation = "Response fails to adapt to conversation context"
            
        return adaptability_score, explanation
    
    def _guideline_followed(self, text: str, guideline: str) -> bool:
        """
        Check if a specific communication guideline is followed.
        
        Args:
            text: Text to check
            guideline: Guideline to check for
            
        Returns:
            True if guideline is followed, False otherwise
        """
        # Extract key elements from guideline
        key_terms = set(re.findall(r'\b\w{4,}\b', guideline.lower()))
        
        # Determine guideline type
        if "avoid" in guideline.lower() or "don't" in guideline.lower() or "do not" in guideline.lower():
            # This is a negative guideline (avoid certain language)
            negative_terms = [term for term in key_terms if term not in {"avoid", "dont", "should"}]
            
            # Check if negative terms are absent
            for term in negative_terms:
                if term in text.lower():
                    return False
            return True
        else:
            # This is a positive guideline (use certain language)
            # Consider guideline followed if at least 30% of key terms are present
            text_terms = set(re.findall(r'\b\w{4,}\b', text.lower()))
            shared_terms = key_terms.intersection(text_terms)
            
            return len(shared_terms) / len(key_terms) >= 0.3 if key_terms else True