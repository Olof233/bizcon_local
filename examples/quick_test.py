#!/usr/bin/env python3
"""
Quick test script for bizCon framework.
This script runs a simple benchmark with a single model and a small set of scenarios.
"""
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import modules
from models import get_model_client
from scenarios import load_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools
from core.pipeline import EvaluationPipeline


def run_quick_test(model_provider, model_name, api_key, output_dir):
    """
    Run a quick benchmark test with a single model.
    
    Args:
        model_provider: Model provider name (openai, anthropic, mistral)
        model_name: Model name to test
        api_key: API key for the model provider
        output_dir: Directory to save results
    """
    # Initialize model
    try:
        model = get_model_client(
            provider=model_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=0.7,
            max_tokens=1024
        )
        print(f"Initialized model: {model}")
    except Exception as e:
        print(f"Error initializing model {model_provider}/{model_name}: {e}")
        return
    
    # Load a small set of scenarios (one from each category)
    test_scenarios = [
        "product_inquiry_001",      # Product inquiry
        "appointment_001",          # Appointment scheduling
        "support_001",              # Technical support
        "contract_001",             # Contract negotiation
    ]
    
    scenarios = load_scenarios(test_scenarios)
    print(f"Loaded {len(scenarios)} test scenarios")
    
    # Create evaluation pipeline
    pipeline = EvaluationPipeline(
        models=[model],
        scenarios=scenarios,
        evaluators=get_all_evaluators(),
        tools=get_default_tools(),
        num_runs=1,
        parallel=False,
        verbose=True
    )
    
    # Run evaluation
    print(f"Running quick test benchmark...")
    results = pipeline.run()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate report
    pipeline.generate_report(output_dir)
    
    # Print summary
    print("\nTest Results:")
    overall_score = results["summary"]["overall_scores"][model.model_name]
    print(f"Overall Score: {overall_score:.2f}/10")
    
    print("\nCategory Scores:")
    for category, score in results["summary"]["category_scores"][model.model_name].items():
        print(f"  {category}: {score:.2f}/10")
    
    print("\nScenario Scores:")
    for scenario_id, score in results["summary"]["scenario_scores"][model.model_name].items():
        scenario_name = next((s.name for s in scenarios if s.scenario_id == scenario_id), scenario_id)
        print(f"  {scenario_name}: {score:.2f}/10")
    
    print(f"\nFull report saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a quick test benchmark with bizCon")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic", "mistral"],
                        help="Model provider name")
    parser.add_argument("--model", default="gpt-4",
                        help="Model name")
    parser.add_argument("--api-key",
                        help="API key (or set as environment variable)")
    parser.add_argument("--output", default="../output/quick_test",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.environ.get(f"{args.provider.upper()}_API_KEY")
    if not api_key:
        print(f"Error: No API key provided. Set {args.provider.upper()}_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    run_quick_test(args.provider, args.model, api_key, args.output)
