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

# Import our modules using relative imports
from models import get_model_client, list_supported_models
from scenarios import _SCENARIO_REGISTRY
from evaluators import get_all_evaluators
from tools import get_default_tools
from core.pipeline import EvaluationPipeline
from core.runner import ScenarioRunner
from tools.base import BusinessTool
from evaluators.base import BaseEvaluator
from visualization.report import generate_report, BenchmarkReport
from visualization.charts import (
    model_comparison_radar,
    scenario_comparison_heatmap, 
    tool_usage_bar_chart,
    performance_trend_line
)

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


def check_scenarios():
    """Check that scenarios are properly implemented."""
    
    # Check scenario registry
    scenario_count = len(_SCENARIO_REGISTRY)
    print_status("Scenario Registry", "INFO", f"Found {scenario_count} registered scenarios")
    
    # Load a few scenarios to verify implementation
    try:
        if _SCENARIO_REGISTRY:
            # Take first 2 scenarios from registry
            scenario_ids = list(_SCENARIO_REGISTRY.keys())[:2]
            
            # Instantiate scenarios
            scenarios = []
            for scenario_id in scenario_ids:
                scenario_class = _SCENARIO_REGISTRY[scenario_id]
                scenarios.append(scenario_class(scenario_id=scenario_id))
            
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
        print_status("Scenario Loading", "ERROR", f"Error: {str(e)}")


def check_tools():
    """Check that business tools are properly implemented."""
    # Import all tool modules
    tool_modules = {}
    
    tools_dir = Path(__file__).parent / "tools"
    for file_path in tools_dir.glob("*.py"):
        if file_path.name == "__init__.py" or file_path.name == "base.py":
            continue
            
        module_name = f"bizcon.tools.{file_path.stem}"
        try:
            module = importlib.import_module(module_name)
            tool_modules[module_name] = module
        except Exception as e:
            print_status(f"Tool Module: {module_name}", "ERROR", f"Import error: {str(e)}")
    
    # Find all tool classes
    tool_classes = []
    for module_name, module in tool_modules.items():
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BusinessTool) and 
                obj != BusinessTool):
                tool_classes.append(obj)
    
    print_status("Business Tools", "INFO", f"Found {len(tool_classes)} tool implementations")
    
    # Instantiate and test a sample tool
    if tool_classes:
        try:
            test_tool = tool_classes[0]()
            definition = test_tool.get_definition()
            
            if definition and "function" in definition:
                print_status(f"Tool: {test_tool.name}", "OK", "Implementation verified")
            else:
                print_status(f"Tool: {test_tool.name}", "WARNING", "Definition format may be incorrect")
                
        except Exception as e:
            print_status("Tool Instantiation", "ERROR", f"Implementation error: {str(e)}")


def check_evaluators():
    """Check that evaluators are properly implemented."""
    
    # Import all evaluator modules
    evaluator_modules = {}
    evaluators_dir = Path(__file__).parent / "evaluators"
    
    for file_path in evaluators_dir.glob("*.py"):
        if file_path.name == "__init__.py" or file_path.name == "base.py":
            continue
            
        module_name = f"bizcon.evaluators.{file_path.stem}"
        try:
            module = importlib.import_module(module_name)
            evaluator_modules[module_name] = module
        except Exception as e:
            print_status(f"Evaluator Module: {module_name}", "ERROR", f"Import error: {str(e)}")
    
    # Find all evaluator classes
    evaluator_classes = []
    for module_name, module in evaluator_modules.items():
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseEvaluator) and 
                obj != BaseEvaluator):
                evaluator_classes.append(obj)
    
    print_status("Evaluators", "INFO", f"Found {len(evaluator_classes)} evaluator implementations")
    
    # Check required evaluators
    required_evaluators = [
        "ResponseQualityEvaluator", 
        "CommunicationStyleEvaluator",
        "ToolUsageEvaluator", 
        "BusinessValueEvaluator", 
        "PerformanceEvaluator"
    ]
    
    found_evaluators = [cls.__name__ for cls in evaluator_classes]
    missing_evaluators = [req for req in required_evaluators if req not in found_evaluators]
    
    if missing_evaluators:
        print_status("Required Evaluators", "WARNING", f"Missing: {', '.join(missing_evaluators)}")
    else:
        print_status("Required Evaluators", "OK", "All required evaluators implemented")


def check_pipeline():
    """Check that the evaluation pipeline is properly implemented."""
    try:
        from bizcon.core.pipeline import EvaluationPipeline
        from bizcon.core.runner import ScenarioRunner
        
        # Check required methods in pipeline
        required_methods = ["run", "generate_report", "_calculate_summary"]
        missing_methods = []
        
        for method_name in required_methods:
            if not hasattr(EvaluationPipeline, method_name):
                missing_methods.append(method_name)
        
        if missing_methods:
            print_status("Evaluation Pipeline", "WARNING", 
                         f"Missing methods: {', '.join(missing_methods)}")
        else:
            print_status("Evaluation Pipeline", "OK", "Core pipeline implementation verified")
            
        # Check runner implementation
        required_runner_methods = ["run", "_generate_response", "_process_tool_calls"]
        missing_runner_methods = []
        
        for method_name in required_runner_methods:
            if not hasattr(ScenarioRunner, method_name):
                missing_runner_methods.append(method_name)
        
        if missing_runner_methods:
            print_status("Scenario Runner", "WARNING", 
                         f"Missing methods: {', '.join(missing_runner_methods)}")
        else:
            print_status("Scenario Runner", "OK", "Core runner implementation verified")
            
    except ImportError as e:
        print_status("Core Pipeline", "ERROR", f"Import error: {str(e)}")
    except Exception as e:
        print_status("Core Pipeline", "ERROR", f"Verification error: {str(e)}")


def check_visualization():
    """Check that visualization components are properly implemented."""
    try:
        from bizcon.visualization.report import generate_report, BenchmarkReport
        
        # Check required chart functions
        from bizcon.visualization.charts import (
            model_comparison_radar,
            scenario_comparison_heatmap,
            tool_usage_bar_chart,
            performance_trend_line
        )
        
        print_status("Visualization", "OK", "Core visualization components verified")
        
    except ImportError as e:
        print_status("Visualization", "ERROR", f"Import error: {str(e)}")
    except Exception as e:
        print_status("Visualization", "ERROR", f"Verification error: {str(e)}")


def check_data_files():
    """Check that data files are properly set up."""
    data_dir = Path(__file__).parent / "data"
    
    # Check required data directories
    required_dirs = ["knowledge_base", "products", "pricing"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not (data_dir / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print_status("Data Directories", "WARNING", f"Missing: {', '.join(missing_dirs)}")
    else:
        print_status("Data Directories", "OK", "All required data directories exist")
    
    # Check for data files
    data_files = []
    for ext in ['.json', '.yaml', '.csv']:
        data_files.extend(list(data_dir.glob(f"**/*{ext}")))
    
    if data_files:
        print_status("Data Files", "INFO", f"Found {len(data_files)} data files")
        
        # Validate a sample JSON file
        for file_path in data_files:
            if file_path.suffix == '.json':
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    print_status(f"JSON File: {file_path.name}", "OK", "Valid JSON format")
                    break
                except json.JSONDecodeError:
                    print_status(f"JSON File: {file_path.name}", "ERROR", "Invalid JSON format")
                except Exception as e:
                    print_status(f"JSON File: {file_path.name}", "ERROR", f"Error reading file: {str(e)}")
    else:
        print_status("Data Files", "WARNING", "No data files found")


def main():
    """Run verification checks."""
    parser = argparse.ArgumentParser(description="Verify bizCon framework components")
    parser.add_argument("--component", choices=["all", "models", "scenarios", "tools", 
                                              "evaluators", "pipeline", "visualization", "data"],
                      default="all", help="Component to verify")
    
    args = parser.parse_args()
    
    print(f"\n{BLUE}=== bizCon Framework Verification ==={ENDC}\n")
    
    # Run checks based on selected component
    if args.component in ["all", "models"]:
        print(f"\n{BLUE}Checking Models...{ENDC}")
        check_models()
        
    if args.component in ["all", "scenarios"]:
        print(f"\n{BLUE}Checking Scenarios...{ENDC}")
        check_scenarios()
        
    if args.component in ["all", "tools"]:
        print(f"\n{BLUE}Checking Business Tools...{ENDC}")
        check_tools()
        
    if args.component in ["all", "evaluators"]:
        print(f"\n{BLUE}Checking Evaluators...{ENDC}")
        check_evaluators()
        
    if args.component in ["all", "pipeline"]:
        print(f"\n{BLUE}Checking Pipeline...{ENDC}")
        check_pipeline()
        
    if args.component in ["all", "visualization"]:
        print(f"\n{BLUE}Checking Visualization...{ENDC}")
        check_visualization()
        
    if args.component in ["all", "data"]:
        print(f"\n{BLUE}Checking Data Files...{ENDC}")
        check_data_files()
        
    print(f"\n{BLUE}Verification Complete{ENDC}\n")


if __name__ == "__main__":
    main()
