#!/usr/bin/env python3
"""
Script for testing a specific scenario with a specific model.
Useful for debugging and verification.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.runner import ScenarioRunner
from models import get_model_client
from scenarios import get_scenario_class, _SCENARIO_REGISTRY
from evaluators.response_quality import ResponseQualityEvaluator
from evaluators.communication_style import CommunicationStyleEvaluator
from tools.knowledge_base import KnowledgeBaseTool
from tools.product_catalog import ProductCatalogTool


def list_scenarios():
    """List all available scenarios."""
    print("\nAvailable Scenarios:")
    print("--------------------")
    for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
        # Create an instance to get metadata
        scenario = scenario_class(scenario_id=scenario_id)
        print(f"ID: {scenario_id}")
        print(f"  Name: {scenario.name}")
        print(f"  Industry: {scenario.industry}")
        print(f"  Complexity: {scenario.complexity}")
        print(f"  Required Tools: {', '.join(scenario.tools_required)}")
        print()


def run_scenario(scenario_id, provider, model_name, verbose=False):
    """
    Run a specific scenario with a specific model.
    
    Args:
        scenario_id: ID of the scenario to run
        provider: Model provider (openai, anthropic, mistral)
        model_name: Name of the model
        verbose: Whether to print detailed information
    """
    # Check if scenario exists
    scenario_class = get_scenario_class(scenario_id)
    if not scenario_class:
        print(f"Error: Scenario '{scenario_id}' not found.")
        list_scenarios()
        return
    
    # Initialize scenario
    scenario = scenario_class(scenario_id=scenario_id)
    print(f"\nRunning scenario: {scenario.name} ({scenario_id})")
    
    # Initialize model
    try:
        model = get_model_client(provider, model_name)
        print(f"Using model: {model}")
    except Exception as e:
        print(f"Error initializing model {provider}/{model_name}: {e}")
        return
    
    # Initialize evaluators
    evaluators = [
        ResponseQualityEvaluator(weight=0.6),
        CommunicationStyleEvaluator(weight=0.4)
    ]
    
    # Initialize tools
    tools = {
        "knowledge_base": KnowledgeBaseTool(),
        "product_catalog": ProductCatalogTool()
    }
    
    # Create a runner
    runner = ScenarioRunner(
        model=model,
        scenario=scenario,
        evaluators=evaluators,
        tools=tools
    )
    
    # Run the scenario
    print("\nExecuting scenario...")
    result = runner.run()
    
    # Print results
    print("\nResults:")
    print(f"Overall Score: {result['overall_score']:.2f}/10")
    print("\nCategory Scores:")
    for category, score in result['category_scores'].items():
        print(f"  {category}: {score:.2f}/10")
    
    # Print conversation if verbose
    if verbose:
        print("\nConversation:")
        for i, turn in enumerate(result['turns']):
            print(f"\n--- Turn {i+1} ---")
            print(f"User: {turn['user_message']}")
            print(f"Model: {turn['model_response']['content']}")
            
            if turn.get('tool_calls'):
                print("\nTool Calls:")
                for call in turn['tool_calls']:
                    print(f"  Tool: {call['tool_id']}")
                    print(f"  Parameters: {call['parameters']}")
                    print(f"  Result: {json.dumps(call['result'], indent=2)[:200]}...")
            
            print("\nEvaluation:")
            for metric, score in turn['evaluation'].items():
                if isinstance(score, dict) and 'score' in score:
                    print(f"  {metric}: {score['score']:.2f}")
                    if 'explanation' in score:
                        print(f"    {score['explanation'][:100]}...")
    
    # Save results to file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{scenario_id}_{provider}_{model_name.replace('-', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test a specific scenario with a specific model")
    parser.add_argument("--scenario", help="Scenario ID to run")
    parser.add_argument("--provider", default="openai", 
                        choices=["openai", "anthropic", "mistral"],
                        help="Model provider")
    parser.add_argument("--model", default="gpt-3.5-turbo", 
                        help="Model name")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print detailed information")
    parser.add_argument("--list", action="store_true", 
                        help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
        return
    
    if not args.scenario:
        print("Error: Please specify a scenario ID or use --list to see available scenarios.")
        return
    
    run_scenario(args.scenario, args.provider, args.model, args.verbose)


if __name__ == "__main__":
    main()
