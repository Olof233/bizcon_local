#!/usr/bin/env python3
"""
Verification script for bizCon framework.
This script checks that all components are properly implemented and working.
"""

import os
import sys
import importlib
import inspect
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Add colors for better output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"


def print_status(component: str, status: str, details: Optional[str] = None):
    """Print component status with color."""
    status_color = {
        "OK": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "INFO": BLUE
    }
    
    color = status_color.get(status, "")
    status_str = f"{color}{status}{ENDC}"
    
    print(f"{component:30} [{status_str}]")
    if details:
        for line in details.split('\n'):
            print(f"  {line}")


def check_models():
    """Check that model clients are properly implemented."""
    try:
        from models import get_model_client, list_supported_models
        
        # Check model registry
        supported_models = list_supported_models()
        print_status("Models Registry", "INFO", f"Found {sum(len(models) for models in supported_models.values())} models across {len(supported_models)} providers")
        
        # Check model implementations
        model_classes = []
        for provider, models in supported_models.items():
            try:
                # Check first model from each provider
                if models:
                    model = get_model_client(provider, models[0], api_key="dummy_key_for_testing")
                    model_classes.append(model.__class__.__name__)
            except Exception as e:
                print_status(f"Model Provider: {provider}", "ERROR", f"Implementation error: {str(e)}")
                continue
        
        if model_classes:
            print_status("Model Implementations", "OK", f"Found implementations: {', '.join(model_classes)}")
        else:
            print_status("Model Implementations", "ERROR", "No working model implementations found")
    except Exception as e:
        print_status("Models Module", "ERROR", f"Failed to import models module: {str(e)}")


def check_scenarios():
    """Check that scenarios are properly implemented."""
    try:
        from scenarios import _SCENARIO_REGISTRY, load_scenarios
        
        # Check scenario registry
        scenario_count = len(_SCENARIO_REGISTRY)
        print_status("Scenario Registry", "INFO", f"Found {scenario_count} registered scenarios")
        
        # Load a few scenarios to verify implementation
        if _SCENARIO_REGISTRY:
            # Take first 2 scenarios from registry
            scenario_ids = list(_SCENARIO_REGISTRY.keys())[:2]
            
            # Instantiate scenarios
            scenarios = load_scenarios(scenario_ids)
            
            if scenarios:
                print_status("Scenario Loading", "OK", 
                            f"Successfully loaded: {', '.join(s.name for s in scenarios)}")
                
                # Check scenario contents
                for scenario in scenarios:
                    conversation = scenario.get_conversation()
                    ground_truth = scenario.get_ground_truth()
                    
                    if conversation and isinstance(conversation, list):
                        print_status(f"Scenario: {scenario.name}", "OK", 
                                    f"Has {len(conversation)} conversation turns")
                    else:
                        print_status(f"Scenario: {scenario.name}", "WARNING", 
                                    "Missing or invalid conversation data")
            else:
                print_status("Scenario Loading", "ERROR", "Failed to load any scenarios")
    except Exception as e:
        print_status("Scenarios Module", "ERROR", f"Failed to import scenarios module: {str(e)}")


def check_evaluators():
    """Check that evaluators are properly implemented."""
    try:
        from evaluators import get_all_evaluators, EVALUATOR_REGISTRY
        
        # Check evaluator registry
        evaluator_count = len(EVALUATOR_REGISTRY)
        print_status("Evaluator Registry", "INFO", f"Found {evaluator_count} registered evaluators")
        
        try:
            # Load all evaluators
            evaluators = get_all_evaluators()
            evaluator_names = [e.name for e in evaluators]
            
            if evaluators:
                print_status("Evaluator Loading", "OK", f"Successfully loaded: {', '.join(evaluator_names)}")
            else:
                print_status("Evaluator Loading", "ERROR", "Failed to load any evaluators")
        except Exception as e:
            print_status("Evaluator Loading", "ERROR", f"Error: {str(e)}")
    except Exception as e:
        print_status("Evaluators Module", "ERROR", f"Failed to import evaluators module: {str(e)}")


def check_tools():
    """Check that business tools are properly implemented."""
    try:
        from tools import get_default_tools
        
        try:
            # Load all tools
            tools = get_default_tools()
            
            if tools:
                print_status("Tools Loading", "OK", f"Successfully loaded {len(tools)} tools: {', '.join(tools.keys())}")
                
                # Check a few key tools
                key_tools = ["knowledge_base", "product_catalog"]
                for tool_id in key_tools:
                    if tool_id in tools:
                        tool = tools[tool_id]
                        # Try a basic call to make sure it works
                        try:
                            if tool_id == "knowledge_base":
                                result = tool.call({"query": "test"})
                            elif tool_id == "product_catalog":
                                result = tool.call({"product_id": "test"})
                            
                            print_status(f"Tool: {tool.name}", "OK", "Basic call succeeded")
                        except Exception as e:
                            print_status(f"Tool: {tool.name}", "WARNING", f"Basic call failed: {str(e)}")
            else:
                print_status("Tools Loading", "ERROR", "Failed to load any tools")
        except Exception as e:
            print_status("Tools Loading", "ERROR", f"Error: {str(e)}")
    except Exception as e:
        print_status("Tools Module", "ERROR", f"Failed to import tools module: {str(e)}")


def check_pipeline():
    """Check that the evaluation pipeline is working."""
    try:
        from core.pipeline import EvaluationPipeline
        from core.runner import ScenarioRunner
        
        # Just check that we can import the classes
        print_status("Pipeline", "OK", "EvaluationPipeline class is available")
        print_status("Runner", "OK", "ScenarioRunner class is available")
    except Exception as e:
        print_status("Pipeline Components", "ERROR", f"Error: {str(e)}")


def check_visualization():
    """Check that visualization components are working."""
    try:
        from visualization.report import generate_report, BenchmarkReport
        from visualization.charts import (
            model_comparison_radar,
            scenario_comparison_heatmap,
            tool_usage_bar_chart
        )
        
        print_status("Visualization", "OK", "Successfully imported visualization components")
    except Exception as e:
        print_status("Visualization", "ERROR", f"Error: {str(e)}")


def check_data_files():
    """Check that data files are present and valid."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if not os.path.exists(data_dir):
        print_status("Data Directory", "ERROR", f"Directory not found: {data_dir}")
        return
    
    # Check for data subdirectories
    expected_dirs = ["knowledge_base", "products", "pricing"]
    missing_dirs = [d for d in expected_dirs if not os.path.exists(os.path.join(data_dir, d))]
    
    if missing_dirs:
        print_status("Data Subdirectories", "WARNING", f"Missing directories: {', '.join(missing_dirs)}")
    else:
        print_status("Data Subdirectories", "OK", f"Found all expected subdirectories")
    
    # Check for key data files
    data_files = {
        "Technical FAQ": os.path.join(data_dir, "knowledge_base", "technical_faq.json"),
        "Product Catalog": os.path.join(data_dir, "products", "enterprise_software.json"),
        "Pricing Data": os.path.join(data_dir, "pricing", "subscription_tiers.json")
    }
    
    for name, filepath in data_files.items():
        if not os.path.exists(filepath):
            print_status(f"Data File: {name}", "ERROR", f"File not found: {filepath}")
            continue
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and data:
                print_status(f"Data File: {name}", "OK", f"Valid JSON with {len(data)} root keys")
            elif isinstance(data, list) and data:
                print_status(f"Data File: {name}", "OK", f"Valid JSON array with {len(data)} items")
            else:
                print_status(f"Data File: {name}", "WARNING", "File exists but has no data")
        except json.JSONDecodeError:
            print_status(f"Data File: {name}", "ERROR", "Invalid JSON format")
        except Exception as e:
            print_status(f"Data File: {name}", "ERROR", f"Error: {str(e)}")


def check_config_files():
    """Check that configuration files are present and valid."""
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    
    if not os.path.exists(config_dir):
        print_status("Config Directory", "ERROR", f"Directory not found: {config_dir}")
        return
    
    # Check for key config files
    config_files = {
        "Models Config": os.path.join(config_dir, "models.yaml"),
        "Evaluation Config": os.path.join(config_dir, "evaluation.yaml")
    }
    
    for name, filepath in config_files.items():
        if not os.path.exists(filepath):
            print_status(f"Config File: {name}", "ERROR", f"File not found: {filepath}")
            continue
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and data:
                print_status(f"Config File: {name}", "OK", f"Valid YAML with {len(data)} root keys")
            else:
                print_status(f"Config File: {name}", "WARNING", "File exists but has no data")
        except yaml.YAMLError:
            print_status(f"Config File: {name}", "ERROR", "Invalid YAML format")
        except Exception as e:
            print_status(f"Config File: {name}", "ERROR", f"Error: {str(e)}")


def main():
    """Run all verification checks."""
    parser = argparse.ArgumentParser(description="Verify bizCon framework components")
    parser.add_argument("--component", "-c", type=str, 
                        choices=["all", "models", "scenarios", "evaluators", "tools", 
                                "pipeline", "visualization", "data", "config"],
                        default="all", help="Component to verify")
    args = parser.parse_args()
    
    print(f"\n{BLUE}bizCon Framework Verification{ENDC}")
    print(f"{BLUE}============================{ENDC}\n")
    
    component = args.component.lower()
    
    if component in ["all", "models"]:
        print(f"\n{BLUE}Checking Models...{ENDC}")
        check_models()
    
    if component in ["all", "scenarios"]:
        print(f"\n{BLUE}Checking Scenarios...{ENDC}")
        check_scenarios()
    
    if component in ["all", "evaluators"]:
        print(f"\n{BLUE}Checking Evaluators...{ENDC}")
        check_evaluators()
    
    if component in ["all", "tools"]:
        print(f"\n{BLUE}Checking Tools...{ENDC}")
        check_tools()
    
    if component in ["all", "pipeline"]:
        print(f"\n{BLUE}Checking Pipeline...{ENDC}")
        check_pipeline()
    
    if component in ["all", "visualization"]:
        print(f"\n{BLUE}Checking Visualization...{ENDC}")
        check_visualization()
    
    if component in ["all", "data"]:
        print(f"\n{BLUE}Checking Data Files...{ENDC}")
        check_data_files()
    
    if component in ["all", "config"]:
        print(f"\n{BLUE}Checking Config Files...{ENDC}")
        check_config_files()
    
    print(f"\n{BLUE}Verification Complete{ENDC}\n")


if __name__ == "__main__":
    main()
