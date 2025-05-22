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

from bizcon.core.pipeline import EvaluationPipeline
from bizcon.models import get_model_client
from bizcon.scenarios import load_scenarios


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
        params = model_config.get('parameters', {})
        
        try:
            model = get_model_client(provider, model_name, **params)
            models.append(model)
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
            scenario = load_scenarios(scenario_id)
            if scenario:
                scenarios.append(scenario)
    else:
        scenarios = load_scenarios(config.get('scenarios', []))
    
    if not scenarios:
        print("No scenarios could be loaded. Check your configuration.")
        return 1
    
    # Initialize and run pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=scenarios,
        num_runs=args.runs,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
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
    
    return 0


def list_scenarios(args):
    """List available scenarios"""
    from bizcon.scenarios import list_available_scenarios
    
    scenarios = list_available_scenarios()
    
    print("Available scenarios:")
    for scenario_id, scenario_info in scenarios.items():
        print(f"  - {scenario_id}: {scenario_info.get('name', 'Unnamed')}")
        if args.verbose and 'description' in scenario_info:
            print(f"      {scenario_info['description']}")
    
    return 0


def list_models(args):
    """List supported models"""
    from bizcon.models import list_supported_models
    
    models = list_supported_models()
    
    print("Supported models:")
    for provider, model_list in models.items():
        print(f"  {provider}:")
        for model in model_list:
            print(f"    - {model}")
    
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
    
    args = parser.parse_args()
    
    if args.command == "run":
        return run_evaluation(args)
    elif args.command == "list-scenarios":
        return list_scenarios(args)
    elif args.command == "list-models":
        return list_models(args)
    else:
        parser.print_help()
        return 0
    
if __name__ == "__main__":
    sys.exit(main())
