#!/usr/bin/env python3
"""
Test script to validate the bizCon framework functionality.
This script creates a mock scenario run to test the pipeline without API keys.
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.base import ModelClient
from scenarios import load_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools
from core.pipeline import EvaluationPipeline


class MockModelClient(ModelClient):
    """Mock model client for testing purposes."""
    
    def __init__(self, model_name="mock-model", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        self.calls_made = 0
    
    def generate_response(self, messages, tools=None):
        """Generate a mock response."""
        self.calls_made += 1
        
        # Simple mock response based on conversation
        last_message = messages[-1]["content"] if messages else ""
        
        response = {
            "content": f"Thank you for your inquiry. I'll help you with that. Based on your request about '{last_message[:50]}...', let me provide you with relevant information."
        }
        
        # Sometimes include mock tool calls
        if tools and self.calls_made % 2 == 0:
            response["tool_calls"] = [
                {
                    "id": f"call_{self.calls_made}",
                    "function": {
                        "name": "knowledge_base",
                        "arguments": '{"query": "test query"}'
                    }
                }
            ]
        
        return response
    
    def get_usage_stats(self):
        """Get usage statistics."""
        return {
            "model_name": self.model_name,
            "total_tokens": self.calls_made * 100,
            "prompt_tokens": self.calls_made * 60,
            "completion_tokens": self.calls_made * 40,
            "total_calls": self.calls_made
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.calls_made = 0
    
    def get_token_count(self, text):
        """Get token count for text (mock implementation)."""
        return len(text.split()) * 1.3  # Rough approximation


def test_framework():
    """Test the framework with mock data."""
    print("Testing bizCon Framework...")
    
    # Test 1: Load scenarios
    print("\n1. Loading scenarios...")
    try:
        scenarios = load_scenarios(["product_inquiry_001", "support_001"])
        print(f"✓ Loaded {len(scenarios)} scenarios successfully")
        for scenario in scenarios:
            print(f"  - {scenario.scenario_id}: {scenario.name}")
    except Exception as e:
        print(f"✗ Failed to load scenarios: {e}")
        return False
    
    # Test 2: Load evaluators
    print("\n2. Loading evaluators...")
    try:
        evaluators = get_all_evaluators()
        print(f"✓ Loaded {len(evaluators)} evaluators successfully")
        for evaluator in evaluators:
            print(f"  - {evaluator.name} (weight: {evaluator.weight})")
    except Exception as e:
        print(f"✗ Failed to load evaluators: {e}")
        return False
    
    # Test 3: Load tools
    print("\n3. Loading tools...")
    try:
        tools = get_default_tools()
        print(f"✓ Loaded {len(tools)} tools successfully")
        for tool_id, tool in tools.items():
            print(f"  - {tool_id}: {tool.__class__.__name__}")
    except Exception as e:
        print(f"✗ Failed to load tools: {e}")
        return False
    
    # Test 4: Create mock models
    print("\n4. Creating mock models...")
    try:
        models = [
            MockModelClient("mock-gpt-4"),
            MockModelClient("mock-claude-3")
        ]
        print(f"✓ Created {len(models)} mock models successfully")
        for model in models:
            print(f"  - {model.model_name}")
    except Exception as e:
        print(f"✗ Failed to create mock models: {e}")
        return False
    
    # Test 5: Run pipeline
    print("\n5. Running evaluation pipeline...")
    try:
        pipeline = EvaluationPipeline(
            models=models,
            scenarios=scenarios[:1],  # Just one scenario for testing
            evaluators=evaluators,
            tools=tools,
            num_runs=1,
            parallel=False,
            verbose=True
        )
        
        results = pipeline.run()
        print(f"✓ Pipeline completed successfully")
        print(f"  - Models evaluated: {len(results['models'])}")
        print(f"  - Scenarios tested: {len(results['scenarios'])}")
        print(f"  - Total duration: {results['duration']:.2f} seconds")
        
        # Print summary
        print("\n  Summary scores:")
        for model_id, score in results["summary"]["overall_scores"].items():
            print(f"    {model_id}: {score:.2f}/10")
        
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Save results
    print("\n6. Saving results...")
    try:
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save raw results
        results_file = os.path.join(output_dir, "test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Results saved to {results_file}")
        
        # Generate report
        pipeline.generate_report(output_dir)
        print(f"✓ Report generated in {output_dir}")
        
    except Exception as e:
        print(f"✗ Failed to save results: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All tests passed! The bizCon framework is working correctly.")
    print(f"\nTest results saved in: {os.path.abspath(output_dir)}")
    return True


if __name__ == "__main__":
    success = test_framework()
    sys.exit(0 if success else 1)