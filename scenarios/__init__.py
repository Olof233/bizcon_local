"""
Scenarios package for bizCon framework.
"""
from typing import Dict, List, Any, Optional, Union
import importlib
import inspect
import os
import glob
import sys

# Use relative imports instead of bizcon package imports
from .base import BusinessScenario
from .product_inquiry import EnterpriseProductInquiry, ProductCustomizationInquiry
from .appointment_scheduling import StandardAppointmentScheduling, ComplexSchedulingScenario
from .technical_support import StandardTechnicalSupport, ComplexIntegrationSupport
from .contract_negotiation import StandardContractNegotiation, EnterpriseAgreementNegotiation
from .compliance_inquiry import RegulatoryComplianceInquiry, DataPrivacyComplianceScenario
from .implementation_planning import EnterpriseImplementationPlanning, MidMarketImplementationPlanning
from .service_complaints import HighValueCustomerComplaint, ServiceFailureComplaint, BillingDisputeScenario
from .multi_department import CrossFunctionalProjectScenario, EnterpriseProductLaunchScenario, CrossDepartmentCollaborationScenario


# Dictionary of scenario ID to scenario class
_SCENARIO_REGISTRY = {
    # Product inquiry
    "product_inquiry_001": EnterpriseProductInquiry,
    "product_inquiry_002": ProductCustomizationInquiry,
    # Appointment scheduling
    "appointment_001": StandardAppointmentScheduling,
    "appointment_002": ComplexSchedulingScenario,
    # Technical support
    "support_001": StandardTechnicalSupport,
    "support_002": ComplexIntegrationSupport,
    # Contract negotiation
    "contract_001": StandardContractNegotiation,
    "contract_002": EnterpriseAgreementNegotiation,
    # Compliance inquiry
    "compliance_001": RegulatoryComplianceInquiry,
    "compliance_002": DataPrivacyComplianceScenario,
    # Implementation planning
    "implementation_001": EnterpriseImplementationPlanning,
    "implementation_002": MidMarketImplementationPlanning,
    # Service complaints
    "complaints_001": HighValueCustomerComplaint,
    "complaints_002": ServiceFailureComplaint,
    "complaints_003": BillingDisputeScenario,
    # Multi-department
    "multi_dept_001": CrossFunctionalProjectScenario,
    "multi_dept_002": EnterpriseProductLaunchScenario,
    "multi_dept_003": CrossDepartmentCollaborationScenario,
}


def register_scenario(scenario_id: str, scenario_class: type) -> None:
    """
    Register a new scenario class.
    
    Args:
        scenario_id: Unique identifier for the scenario
        scenario_class: Scenario class to register
    """
    _SCENARIO_REGISTRY[scenario_id] = scenario_class


def get_scenario_class(scenario_id: str) -> Optional[type]:
    """
    Get a scenario class by ID.
    
    Args:
        scenario_id: Scenario ID
        
    Returns:
        Scenario class or None if not found
    """
    return _SCENARIO_REGISTRY.get(scenario_id)


def load_scenarios(scenario_ids: Union[str, List[str]]) -> List[BusinessScenario]:
    """
    Load scenarios by ID.
    
    Args:
        scenario_ids: Single scenario ID or list of scenario IDs
        
    Returns:
        List of initialized scenario objects
    """
    if isinstance(scenario_ids, str):
        scenario_ids = [scenario_ids]
    
    scenarios = []
    for scenario_id in scenario_ids:
        scenario_class = get_scenario_class(scenario_id)
        if scenario_class:
            scenarios.append(scenario_class(scenario_id=scenario_id))
    
    return scenarios


def discover_scenarios() -> None:
    """
    Discover and register all scenario classes in the scenarios package.
    """
    # Get the directory of the scenarios package
    scenarios_dir = os.path.dirname(__file__)
    
    # Find all Python files in the package
    python_files = glob.glob(os.path.join(scenarios_dir, "*.py"))
    
    # Import each module
    for file_path in python_files:
        if os.path.basename(file_path) == "__init__.py":
            continue
        
        module_name = os.path.basename(file_path)[:-3]  # Remove .py extension
        module_path = f"bizcon.scenarios.{module_name}"
        
        try:
            module = importlib.import_module(module_path)
            
            # Find all BusinessScenario subclasses in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BusinessScenario) and 
                    obj != BusinessScenario):
                    
                    # Create an instance to get the scenario ID
                    instance = obj()
                    scenario_id = instance.scenario_id
                    
                    # Register the scenario
                    register_scenario(scenario_id, obj)
        
        except Exception as e:
            print(f"Error loading scenarios from {module_path}: {e}", file=sys.stderr)


def list_available_scenarios() -> Dict[str, Dict[str, Any]]:
    """
    List all available scenarios.
    
    Returns:
        Dictionary mapping scenario IDs to metadata
    """
    # Ensure all scenarios are discovered
    discover_scenarios()
    
    result = {}
    for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
        # Create an instance to get metadata
        instance = scenario_class(scenario_id=scenario_id)
        result[scenario_id] = instance.get_metadata()
    
    return result


# Discover scenarios when the module is imported
discover_scenarios()

# Main section for validation when run directly
if __name__ == "__main__":
    print("Validating scenario implementations...")
    all_scenarios = list_available_scenarios()
    print(f"Found {len(all_scenarios)} registered scenarios:")
    for scenario_id, metadata in all_scenarios.items():
        print(f"  - {scenario_id}: {metadata['name']}")
    
    # Verify our new implementations specifically
    expected_new_scenarios = [
        "implementation_001", "implementation_002",
        "complaints_001", "complaints_002", "complaints_003",
        "multi_dept_001", "multi_dept_002", "multi_dept_003"
    ]
    
    print("\nVerifying newly implemented scenarios:")
    missing = []
    for scenario_id in expected_new_scenarios:
        if scenario_id in all_scenarios:
            print(f"  ✓ {scenario_id} ({all_scenarios[scenario_id]['name']}) is registered")
        else:
            missing.append(scenario_id)
            print(f"  ✗ {scenario_id} is missing")
    
    if missing:
        print(f"\nFailed: {len(missing)} scenarios are missing")
    else:
        print("\nSuccess: All expected scenarios are registered!")