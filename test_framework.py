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
    """Mock model client for testing purposes with differentiated behavior."""
    
    def __init__(self, model_name="mock-model", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        self.calls_made = 0
        self.model_personality = self._get_model_personality()
    
    def _get_model_personality(self):
        """Define different personalities/behaviors for different mock models."""
        if "gpt-4" in self.model_name.lower():
            return {
                "style": "detailed",
                "tool_frequency": 0.7,  # Uses tools 70% of the time
                "token_multiplier": 1.2,
                "response_length": "verbose",
                "quality_factor": 0.9  # Higher quality responses
            }
        elif "claude" in self.model_name.lower():
            return {
                "style": "concise",
                "tool_frequency": 0.5,  # Uses tools 50% of the time
                "token_multiplier": 0.8,
                "response_length": "balanced",
                "quality_factor": 0.85
            }
        elif "mistral" in self.model_name.lower():
            return {
                "style": "technical",
                "tool_frequency": 0.3,  # Uses tools 30% of the time
                "token_multiplier": 0.6,
                "response_length": "brief",
                "quality_factor": 0.75
            }
        else:
            return {
                "style": "generic",
                "tool_frequency": 0.4,
                "token_multiplier": 1.0,
                "response_length": "balanced",
                "quality_factor": 0.8
            }
    
    def generate_response(self, messages, tools=None):
        """Generate a mock response with model-specific characteristics."""
        self.calls_made += 1
        
        # Get last message for context
        last_message = messages[-1]["content"] if messages else ""
        personality = self.model_personality
        
        # Generate response based on model personality and accuracy
        if personality["style"] == "detailed":
            # GPT-4 style: Detailed but sometimes includes incorrect facts to test accuracy scoring
            if self.calls_made == 1:
                content = f"Thank you for your detailed inquiry about DataInsight Enterprise. This is a comprehensive business intelligence platform designed for financial services. The typical implementation timeline is 8-10 weeks (incorrect - should be 10-12), and our base pricing starts at $1500 per user per month (incorrect - should be $1200). Let me provide you with detailed information about our key features including real-time analytics, automated reporting, and regulatory compliance tools."
            else:
                content = f"I'll provide comprehensive follow-up information. Based on your specific requirements, I recommend scheduling a detailed consultation to discuss implementation phases, training requirements, and ongoing support options. Our enterprise solution includes 24/7 technical support and dedicated account management."
        elif personality["style"] == "concise":
            # Claude style: Accurate but sometimes missing required elements
            if self.calls_made == 1:
                content = f"I'll help with your DataInsight Enterprise inquiry. Our solution offers real-time analytics and automated reporting capabilities. The implementation typically takes 10-12 weeks with base pricing at $1200 per user monthly. Would you like me to check specific pricing for your organization size?"
            else:
                content = f"I can provide additional details about features and implementation phases. Our support team is available to schedule a consultation call."
        elif personality["style"] == "technical":
            # Mistral style: Brief but highly accurate technical details
            if self.calls_made == 1:
                content = f"DataInsight Enterprise specifications: Core platform supports real-time data processing, automated report generation, regulatory compliance modules. Implementation timeline: 10-12 weeks standard deployment. Pricing model: per-user subscription at $1200 base rate. Technical requirements and integration capabilities available upon request."
            else:
                content = f"Technical implementation details: Phase-based deployment methodology, API integration support, cloud-native architecture. Support includes technical documentation and integration assistance."
        else:
            content = f"Regarding '{last_message[:30]}...', I can assist you with this request."
        
        response = {"content": content}
        
        # Add tool calls based on model's tool usage frequency
        import random
        if tools and random.random() < personality["tool_frequency"]:
            # Choose tools more strategically based on the conversation turn
            if self.calls_made == 1:
                tool_options = ["product_catalog", "pricing_calculator"]
            else:
                tool_options = ["knowledge_base", "customer_history", "scheduler"]
            
            selected_tool = random.choice(tool_options)
            
            response["tool_calls"] = [
                {
                    "id": f"call_{self.calls_made}_{self.model_name}",
                    "function": {
                        "name": selected_tool,
                        "arguments": '{"query": "DataInsight Enterprise details"}' if selected_tool in ["product_catalog", "knowledge_base"] else '{"customer_size": "enterprise"}'
                    }
                }
            ]
        
        return response
    
    def get_usage_stats(self):
        """Get usage statistics with model-specific variations."""
        personality = self.model_personality
        base_tokens = self.calls_made * 80
        
        # Apply model-specific token multipliers
        total_tokens = int(base_tokens * personality["token_multiplier"])
        prompt_tokens = int(total_tokens * 0.6)
        completion_tokens = total_tokens - prompt_tokens
        
        return {
            "model_name": self.model_name,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_calls": self.calls_made,
            "avg_tokens_per_call": total_tokens / max(self.calls_made, 1),
            "tool_usage_rate": personality["tool_frequency"]
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.calls_made = 0
    
    def get_token_count(self, text):
        """Get token count for text with model-specific calculations."""
        base_count = len(text.split()) * 1.3
        return int(base_count * self.model_personality["token_multiplier"])


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
            MockModelClient("mock-claude-3"),
            MockModelClient("mock-mistral-large")
        ]
        print(f"✓ Created {len(models)} mock models successfully")
        for model in models:
            personality = model.model_personality
            print(f"  - {model.model_name} (style: {personality['style']}, tool_freq: {personality['tool_frequency']})")
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
        
        # Print summary with detailed stats
        print("\n  Summary scores:")
        for model_id, score in results["summary"]["overall_scores"].items():
            print(f"    {model_id}: {score:.2f}/10")
        
        # Show model usage stats to demonstrate differences
        print("\n  Model usage statistics:")
        for model in models:
            stats = model.get_usage_stats()
            print(f"    {stats['model_name']}:")
            print(f"      - Total tokens: {stats['total_tokens']}")
            print(f"      - Calls made: {stats['total_calls']}")
            print(f"      - Avg tokens/call: {stats['avg_tokens_per_call']:.1f}")
            print(f"      - Tool usage rate: {stats['tool_usage_rate']:.0%}")
        
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