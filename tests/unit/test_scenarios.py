"""
Unit tests for scenario classes.
"""
import unittest
import sys
import os
import inspect
from typing import List, Type

# Add the parent directory to the Python path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from bizcon.scenarios.base import BusinessScenario
from bizcon.scenarios import _SCENARIO_REGISTRY
from bizcon.scenarios.multi_department import EnterpriseProductLaunchScenario, CrossFunctionalProjectScenario, CrossDepartmentCollaborationScenario


class TestScenarios(unittest.TestCase):
    """Tests for the scenario classes."""

    def test_basic(self):
        """Basic test to check if unittest is working."""
        self.assertTrue(True)
    
    def test_all_scenario_classes_instantiate(self):
        """Test that all scenario classes can be instantiated."""
        for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
            try:
                instance = scenario_class(scenario_id=scenario_id)
                self.assertIsInstance(instance, BusinessScenario, 
                                     f"{scenario_class.__name__} should be an instance of BusinessScenario")
            except Exception as e:
                self.fail(f"Failed to instantiate {scenario_class.__name__}: {e}")
    
    def test_required_methods_implemented(self):
        """Test that all scenario classes implement the required methods."""
        required_methods = [
            '_initialize_conversation',
            '_initialize_ground_truth',
        ]
        
        for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
            for method_name in required_methods:
                method = getattr(scenario_class, method_name, None)
                self.assertIsNotNone(method, 
                                    f"{scenario_class.__name__} is missing required method: {method_name}")
                self.assertTrue(inspect.isfunction(method), 
                               f"{method_name} in {scenario_class.__name__} is not a function")
    
    def test_conversation_structure(self):
        """Test that all scenario conversations have the expected structure."""
        for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
            instance = scenario_class(scenario_id=scenario_id)
            conversation = instance.get_conversation()
            
            self.assertIsInstance(conversation, list, 
                                 f"Conversation for {scenario_class.__name__} should be a list")
            
            for i, turn in enumerate(conversation):
                self.assertIn("user_message", turn, 
                             f"Turn {i} in {scenario_class.__name__} missing 'user_message'")
                self.assertIsInstance(turn["user_message"], str, 
                                    f"'user_message' in turn {i} of {scenario_class.__name__} should be a string")
                
                if "expected_tool_calls" in turn:
                    self.assertIsInstance(turn["expected_tool_calls"], list, 
                                         f"'expected_tool_calls' in turn {i} of {scenario_class.__name__} should be a list")
                    
                    for j, tool_call in enumerate(turn["expected_tool_calls"]):
                        self.assertIn("tool_id", tool_call, 
                                     f"Tool call {j} in turn {i} of {scenario_class.__name__} missing 'tool_id'")
                        self.assertIn("parameters", tool_call, 
                                     f"Tool call {j} in turn {i} of {scenario_class.__name__} missing 'parameters'")
    
    def test_ground_truth_exists(self):
        """Test that all scenarios have ground truth data."""
        for scenario_id, scenario_class in _SCENARIO_REGISTRY.items():
            instance = scenario_class(scenario_id=scenario_id)
            ground_truth = instance.get_ground_truth()
            
            self.assertIsNotNone(ground_truth, 
                                f"Ground truth for {scenario_class.__name__} should not be None")
            self.assertTrue(ground_truth, 
                           f"Ground truth for {scenario_class.__name__} should not be empty")
    
    def test_multi_department_scenarios(self):
        """Test specific multi_department scenarios that were implemented."""
        # Test CrossFunctionalProjectScenario
        scenario = CrossFunctionalProjectScenario()
        self.assertIsInstance(scenario, BusinessScenario)
        
        # Get conversation and check structure
        conversation = scenario.get_conversation()
        self.assertIsInstance(conversation, list)
        self.assertTrue(len(conversation) > 0)
        
        # Get ground truth and check it's not empty
        ground_truth = scenario.get_ground_truth()
        self.assertIsInstance(ground_truth, dict)
        self.assertTrue(len(ground_truth) > 0)
        
        # Test EnterpriseProductLaunchScenario - this was fixed in our implementation
        scenario = EnterpriseProductLaunchScenario()
        self.assertIsInstance(scenario, BusinessScenario)
        
        # Get conversation and check structure - this should use the _initialize_conversation method we fixed
        conversation = scenario.get_conversation()
        self.assertIsInstance(conversation, list)
        self.assertTrue(len(conversation) > 0)
        
        # Verify the _initialize_conversation method specifically
        initialize_conversation_method = getattr(EnterpriseProductLaunchScenario, '_initialize_conversation')
        self.assertIsNotNone(initialize_conversation_method)
        
        # Call the method directly to verify it works
        conversation_data = initialize_conversation_method(scenario)
        self.assertIsInstance(conversation_data, list)
        self.assertTrue(len(conversation_data) > 0)
        
        # Get ground truth and check it's not empty
        ground_truth = scenario.get_ground_truth()
        self.assertIsInstance(ground_truth, dict)
        self.assertTrue(len(ground_truth) > 0)
        
        # Test CrossDepartmentCollaborationScenario
        scenario = CrossDepartmentCollaborationScenario()
        self.assertIsInstance(scenario, BusinessScenario)
        
        # Get conversation and check structure
        conversation = scenario.get_conversation()
        self.assertIsInstance(conversation, list)
        self.assertTrue(len(conversation) > 0)
        
        # Get ground truth and check it's not empty
        ground_truth = scenario.get_ground_truth()
        self.assertIsInstance(ground_truth, dict)
        self.assertTrue(len(ground_truth) > 0)


if __name__ == "__main__":
    unittest.main()