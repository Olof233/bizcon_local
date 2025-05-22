#!/usr/bin/env python3
"""
Command-line interface for bizCon framework.
"""

import argparse
import sys
import os
import yaml
import json
from pathlib import Path

from core.pipeline import EvaluationPipeline
from models import get_model_client, list_supported_models
from scenarios import load_scenarios, list_available_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools
from visualization.dashboard import launch_dashboard


def run_evaluation(args):
    """Run evaluation with specified models and scenarios"""
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize models
    models = []
    for model_config in config.get('models', []):
        model_name = model_config.get('name')
        provider = model_config.get('provider')
        temperature = model_config.get('temperature', 0.7)
        max_tokens = model_config.get('max_tokens', 1024)
        params = model_config.get('parameters', {})
        
        # Get API key from environment or config
        api_key = os.environ.get(f"{provider.upper()}_API_KEY", model_config.get('api_key'))
        if not api_key:
            print(f"Warning: No API key found for {provider}. Set {provider.upper()}_API_KEY environment variable.")
            continue
        
        try:
            model = get_model_client(
                provider=provider, 
                model_name=model_name, 
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **params
            )
            models.append(model)
            print(f"Initialized model: {model}")
        except Exception as e:
            print(f"Error initializing model {model_name}: {e}")
            continue
    
    if not models:
        print("No models could be initialized. Check your configuration.")
        return 1
    
    # Load scenarios
    scenarios = []
    if args.scenario:
        for scenario_id in args.scenario:
            loaded_scenarios = load_scenarios(scenario_id)
            if loaded_scenarios:
                scenarios.extend(loaded_scenarios)
            else:
                print(f"Warning: Scenario '{scenario_id}' not found.")
    else:
        # Load scenarios from config or use default selection
        scenario_ids = config.get('evaluation', {}).get('scenarios', [])
        if scenario_ids:
            scenarios = load_scenarios(scenario_ids)
        else:
            # Use scenarios from specific categories
            scenario_categories = config.get('evaluation', {}).get('scenario_categories', [])
            available_scenarios = list_available_scenarios()
            
            for scenario_id, metadata in available_scenarios.items():
                category = scenario_id.split('_')[0]
                if category in scenario_categories or not scenario_categories:
                    loaded = load_scenarios(scenario_id)
                    if loaded:
                        scenarios.extend(loaded)
    
    if not scenarios:
        print("No scenarios could be loaded. Check your configuration.")
        return 1
    
    print(f"Loaded {len(scenarios)} scenarios for evaluation")
    
    # Get evaluator weights from config
    evaluator_weights = config.get('evaluation', {}).get('evaluator_weights', {})
    evaluators = get_all_evaluators(weights=evaluator_weights)
    
    # Get tool error rates from config
    tool_error_rates = config.get('evaluation', {}).get('tool_error_rates', {})
    tools = get_default_tools()
    for tool_id, tool in tools.items():
        if tool_id in tool_error_rates:
            tool.error_rate = tool_error_rates[tool_id]
    
    # Initialize and run pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=scenarios,
        evaluators=evaluators,
        tools=tools,
        num_runs=args.runs,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
    print(f"Running evaluation with {len(models)} models on {len(scenarios)} scenarios...")
    results = pipeline.run()
    
    # Generate report
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pipeline.generate_report(output_dir)
        
        if args.format == 'json':
            with open(output_dir / 'results.json', 'w') as f:
                json.dump(results, f, indent=2)
        
        print(f"Results saved to {output_dir}")
        
        # Print summary
        print("\nSummary of Results:")
        for model_id, score in results["summary"]["overall_scores"].items():
            print(f"  {model_id}: {score:.2f}")
    
    return 0


def list_scenarios(args):
    """List available scenarios"""
    scenarios = list_available_scenarios()
    
    print("Available scenarios:")
    for scenario_id, scenario_info in scenarios.items():
        print(f"  - {scenario_id}: {scenario_info.get('name', 'Unnamed')}")
        if args.verbose and 'description' in scenario_info:
            print(f"      {scenario_info['description']}")
    
    return 0


def list_models(args):
    """List supported models"""
    models = list_supported_models()
    
    print("Supported models:")
    for provider, model_list in models.items():
        print(f"  {provider}:")
        for model in model_list:
            print(f"    - {model}")
    
    return 0


def start_dashboard(args):
    """Start the interactive dashboard"""
    results_dir = Path(args.results_dir)
    if not results_dir.exists() or not any(results_dir.glob('*.json')):
        print(f"No results found in {results_dir}. Run evaluations first.")
        return 1
    
    print(f"Starting dashboard with results from {results_dir}")
    launch_dashboard(results_dir, args.host, args.port)
    return 0


def main():
    parser = argparse.ArgumentParser(description="bizCon: LLM Business Conversation Evaluation Framework")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Run evaluation command
    run_parser = subparsers.add_parser("run", help="Run evaluation")
    run_parser.add_argument("-c", "--config", default="config/evaluation.yaml", 
                           help="Path to configuration file")
    run_parser.add_argument("-s", "--scenario", nargs="+", 
                           help="Specific scenario IDs to run (overrides config)")
    run_parser.add_argument("-o", "--output", default="output", 
                           help="Output directory for results")
    run_parser.add_argument("-f", "--format", choices=["json", "csv"], default="json",
                           help="Output format for raw results")
    run_parser.add_argument("-r", "--runs", type=int, default=1,
                           help="Number of runs per scenario")
    run_parser.add_argument("-p", "--parallel", action="store_true",
                           help="Run evaluations in parallel")
    run_parser.add_argument("-v", "--verbose", action="store_true",
                           help="Enable verbose output")
    
    # List scenarios command
    list_scenarios_parser = subparsers.add_parser("list-scenarios", help="List available scenarios")
    list_scenarios_parser.add_argument("-v", "--verbose", action="store_true",
                                      help="Show detailed scenario descriptions")
    
    # List models command
    list_models_parser = subparsers.add_parser("list-models", help="List supported models")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start interactive dashboard")
    dashboard_parser.add_argument("-d", "--results-dir", default="output",
                               help="Directory containing benchmark results")
    dashboard_parser.add_argument("--host", default="127.0.0.1",
                               help="Host to run the dashboard server on")
    dashboard_parser.add_argument("--port", type=int, default=5000,
                               help="Port to run the dashboard server on")
    
    args = parser.parse_args()
    
    if args.command == "run":
        return run_evaluation(args)
    elif args.command == "list-scenarios":
        return list_scenarios(args)
    elif args.command == "list-models":
        return list_models(args)
    elif args.command == "dashboard":
        return start_dashboard(args)
    else:
        parser.print_help()
        return 0
    
if __name__ == "__main__":
    sys.exit(main())
