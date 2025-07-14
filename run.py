#!/usr/bin/env python3
"""
Main entry point for running bizCon benchmarks.
"""

import os
import sys
import argparse
import yaml
import json
import datetime
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import our modules
from models import get_model_client, list_supported_models
from scenarios import load_scenarios, list_available_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools
from core.pipeline import EvaluationPipeline


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_scenarios_by_config(config, scenario_ids=None):
    """
    Load scenarios based on configuration and optional specific IDs.
    
    Args:
        config: Configuration dictionary
        scenario_ids: Optional list of specific scenario IDs to load
        
    Returns:
        List of scenario instances
    """
    if scenario_ids:
        # Load specific scenarios by ID
        return load_scenarios(scenario_ids)
    
    # Check for scenarios in config
    config_scenarios = config.get('evaluation', {}).get('scenarios', [])
    if config_scenarios:
        return load_scenarios(config_scenarios)
    
    # Check for scenario categories in config
    scenario_categories = config.get('evaluation', {}).get('scenario_categories', [])
    if scenario_categories:
        # Get all available scenarios
        available_scenarios = list_available_scenarios()
        scenario_ids = []
        
        for scenario_id, metadata in available_scenarios.items():
            category = scenario_id.split('_')[0]
            if category in scenario_categories:
                scenario_ids.append(scenario_id)
        
        return load_scenarios(scenario_ids)
    
    # Default to all scenarios
    return load_scenarios(list(list_available_scenarios().keys()))


def load_models_from_config(config):
    """
    Load model clients from configuration.
    
    Args:
        config: Dictionary with model configurations
        
    Returns:
        List of model client instances
    """
    models = []
    for model_config in config.get('models', []):
        provider = model_config.get('provider')
        model_name = model_config.get('name')
        
        # Get API key from environment or config
        api_key = os.environ.get(f"{provider.upper()}_API_KEY", model_config.get('api_key'))
        if not api_key:
            print(f"Warning: No API key found for {provider}. Set {provider.upper()}_API_KEY environment variable.")
            continue
        
        # Create model client
        try:
            print(model_config.get('api_version'), model_config.get('azure_endpoint'))
            model = get_model_client(
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                temperature=model_config.get('temperature', 0.7),
                max_tokens=model_config.get('max_tokens', 1024),
                api_version=model_config.get('api_version'),  # For Azure models
                endpoint=model_config.get('azure_endpoint'),  # For Azure models
                **(model_config.get('parameters', {}))
            )
            models.append(model)
            print(f"Initialized model: {model}")
        except Exception as e:
            print(f"Error initializing model {provider}/{model_name}: {e}")
    
    return models


def run_benchmark(config_path, output_dir, scenario_ids=None, parallel=False, verbose=False):
    """
    Run benchmark evaluation.
    
    Args:
        config_path: Path to configuration file
        output_dir: Directory to save output
        scenario_ids: Optional list of scenario IDs to run
        parallel: Whether to run evaluations in parallel
        verbose: Whether to display detailed progress
    """
    # Load configuration
    config = load_config(config_path)
    
    # Load models
    models = load_models_from_config(config)
    if not models:
        print("Error: No models loaded. Check your API keys and configuration.")
        return
    
    # Load scenarios
    scenarios = load_scenarios_by_config(config, scenario_ids)
    if not scenarios:
        print("Error: No scenarios loaded. Check your scenario IDs or configuration.")
        return
    
    print(f"Loaded {len(scenarios)} scenarios for evaluation")
    
    # Load evaluators with weights from config
    evaluator_weights = config.get('evaluation', {}).get('evaluator_weights', {})
    evaluators = get_all_evaluators(weights=evaluator_weights)
    
    # Load tools with error rates from config
    tool_error_rates = config.get('evaluation', {}).get('tool_error_rates', {})
    tools = get_default_tools()
    for tool_id, tool in tools.items():
        if tool_id in tool_error_rates:
            tool.error_rate = tool_error_rates[tool_id]
    
    # Get number of runs from config
    num_runs = config.get('evaluation', {}).get('num_runs', 1)
    
    # Set up pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=scenarios,
        evaluators=evaluators,
        tools=tools,
        num_runs=num_runs,
        parallel=parallel,
        verbose=verbose
    )
    
    # Run evaluation
    print(f"Running benchmark with {len(models)} models on {len(scenarios)} scenarios...")
    results = pipeline.run()
    
    # Create timestamped output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(output_dir, f"benchmark_{timestamp}")
    os.makedirs(result_dir, exist_ok=True)
    
    # Save raw results
    results_file = os.path.join(result_dir, "results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {results_file}")
    
    # Generate report
    pipeline.generate_report(result_dir)
    
    print(f"Report generated in {result_dir}")
    
    # Print summary
    print("\nSummary of Results:")
    for model_id, score in results["summary"]["overall_scores"].items():
        print(f"  {model_id}: {score:.2f}")
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run bizCon benchmarks")
    parser.add_argument("--config", "-c", type=str, default="config/models.yaml",
                        help="Path to configuration file")
    parser.add_argument("--output", "-o", type=str, default="output",
                        help="Directory to save results")
    parser.add_argument("--scenarios", "-s", type=str, nargs="+",
                        help="Specific scenario IDs to run")
    parser.add_argument("--parallel", "-p", action="store_true",
                        help="Run evaluations in parallel")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Display detailed progress")
    parser.add_argument("--list-scenarios", "-l", action="store_true",
                        help="List available scenarios and exit")
    parser.add_argument("--list-models", "-m", action="store_true",
                        help="List supported models and exit")
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        print("\nAvailable Scenarios:")
        print("-------------------")
        scenarios = list_available_scenarios()
        for scenario_id, metadata in sorted(scenarios.items()):
            print(f"{scenario_id}: {metadata.get('name')}")
            if args.verbose and 'description' in metadata:
                print(f"  {metadata['description']}")
        return
    
    if args.list_models:
        print("\nSupported Models:")
        print("----------------")
        models = list_supported_models()
        for provider, provider_models in sorted(models.items()):
            print(f"{provider}:")
            for model in provider_models:
                print(f"  - {model}")
        return
    
    run_benchmark(
        config_path=args.config,
        output_dir=args.output,
        scenario_ids=args.scenarios,
        parallel=args.parallel,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
