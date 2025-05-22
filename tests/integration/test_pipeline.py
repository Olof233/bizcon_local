#!/usr/bin/env python3
"""
Integration tests for the evaluation pipeline.
"""
import unittest
import sys
import os
import json
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.pipeline import EvaluationPipeline
from scenarios.base import BusinessScenario
from models.base import ModelClient


class MockModel(ModelClient):
    """Mock model for testing the pipeline."""
    
    def __init__(self, model_name="mock-model", responses=None):
        super().__init__(model_name=model_name)
        self.responses = responses or {}
        self.call_history = []
    
    def generate_response(self, messages, tools=None):
        """Generate a mocked response."""
        user_message = next((m["content"] for m in reversed(messages) 
                            if m.get("role") == "user"), "")
        
        # Record the call
        self.call_history.append({
            "messages": messages,
            "tools": tools
        })
        
        # Find matching response or return default
        if user_message in self.responses:
            return self.responses[user_message]
        
        # Default response with tool calls if tools are provided
        if tools:
            tool_id = tools[0]["function"]["name"]
            return {
                "content": "I'll help you with that. Let me check our systems.",
                "tool_calls": [
                    {
                        "id": "call_01",
                        "type": "function",
                        "function": {
                            "name": tool_id,
                            "arguments": "{}"
                        }
                    }
                ]
            }
        
        return {"content": "This is a mock response."}
    
    def get_token_count(self, text):
        """Mock token counting."""
        if not text:
            return 0
        return len(text) // 4  # Rough approximation


class MockScenario(BusinessScenario):
    """Mock scenario for testing the pipeline."""
    
    def __init__(self, scenario_id="mock_scenario", name="Mock Scenario"):
        super().__init__(
            scenario_id=scenario_id,
            name=name,
            description="A mock scenario for testing",
            industry="general",
            complexity="simple",
            tools_required=["knowledge_base"]
        )
    
    def _initialize_conversation(self):
        """Initialize the conversation flow."""
        return [
            {
                "user_message": "Tell me about your product features.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "product features"
                        }
                    }
                ]
            },
            {
                "user_message": "What about pricing?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "pricing"
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self):
        """Initialize ground truth information."""
        return {
            "expected_facts": [
                "Our product has advanced analytics features",
                "It supports integration with common platforms"
            ],
            "required_elements": [
                "Feature details",
                "Integration capabilities"
            ],
            "expected_tone": "professional",
            "expected_formality": "formal",
            "expected_tool_calls": [
                {
                    "tool_id": "knowledge_base",
                    "parameters": {
                        "query": "product features"
                    }
                }
            ],
            "expected_business_outcomes": [
                "Provide accurate information",
                "Build customer confidence"
            ]
        }


class MockTool:
    """Mock business tool for testing."""
    
    def __init__(self, tool_id, response=None):
        self.tool_id = tool_id
        self.response = response or {"status": "success", "result": "This is a mock result"}
        self.call_count = 0
        self.error_count = 0
    
    def get_definition(self):
        """Get the tool definition."""
        return {
            "type": "function",
            "function": {
                "name": self.tool_id,
                "description": f"Mock {self.tool_id} tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query string"
                        }
                    }
                }
            }
        }
    
    def call(self, parameters):
        """Call the mock tool."""
        self.call_count += 1
        return self.response
    
    def get_usage_stats(self):
        """Get usage statistics."""
        return {
            "tool_id": self.tool_id,
            "calls": self.call_count,
            "errors": self.error_count,
            "success_rate": 1.0
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.call_count = 0
        self.error_count = 0


class TestEvaluationPipeline(unittest.TestCase):
    """Test the evaluation pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.model_a = MockModel(model_name="model-a", responses={
            "Tell me about your product features.": {
                "content": "Our product has advanced analytics with real-time dashboards and API integrations."
            },
            "What about pricing?": {
                "content": "The product costs $1000/month for the enterprise tier."
            }
        })
        
        self.model_b = MockModel(model_name="model-b", responses={
            "Tell me about your product features.": {
                "content": "The product does stuff. It's pretty good."
            },
            "What about pricing?": {
                "content": "It costs money."
            }
        })
        
        # Create mock scenarios
        self.scenario_1 = MockScenario(scenario_id="mock_001", name="Mock Scenario 1")
        self.scenario_2 = MockScenario(scenario_id="mock_002", name="Mock Scenario 2")
        
        # Create mock tools
        self.mock_tools = {
            "knowledge_base": MockTool("knowledge_base", {
                "status": "success",
                "result": [
                    {"question": "What features does your product have?", 
                     "answer": "Our product includes advanced analytics, real-time dashboards, and API integrations."}
                ]
            })
        }
    
    def test_pipeline_execution(self):
        """Test that the pipeline executes successfully."""
        # Create the pipeline
        pipeline = EvaluationPipeline(
            models=[self.model_a, self.model_b],
            scenarios=[self.scenario_1],
            tools=self.mock_tools,
            num_runs=1,
            parallel=False,
            verbose=False
        )
        
        # Run the pipeline
        results = pipeline.run()
        
        # Check that results were generated
        self.assertIsNotNone(results)
        self.assertIn("summary", results)
        self.assertIn("results", results)
        
        # Check that both models were evaluated
        self.assertIn("model-a", results["summary"]["overall_scores"])
        self.assertIn("model-b", results["summary"]["overall_scores"])
        
        # Verify model A scored higher than model B (since it gives better responses)
        self.assertGreater(
            results["summary"]["overall_scores"]["model-a"],
            results["summary"]["overall_scores"]["model-b"]
        )
        
        # Check that the tool was called
        self.assertGreaterEqual(self.mock_tools["knowledge_base"].call_count, 1)


if __name__ == '__main__':
    unittest.main()