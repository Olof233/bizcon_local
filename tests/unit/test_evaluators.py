#!/usr/bin/env python3
"""
Unit tests for evaluator components.
"""
import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from evaluators.base import BaseEvaluator
from evaluators.response_quality import ResponseQualityEvaluator
from evaluators.communication_style import CommunicationStyleEvaluator
from evaluators.tool_usage import ToolUsageEvaluator
from evaluators.business_value import BusinessValueEvaluator
from evaluators.performance import PerformanceEvaluator


class MockScenario:
    """Mock scenario for testing evaluators."""
    
    def __init__(self):
        self.scenario_id = "test_scenario"
        self.name = "Test Scenario"
    
    def get_ground_truth(self, turn_index=0):
        """Return mock ground truth data."""
        return {
            "expected_facts": [
                "Product DataInsight costs $1000 per month",
                "Implementation takes 3-4 weeks"
            ],
            "required_elements": [
                "pricing information",
                "implementation timeline"
            ],
            "expected_tone": "professional",
            "expected_formality": "formal",
            "communication_guidelines": [
                "Use clear language",
                "Provide specific details"
            ],
            "expected_tool_calls": [
                {
                    "tool_id": "product_catalog",
                    "parameters": {
                        "product_id": "data_analytics_enterprise"
                    }
                }
            ],
            "expected_business_outcomes": [
                "Provide accurate information",
                "Demonstrate product expertise"
            ]
        }
    
    def get_context(self):
        """Return mock context data."""
        return {
            "customer_type": "enterprise",
            "industry": "finance",
            "scenario_type": "product_inquiry"
        }


class TestBaseEvaluator(unittest.TestCase):
    """Test the base evaluator functionality."""
    
    def test_normalize_score(self):
        """Test score normalization."""
        class TestEvaluator(BaseEvaluator):
            def evaluate(self, *args, **kwargs):
                pass
        
        evaluator = TestEvaluator(name="Test", weight=0.5)
        
        # Test normal values
        self.assertEqual(evaluator.normalize_score(5.0), 5.0)
        
        # Test below minimum
        self.assertEqual(evaluator.normalize_score(-1.0), 0.0)
        
        # Test above maximum
        self.assertEqual(evaluator.normalize_score(11.0), 10.0)


class TestResponseQualityEvaluator(unittest.TestCase):
    """Test the response quality evaluator."""
    
    def setUp(self):
        self.evaluator = ResponseQualityEvaluator(weight=1.0)
        self.scenario = MockScenario()
        self.conversation_history = [
            {"role": "user", "content": "Tell me about your DataInsight product pricing and implementation."}
        ]
    
    def test_good_response(self):
        """Test evaluation of a good response."""
        response = {
            "content": "DataInsight Enterprise costs $1000 per month for the standard package. " +
                      "Implementation typically takes 3-4 weeks, including setup, data migration, and training."
        }
        
        result = self.evaluator.evaluate(
            response=response,
            scenario=self.scenario,
            turn_index=0,
            conversation_history=self.conversation_history,
            tool_calls=[]
        )
        
        # Check that the score is high (above 7 out of 10)
        self.assertGreater(result.get("score", 0), 7.0)
    
    def test_incomplete_response(self):
        """Test evaluation of an incomplete response."""
        response = {
            "content": "DataInsight is our enterprise analytics solution. " +
                      "It offers real-time data processing and visualization."
        }
        
        result = self.evaluator.evaluate(
            response=response,
            scenario=self.scenario,
            turn_index=0,
            conversation_history=self.conversation_history,
            tool_calls=[]
        )
        
        # Check that the score is medium-low (below 5 out of 10)
        self.assertLess(result.get("score", 10), 5.0)


class TestCommunicationStyleEvaluator(unittest.TestCase):
    """Test the communication style evaluator."""
    
    def setUp(self):
        self.evaluator = CommunicationStyleEvaluator(weight=1.0)
        self.scenario = MockScenario()
        self.conversation_history = [
            {"role": "user", "content": "Tell me about your DataInsight product pricing and implementation."}
        ]
    
    def test_professional_response(self):
        """Test evaluation of a professionally styled response."""
        response = {
            "content": "Thank you for your interest in DataInsight Enterprise. " +
                      "Our standard package is priced at $1,000 per month with annual billing options available. " +
                      "The implementation process typically takes 3-4 weeks, during which our team will guide you " +
                      "through setup, data migration, and provide comprehensive training for your team."
        }
        
        result = self.evaluator.evaluate(
            response=response,
            scenario=self.scenario,
            turn_index=0,
            conversation_history=self.conversation_history,
            tool_calls=[]
        )
        
        # Check that the score is high (above 8 out of 10)
        self.assertGreater(result.get("score", 0), 8.0)
    
    def test_inappropriate_response(self):
        """Test evaluation of an inappropriately styled response."""
        response = {
            "content": "yo! DataInsight is gonna cost ya $1000/month lol. " +
                      "setup takes like 3-4 weeks or whatever. hit us up if u want it!"
        }
        
        result = self.evaluator.evaluate(
            response=response,
            scenario=self.scenario,
            turn_index=0,
            conversation_history=self.conversation_history,
            tool_calls=[]
        )
        
        # Check that the score is low (below 4 out of 10)
        self.assertLess(result.get("score", 10), 4.0)


if __name__ == '__main__':
    unittest.main()