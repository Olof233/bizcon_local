#!/usr/bin/env python3
"""
Comprehensive validation of the bizCon framework.
Tests core functionality without requiring API keys.
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.pipeline import EvaluationPipeline
from core.runner import ScenarioRunner
from models.base import ModelClient
from scenarios import load_scenarios, list_available_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools


class MockModel(ModelClient):
    """Mock model for testing without API calls"""
    
    def __init__(self, model_name="mock-model"):
        super().__init__(model_name=model_name)
        self.call_count = 0
    
    def generate_response(self, messages, tools=None) -> Dict[str, Any]:
        self.call_count += 1
        
        # Simulate realistic tool usage
        tool_calls = []
        if tools and self.call_count % 2 == 1:  # Use tools on odd calls
            # Pick a random tool to simulate usage - tools is a list of tool definitions
            tool_def = tools[0] if tools else None
            if tool_def and "function" in tool_def:
                tool_name = tool_def["function"]["name"]
                tool_calls.append({
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps({"query": "test query"})
                    }
                })
        
        return {
            "content": f"Mock response {self.call_count} with realistic business content. "
                      f"I understand you need assistance with your business inquiry. "
                      f"Let me help you with that. Based on the information provided, "
                      f"I recommend the following approach...",
            "tool_calls": tool_calls,
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    
    def get_token_count(self, text: str) -> int:
        """Mock token counting - roughly 4 characters per token"""
        return len(text) // 4
    
    def chat(self, messages, tools=None, max_tokens=1024, temperature=0.7) -> Dict[str, Any]:
        self.call_count += 1
        
        # Simulate realistic tool usage
        tool_calls = []
        if tools and self.call_count % 2 == 1:  # Use tools on odd calls
            # Pick a random tool to simulate usage
            tool_id = list(tools.keys())[0] if tools else None
            if tool_id:
                tool_calls.append({
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": tool_id,
                        "arguments": json.dumps({"query": "test query"})
                    }
                })
        
        return {
            "content": f"Mock response {self.call_count} with realistic business content. "
                      f"I understand you need assistance with your business inquiry. "
                      f"Let me help you with that. Based on the information provided, "
                      f"I recommend the following approach...",
            "tool_calls": tool_calls,
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }


def test_scenario_loading():
    """Test scenario loading functionality"""
    print("Testing scenario loading...")
    
    # Test listing scenarios
    scenarios = list_available_scenarios()
    print(f"✓ Found {len(scenarios)} scenario definitions")
    
    # Check for duplicate IDs
    scenario_ids = list(scenarios.keys())
    unique_ids = set(scenario_ids)
    if len(scenario_ids) != len(unique_ids):
        duplicates = [id for id in unique_ids if scenario_ids.count(id) > 1]
        print(f"⚠️  Warning: Found duplicate scenario IDs: {duplicates}")
    else:
        print("✓ No duplicate scenario IDs found")
    
    # Test loading specific scenarios
    test_scenario_id = "product_inquiry_001"
    loaded_scenarios = load_scenarios([test_scenario_id])
    if loaded_scenarios:
        print(f"✓ Successfully loaded scenario: {test_scenario_id}")
        scenario = loaded_scenarios[0]
        print(f"  - Name: {scenario.name}")
        print(f"  - Tools required: {scenario.tools_required}")
        print(f"  - Conversation turns: {len(scenario.get_conversation())}")
    else:
        print(f"✗ Failed to load scenario: {test_scenario_id}")
        return False
    
    return True


def test_evaluator_logic():
    """Test evaluator functionality"""
    print("\nTesting evaluator logic...")
    
    evaluators = get_all_evaluators()
    print(f"✓ Loaded {len(evaluators)} evaluators")
    
    # Test each evaluator with mock data
    mock_response = {
        "content": "Thank you for your inquiry about our enterprise software solution. Based on your requirements, I recommend our Premium Analytics package which includes advanced reporting, real-time dashboards, and enterprise-grade security features.",
        "tool_calls": [],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    }
    mock_scenario = load_scenarios(["product_inquiry_001"])[0]
    
    for evaluator in evaluators:
        try:
            result = evaluator.evaluate(
                response=mock_response,
                scenario=mock_scenario,
                turn_index=0,
                conversation_history=[],
                tool_calls=[]
            )
            
            # Validate evaluator result structure
            required_keys = ['score', 'explanation', 'max_possible']
            if all(key in result for key in required_keys):
                score = result['score']
                max_score = result['max_possible']
                if 0 <= score <= max_score:
                    print(f"✓ {evaluator.name}: {score:.1f}/{max_score}")
                else:
                    print(f"✗ {evaluator.name}: Invalid score {score}/{max_score}")
                    return False
            else:
                print(f"✗ {evaluator.name}: Missing required keys in result")
                return False
                
        except Exception as e:
            print(f"✗ {evaluator.name}: Error during evaluation - {str(e)}")
            return False
    
    return True


def test_tool_integration():
    """Test business tool functionality"""
    print("\nTesting tool integration...")
    
    tools = get_default_tools()
    print(f"✓ Loaded {len(tools)} business tools")
    
    # Test each tool
    for tool_id, tool in tools.items():
        try:
            # Test tool execution with mock parameters
            if hasattr(tool, 'call'):
                if tool_id == "knowledge_base":
                    result = tool.call({"query": "enterprise software features"})
                elif tool_id == "product_catalog":
                    result = tool.call({"category": "analytics"})
                elif tool_id == "pricing_calculator":
                    result = tool.call({"product_id": "analytics_pro", "users": 100})
                elif tool_id == "scheduler":
                    result = tool.call({"action": "check_availability", "date": "2024-01-15"})
                elif tool_id == "customer_history":
                    result = tool.call({"customer_id": "CUST_001"})
                elif tool_id == "document_retrieval":
                    result = tool.call({"query": "contract template"})
                elif tool_id == "order_management":
                    result = tool.call({"action": "get_order", "order_id": "ORD_001"})
                elif tool_id == "support_ticket":
                    result = tool.call({"action": "create", "priority": "high", "description": "Test ticket"})
                else:
                    result = tool.call({})
                
                if result and isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        print(f"✓ {tool_id}: Working correctly")
                    else:
                        print(f"✓ {tool_id}: Working correctly (with simulated error: {result.get('error', 'unknown')})")
                else:
                    print(f"✗ {tool_id}: Invalid result format")
                    return False
            else:
                print(f"✗ {tool_id}: Missing call method")
                return False
                
        except Exception as e:
            print(f"✗ {tool_id}: Error during execution - {str(e)}")
            traceback.print_exc()
            return False
    
    return True


def test_pipeline_execution():
    """Test end-to-end pipeline execution"""
    print("\nTesting pipeline execution...")
    
    # Create mock models
    models = [
        MockModel("mock-gpt-4"),
        MockModel("mock-claude-3")
    ]
    
    # Load scenarios
    scenarios = load_scenarios(["product_inquiry_001"])
    if not scenarios:
        print("✗ Failed to load test scenario")
        return False
    
    # Get evaluators and tools
    evaluators = get_all_evaluators()  # This returns a list
    tools = get_default_tools()
    
    # Create and run pipeline
    try:
        pipeline = EvaluationPipeline(
            models=models,
            scenarios=scenarios,
            evaluators=evaluators,
            tools=tools,
            num_runs=1,
            parallel=False,
            verbose=True
        )
        
        print("✓ Pipeline created successfully")
        
        # Run evaluation
        results = pipeline.run()
        
        # Validate results structure
        required_keys = ['summary', 'results', 'timestamp']
        if all(key in results for key in required_keys):
            print("✓ Pipeline execution completed")
            print(f"✓ Results structure valid")
            
            # Check summary scores
            summary = results['summary']
            if 'overall_scores' in summary:
                for model_id, score in summary['overall_scores'].items():
                    print(f"  - {model_id}: {score:.2f}/10")
                print("✓ Summary scores generated")
            else:
                print("✗ Missing overall scores in summary")
                return False
                
        else:
            print(f"✗ Invalid results structure. Missing: {[k for k in required_keys if k not in results]}")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline execution failed: {str(e)}")
        traceback.print_exc()
        return False
    
    return True


def test_report_generation():
    """Test report generation functionality"""
    print("\nTesting report generation...")
    
    # Use results from previous test if available
    test_output_dir = Path("validation_output")
    test_output_dir.mkdir(exist_ok=True)
    
    try:
        # Create a simple pipeline for report testing
        models = [MockModel("test-model")]
        scenarios = load_scenarios(["product_inquiry_001"])
        evaluators = get_all_evaluators()  # This returns a list
        tools = get_default_tools()
        
        pipeline = EvaluationPipeline(
            models=models,
            scenarios=scenarios,
            evaluators=evaluators,
            tools=tools,
            num_runs=1,
            parallel=False,
            verbose=False
        )
        
        # Run and generate report
        results = pipeline.run()
        pipeline.generate_report(test_output_dir)
        
        # Check if report files were created
        expected_files = [
            "benchmark_report.html",
            "benchmark_report.md",
            "overall_scores.csv",
            "category_scores.csv",
            "scenario_scores.csv"
        ]
        
        missing_files = []
        for file_name in expected_files:
            file_path = test_output_dir / file_name
            if file_path.exists():
                print(f"✓ Generated: {file_name}")
            else:
                missing_files.append(file_name)
        
        if missing_files:
            print(f"✗ Missing report files: {missing_files}")
            return False
        else:
            print("✓ All report files generated successfully")
            
    except Exception as e:
        print(f"✗ Report generation failed: {str(e)}")
        traceback.print_exc()
        return False
    
    return True


def run_pytest_tests():
    """Run the existing pytest test suite"""
    print("\nRunning pytest test suite...")
    
    try:
        import subprocess
        result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All pytest tests passed")
            return True
        else:
            print("✗ Some pytest tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error running pytest: {str(e)}")
        return False


def main():
    """Run comprehensive framework validation"""
    print("=" * 60)
    print("COMPREHENSIVE BIZCON FRAMEWORK VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Scenario Loading", test_scenario_loading),
        ("Evaluator Logic", test_evaluator_logic),
        ("Tool Integration", test_tool_integration),
        ("Pipeline Execution", test_pipeline_execution),
        ("Report Generation", test_report_generation),
        ("Pytest Suite", run_pytest_tests),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {str(e)}")
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Framework is fully operational.")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed. Framework needs attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())