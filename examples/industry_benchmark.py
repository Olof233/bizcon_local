#!/usr/bin/env python3
"""
Industry-specific benchmark for LLMs using bizCon framework.
This example evaluates models on industry-specific scenarios.
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
from scenarios import load_scenarios, discover_scenarios


def run_industry_benchmark(config_path, output_dir, industry=None):
    """
    Run an industry-specific benchmark of models.
    
    Args:
        config_path: Path to config file with model definitions
        output_dir: Directory to save evaluation results
        industry: Specific industry to focus on (e.g., 'healthcare', 'finance')
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
    
    # Discover all available scenarios
    discover_scenarios()
    
    # Load all scenarios
    all_scenarios = []
    
    # Healthcare scenarios
    if not industry or industry.lower() == 'healthcare':
        healthcare_scenarios = [
            "compliance_001",  # Regulatory compliance for healthcare
            "implementation_001",  # Healthcare system implementation
            "support_002",  # Complex integration for medical systems
        ]
        all_scenarios.extend(load_scenarios(healthcare_scenarios))
    
    # Financial services scenarios
    if not industry or industry.lower() == 'finance':
        finance_scenarios = [
            "contract_002",  # Enterprise agreement negotiation
            "multi_dept_001",  # Cross-functional project
            "complaints_003",  # Billing dispute resolution
        ]
        all_scenarios.extend(load_scenarios(finance_scenarios))
    
    # Retail scenarios
    if not industry or industry.lower() == 'retail':
        retail_scenarios = [
            "product_inquiry_002",  # Product customization
            "order_management_001",  # Order processing and tracking
            "complaints_001",  # High-value customer complaint
        ]
        all_scenarios.extend(load_scenarios(retail_scenarios))
    
    print(f"Loaded {len(all_scenarios)} industry-specific scenarios for evaluation")
    
    # Create evaluation pipeline
    pipeline = EvaluationPipeline(
        models=models,
        scenarios=all_scenarios,
        num_runs=3,  # Run each scenario multiple times for consistency
        parallel=True,
        verbose=True
    )
    
    # Run evaluation
    print("Running industry benchmark evaluations...")
    results = pipeline.run()
    
    # Generate report
    print("Generating report...")
    report_dir = os.path.join(output_dir, f"industry_benchmark_{industry or 'all'}")
    os.makedirs(report_dir, exist_ok=True)
    pipeline.generate_report(report_dir)
    
    print(f"Evaluation complete. Results saved to {report_dir}")
    
    # Print summary
    print("\nSummary of Results:")
    for model_id, score in results["summary"]["overall_scores"].items():
        print(f"  {model_id}: {score:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an industry-specific benchmark of LLMs using bizCon")
    parser.add_argument("--config", default="../config/models.yaml", help="Path to model config file")
    parser.add_argument("--output", default="../output", help="Output directory for results")
    parser.add_argument("--industry", choices=["healthcare", "finance", "retail"], 
                        help="Specific industry to benchmark")
    
    args = parser.parse_args()
    
    run_industry_benchmark(args.config, args.output, args.industry)