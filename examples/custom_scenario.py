#!/usr/bin/env python3
"""
Example of creating and running a custom business scenario.
"""
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import our modules
from scenarios.base import BusinessScenario
from core.pipeline import EvaluationPipeline
from models import get_model_client
from evaluators import get_all_evaluators
from tools import get_default_tools


class SupplyChainDisruptionScenario(BusinessScenario):
    """
    Custom scenario for supply chain disruption.
    
    Tests how well the model handles complex supply chain disruption issues,
    requiring coordination across multiple departments and vendors.
    """
    
    def __init__(self, scenario_id: str = "custom_supply_chain_001"):
        """
        Initialize the supply chain disruption scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Supply Chain Disruption Handling",
            description="Customer inquiring about alternative solutions for a disrupted supply chain",
            industry="Manufacturing",
            complexity="complex",
            tools_required=["product_catalog", "order_management", "knowledge_base"]
        )
    
    def _initialize_conversation(self) -> list:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Hi there, we're experiencing a major delay with our regular component supplier due to shipping constraints. We need to find alternative parts that are compatible with our manufacturing line within the next 2 weeks. Can you help us identify options?",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_category": "manufacturing_components",
                            "availability": "immediate"
                        }
                    }
                ]
            },
            {
                "user_message": "Those alternatives look promising. Can you check if we have any current orders with those suppliers that we might be able to modify or expedite?",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "supplier_ids": ["SUP-1234", "SUP-5678"],
                            "status": "active"
                        }
                    }
                ]
            },
            {
                "user_message": "Perfect. We'll need to verify that these alternative components will work with our existing equipment. Do you have any compatibility guidelines or case studies from other customers who've made similar substitutions?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "component compatibility manufacturing substitution",
                            "categories": ["technical_specifications", "case_studies"]
                        }
                    }
                ]
            },
            {
                "user_message": "Thanks for that information. Can you also help us understand how this might impact our product quality and what additional testing we might need to do?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "component substitution quality impact testing",
                            "categories": ["quality_assurance", "testing_protocols"]
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> dict:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "alternative_components": {
                "original_component": "XYZ-1000 Power Regulator",
                "alternative_options": [
                    {
                        "name": "ABC-750 Power Module",
                        "compatibility": "95%",
                        "lead_time": "3-5 days",
                        "price_difference": "+15%"
                    },
                    {
                        "name": "DEF-800 Regulator Assembly",
                        "compatibility": "90%",
                        "lead_time": "1-2 days",
                        "price_difference": "+22%"
                    }
                ]
            },
            "order_information": {
                "existing_orders": [
                    {
                        "supplier": "ABC Manufacturing",
                        "order_id": "ORD-22789",
                        "items": ["Circuit Boards", "Connectors"],
                        "status": "Processing",
                        "delivery_date": "2 weeks"
                    },
                    {
                        "supplier": "DEF Components",
                        "order_id": "ORD-23001",
                        "items": ["Casings", "Displays"],
                        "status": "Shipped",
                        "delivery_date": "5 days"
                    }
                ]
            },
            "compatibility_information": {
                "key_considerations": [
                    "Voltage tolerance (±5%)",
                    "Heat dissipation requirements",
                    "Physical dimensions and mounting points",
                    "Communication protocol compatibility"
                ],
                "successful_case_studies": [
                    "Company A successfully substituted similar components with minor firmware adjustments",
                    "Company B used the ABC-750 as a drop-in replacement with no issues"
                ],
                "potential_issues": [
                    "May require recalibration of the production line",
                    "Slight differences in power efficiency might affect final product performance",
                    "Some connectors might need adapters"
                ]
            },
            "quality_impact": {
                "required_testing": [
                    "Accelerated life testing (minimum 72 hours)",
                    "Thermal cycle testing (25 cycles)",
                    "Power surge protection verification",
                    "Full system integration testing"
                ],
                "expected_impact": [
                    "Minimal impact on product lifespan",
                    "Potentially improved surge protection",
                    "Slight increase in power consumption"
                ]
            }
        }


def run_custom_scenario(model_provider, model_name, api_key):
    """Run the custom scenario with the specified model."""
    # Create model client
    model = get_model_client(
        provider=model_provider,
        model_name=model_name,
        api_key=api_key,
        temperature=0.7,
        max_tokens=2048
    )
    
    # Create scenario
    scenario = SupplyChainDisruptionScenario()
    
    # Create pipeline
    pipeline = EvaluationPipeline(
        models=[model],
        scenarios=[scenario],
        evaluators=get_all_evaluators(),
        tools=get_default_tools(),
        num_runs=1,
        verbose=True
    )
    
    # Run evaluation
    print(f"Running custom scenario with {model_provider}/{model_name}...")
    results = pipeline.run()
    
    # Print results
    model_id = model.model_name
    scenario_id = scenario.scenario_id
    score = results["summary"]["overall_scores"][model_id]
    
    print(f"\nResults for {model_id} on {scenario.name}:")
    print(f"Overall Score: {score:.2f}/10")
    
    # Category scores
    print("\nCategory Scores:")
    for category, score in results["summary"]["category_scores"][model_id].items():
        print(f"  {category}: {score:.2f}/10")
    
    # Generate report
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "custom_scenario")
    os.makedirs(output_dir, exist_ok=True)
    
    pipeline.generate_report(output_dir)
    print(f"\nDetailed report saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a custom business scenario")
    parser.add_argument("--provider", default="openai", help="Model provider (openai, anthropic, mistral)")
    parser.add_argument("--model", default="gpt-4", help="Model name")
    parser.add_argument("--api-key", help="API key (or set as environment variable)")
    
    args = parser.parse_args()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.environ.get(f"{args.provider.upper()}_API_KEY")
    if not api_key:
        print(f"Error: No API key provided. Set {args.provider.upper()}_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    run_custom_scenario(args.provider, args.model, api_key)