#!/usr/bin/env python3
"""
Script for checking all available scenarios to ensure they are properly defined.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scenarios import _SCENARIO_REGISTRY


def check_scenario(scenario_class, verbose=False):
    """
    Check a specific scenario for completeness.
    
    Args:
        scenario_class: Scenario class to check
        verbose: Whether to print detailed information
    
    Returns:
        Tuple of (scenario_id, status, issues)
    """
    issues = []
    status = "OK"
    
    # Instantiate the scenario
    try:
        scenario_id = next((sid for sid, cls in _SCENARIO_REGISTRY.items() 
                           if cls == scenario_class), "unknown")
        scenario = scenario_class(scenario_id=scenario_id)
    except Exception as e:
        return scenario_class.__name__, "ERROR", [f"Failed to instantiate: {str(e)}"]
    
    # Check basic metadata
    if not scenario.name:
        issues.append("Missing name")
        status = "WARNING"
    
    if not scenario.description:
        issues.append("Missing description")
        status = "WARNING"
    
    if not scenario.industry:
        issues.append("Missing industry")
        status = "WARNING"
    
    # Check conversation flow
    try:
        conversation = scenario.get_conversation()
        if not conversation:
            issues.append("Empty conversation flow")
            status = "ERROR"
        elif len(conversation) < 2:
            issues.append(f"Only {len(conversation)} turns (minimum 2 recommended)")
            status = "WARNING"
            
        # Check conversation structure
        for i, turn in enumerate(conversation):
            if not turn.get("user_message"):
                issues.append(f"Turn {i+1}: Missing user message")
                status = "ERROR"
    except Exception as e:
        issues.append(f"Error accessing conversation flow: {str(e)}")
        status = "ERROR"
    
    # Check ground truth
    try:
        ground_truth = scenario.get_ground_truth()
        if not ground_truth:
            issues.append("Missing ground truth data")
            status = "ERROR"
        else:
            # Check for key ground truth elements
            if "expected_facts" not in ground_truth:
                issues.append("Ground truth missing 'expected_facts'")
                status = "WARNING"
                
            if "required_elements" not in ground_truth:
                issues.append("Ground truth missing 'required_elements'")
                status = "WARNING"
    except Exception as e:
        issues.append(f"Error accessing ground truth: {str(e)}")
        status = "ERROR"
    
    # Check tool requirements
    if not scenario.tools_required:
        issues.append("No tools specified as required")
        status = "WARNING"
    
    # Get initial message
    try:
        initial_message = scenario.get_initial_message()
        if not initial_message or not initial_message.get("content"):
            issues.append("Missing or empty initial message")
            status = "ERROR"
    except Exception as e:
        issues.append(f"Error getting initial message: {str(e)}")
        status = "ERROR"
    
    # Print verbose details if requested
    if verbose:
        print(f"\nScenario: {scenario.name} ({scenario_id})")
        print(f"  Description: {scenario.description}")
        print(f"  Industry: {scenario.industry}")
        print(f"  Complexity: {scenario.complexity}")
        print(f"  Required Tools: {', '.join(scenario.tools_required)}")
        print(f"  Turns: {len(conversation) if conversation else 0}")
        print(f"  Status: {status}")
        
        if issues:
            print("  Issues:")
            for issue in issues:
                print(f"    - {issue}")
    
    return scenario_id, status, issues


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check all available scenarios")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print detailed information for each scenario")
    parser.add_argument("--output", default="output/scenario_check.json",
                        help="Path to save the check results")
    
    args = parser.parse_args()
    
    print("\nChecking all available scenarios...")
    
    # Track statistics
    results = {}
    count_ok = 0
    count_warning = 0
    count_error = 0
    
    # Check each scenario
    for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
        scenario_id, status, issues = check_scenario(scenario_class, args.verbose)
        
        results[scenario_id] = {
            "status": status,
            "issues": issues
        }
        
        if status == "OK":
            count_ok += 1
        elif status == "WARNING":
            count_warning += 1
        elif status == "ERROR":
            count_error += 1
    
    # Print summary
    print("\nSummary:")
    print(f"  Total scenarios: {len(results)}")
    print(f"  OK: {count_ok}")
    print(f"  Warnings: {count_warning}")
    print(f"  Errors: {count_error}")
    
    # Save results to file
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nDetailed results saved to {output_path}")


if __name__ == "__main__":
    main()