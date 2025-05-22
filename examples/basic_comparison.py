#!/usr/bin/env python3
"""
Basic example of comparing multiple LLMs using bizCon framework.
"""
import os
import sys
import argparse
import yaml
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Use relative imports instead of bizcon package imports
from core.pipeline import EvaluationPipeline
from models import get_model_client
from scenarios import load_scenarios


def run_comparison(config_path, output_dir, scenario_ids=None):
    """
    Run a basic comparison of models using specified scenarios.
    
    Args:
        config_path: Path to config file with model definitions
        output_dir: Directory to save evaluation results
        scenario_ids: Optional list of specific scenario IDs to run
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize models
    models = []
    for model_config in config.get('models', []):
        provider = model_config.get('provider')
        model_name = model_config.get('name')
        params = model_config.get('parameters', {})
        temperature = model_config.get('temperature', 0.7)
        max_tokens = model_config.get('max_tokens', 1024)
        
        try:
            model = get_model_client(
                provider=provider, 
                model_name=model_name, 
                temperature=temperature,
                max_tokens=max_tokens,
                **params
            )
            models.append(model)
            print(f"Initialized model: {model}")
        except Exception as e:
            print(f"Error initializing model {provider}/{model_name}: {e}")
    
    if not models:
        print("No models could be initialized. Check your configuration.")
        return
    
    # Load scenarios
    if scenario_ids:
        scenarios = load_scenarios(scenario_ids)
    else:
        # Default to product inquiry and appointment scheduling scenarios
        scenarios = load_scenarios([
            "product_inquiry_001",
            "product_inquiry_002",
            "appointment_001",
            "support_001"
        ])
    
    print(f"Loaded {len(scenarios)} scenarios for evaluation")
    
    # Create evaluation pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=scenarios,
        num_runs=2,  # Run each scenario twice for consistency
        parallel=True,
        verbose=True
    )
    
    # Run evaluation
    print("Running evaluations...")
    results = pipeline.run()
    
    # Generate report
    print("Generating report...")
    os.makedirs(output_dir, exist_ok=True)
    pipeline.generate_report(output_dir)
    
    print(f"Evaluation complete. Results saved to {output_dir}")
    
    # Print summary
    print("\nSummary of Results:")
    for model_id, score in results["summary"]["overall_scores"].items():
        print(f"  {model_id}: {score:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a basic comparison of LLMs using bizCon")
    parser.add_argument("--config", default="../config/models.yaml", help="Path to model config file")
    parser.add_argument("--output", default="../output/basic_comparison", help="Output directory for results")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenario IDs to run")
    
    args = parser.parse_args()
    
    run_comparison(args.config, args.output, args.scenarios)