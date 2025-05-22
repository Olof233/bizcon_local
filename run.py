#!/usr/bin/env python3
"""
Main entry point for running bizCon benchmarks.
"""

import os
import sys
import argparse
import yaml
import json
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import our modules
from models import get_model_client
from scenarios import _SCENARIO_REGISTRY
from evaluators import get_all_evaluators
from tools import get_default_tools
from core.pipeline import EvaluationPipeline


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_scenarios(scenario_ids=None):
    """
    Load scenarios by ID.
    
    Args:
        scenario_ids: Optional list of scenario IDs to load
        
    Returns:
        List of scenario instances
    """
    if scenario_ids is None:
        # Load all scenarios
        scenario_ids = list(_SCENARIO_REGISTRY.keys())
    
    scenarios = []
    for scenario_id in scenario_ids:
        if scenario_id in _SCENARIO_REGISTRY:
            scenario_class = _SCENARIO_REGISTRY[scenario_id]
            scenarios.append(scenario_class(scenario_id=scenario_id))
    
    return scenarios


def load_models(config):
    """
    Load model clients from configuration.
    
    Args:
        config: Dictionary with model configurations
        
    Returns:
        List of model client instances
    """
    models = []
    for model_config in config['models']:
        provider = model_config['provider']
        model_name = model_config['name']
        
        # Get API key from environment or config
        api_key = os.environ.get(f"{provider.upper()}_API_KEY", model_config.get('api_key'))
        if not api_key:
            print(f"Warning: No API key found for {provider}. Set {provider.upper()}_API_KEY environment variable.")
            continue
        
        # Create model client
        model = get_model_client(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=model_config.get('temperature', 0.7),
            max_tokens=model_config.get('max_tokens', 1024)
        )
        models.append(model)
    
    return models


def run_benchmark(config_path, output_dir, scenario_ids=None, parallel=False):
    """
    Run benchmark evaluation.
    
    Args:
        config_path: Path to configuration file
        output_dir: Directory to save output
        scenario_ids: Optional list of scenario IDs to run
        parallel: Whether to run evaluations in parallel
    """
    # Load configuration
    config = load_config(config_path)
    
    # Load models
    models = load_models(config)
    if not models:
        print("Error: No models loaded. Check your API keys and configuration.")
        return
    
    # Load scenarios
    scenarios = load_scenarios(scenario_ids)
    if not scenarios:
        print("Error: No scenarios loaded. Check your scenario IDs.")
        return
    
    # Load evaluators with weights from config
    evaluator_weights = config.get('evaluation', {}).get('weights', {})
    evaluators = get_all_evaluators(weights=evaluator_weights)
    
    # Load tools with error rates from config
    tool_error_rates = config.get('evaluation', {}).get('tool_error_rates', {})
    tools = get_default_tools()
    for tool_id, tool in tools.items():
        if tool_id in tool_error_rates:
            tool.error_rate = tool_error_rates[tool_id]
    
    # Set up pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=scenarios,
        evaluators=evaluators,
        tools=tools,
        num_runs=config.get('evaluation', {}).get('num_runs', 1),
        parallel=parallel,
        verbose=True
    )
    
    # Run evaluation
    print(f"Running benchmark with {len(models)} models on {len(scenarios)} scenarios...")
    results = pipeline.run()
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    timestamp = results.get('timestamp', 'unknown')
    output_file = os.path.join(output_dir, f"benchmark_results_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    # Generate report
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.html")
    pipeline.generate_report(report_file)
    
    print(f"Report saved to {report_file}")
    
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
    parser.add_argument("--list-scenarios", "-l", action="store_true",
                        help="List available scenarios and exit")
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        print("\nAvailable Scenarios:")
        print("-------------------")
        for scenario_id, scenario_class in sorted(_SCENARIO_REGISTRY.items()):
            # Create an instance to get metadata
            scenario = scenario_class(scenario_id=scenario_id)
            print(f"{scenario_id}: {scenario.name}")
        return
    
    run_benchmark(
        config_path=args.config,
        output_dir=args.output,
        scenario_ids=args.scenarios,
        parallel=args.parallel
    )


if __name__ == "__main__":
    main()
