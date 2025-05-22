"""
Appointment scheduling business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os
import datetime

from .base import BusinessScenario


class StandardAppointmentScheduling(BusinessScenario):
    """
    Standard appointment scheduling scenario.
    
    Tests how well the model handles appointment scheduling requests,
    requiring the use of the scheduler tool and handling follow-up questions.
    """
    
    def __init__(self, scenario_id: str = "appointment_001"):
        """
        Initialize the standard appointment scheduling scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Standard Appointment Scheduling",
            description="Customer requesting to schedule a product demo with a sales representative",
            industry="General",
            complexity="simple",
            tools_required=["scheduler", "product_catalog"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        # Calculate next Tuesday for demo scheduling
        today = datetime.datetime.now()
        days_until_next_tuesday = (1 - today.weekday()) % 7 + 1
        next_tuesday = today + datetime.timedelta(days=days_until_next_tuesday)
        next_tuesday_str = next_tuesday.strftime("%Y-%m-%d")
        
        return [
            {
                "user_message": "Hi, I'd like to schedule a demo for your project management software. I'm looking to understand how it might help our marketing team coordinate campaigns better.",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_category": "project_management",
                            "use_case": "marketing"
                        }
                    }
                ]
            },
            {
                "user_message": f"Thanks for the information. That sounds like it would work for us. Could we schedule a demo next Tuesday afternoon? We'd like to have someone who understands marketing use cases specifically.",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "product_demo",
                            "product_id": "project_management_pro",
                            "date": next_tuesday_str,
                            "time_range": "13:00-17:00",
                            "participants": ["sales_rep", "technical_specialist"],
                            "industry": "marketing"
                        }
                    }
                ]
            },
            {
                "user_message": "The 2:30 PM slot works for us. There will be 4 people from our team attending. Can we make it a 90-minute session instead of 60 minutes? And will this be a virtual meeting or in-person?",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "product_demo",
                            "product_id": "project_management_pro",
                            "date": next_tuesday_str,
                            "time_range": "14:30-16:00",
                            "duration": 90,
                            "participants": ["sales_rep", "technical_specialist"],
                            "industry": "marketing",
                            "book": True
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "product_information": {
                "name": "ProjectFlow Pro",
                "category": "project_management",
                "key_features": [
                    "Campaign timeline visualization",
                    "Resource allocation tracking",
                    "Automated task dependencies",
                    "Marketing-specific templates",
                    "Collaboration tools",
                    "Performance analytics"
                ]
            },
            "scheduling_information": {
                "available_meeting_types": [
                    "product_demo",
                    "sales_consultation",
                    "technical_discussion"
                ],
                "session_durations": [30, 60, 90, 120],
                "default_duration": 60,
                "meeting_format": "Virtual (Zoom or Microsoft Teams)",
                "scheduling_notice": "24 hours minimum",
                "availability": "Monday-Friday, 9:00 AM - 5:00 PM EST"
            },
            "expected_responses": {
                "should_confirm_details": True,
                "should_mention_preparation": True,
                "should_offer_calendar_invite": True,
                "should_provide_contact_info": True
            }
        }


class ComplexSchedulingScenario(BusinessScenario):
    """
    Complex appointment scheduling scenario.
    
    Tests how well the model handles complex scheduling situations with
    constraints, conflicts, and multiple participants across departments.
    """
    
    def __init__(self, scenario_id: str = "appointment_002"):
        """
        Initialize the complex scheduling scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Multi-Department Implementation Planning",
            description="Enterprise customer scheduling an implementation planning meeting requiring multiple departments",
            industry="Manufacturing",
            complexity="complex",
            tools_required=["scheduler", "knowledge_base"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "We're getting ready to implement your ERP system across our manufacturing plants. We need to schedule a planning session with your implementation team, including technical specialists and training staff. What's the best way to coordinate this?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "ERP implementation planning manufacturing",
                            "categories": ["implementation", "planning", "manufacturing"]
                        }
                    }
                ]
            },
            {
                "user_message": "Great. We'd like to have our IT director, operations manager, and plant supervisors in the meeting. We'd need representatives from your technical team, training department, and a project manager who has experience with manufacturing implementations. We're looking at the week of August 15th, 2025. What availability do you have?",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "implementation_planning",
                            "product_id": "erp_manufacturing",
                            "date": "2025-08-15",
                            "duration": 120,
                            "participants": ["technical_specialist", "support_specialist", "implementation_manager"],
                            "industry": "manufacturing"
                        }
                    }
                ]
            },
            {
                "user_message": "None of those times work for our team. Could we look at the following week instead? Preferably in the morning as our plant supervisors have shift changes in the afternoon.",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "implementation_planning",
                            "product_id": "erp_manufacturing",
                            "date": "2025-08-22",
                            "time_range": "08:00-12:00",
                            "duration": 120,
                            "participants": ["technical_specialist", "support_specialist", "implementation_manager"],
                            "industry": "manufacturing"
                        }
                    }
                ]
            },
            {
                "user_message": "The Tuesday slot at 9:00 AM works perfectly. Let's book that. Also, we'll need to cover data migration from our legacy system. Will someone with expertise in that area be present?",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "implementation_planning",
                            "product_id": "erp_manufacturing",
                            "date": "2025-08-26",
                            "time_range": "09:00-11:00",
                            "duration": 120,
                            "participants": ["technical_specialist", "support_specialist", "implementation_manager", "data_migration_specialist"],
                            "industry": "manufacturing",
                            "book": True
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "implementation_process": {
                "phases": [
                    "Planning and Requirements Gathering",
                    "System Configuration",
                    "Data Migration",
                    "Testing",
                    "Training",
                    "Go-Live Support"
                ],
                "planning_meeting_objectives": [
                    "Establish project timeline",
                    "Identify key stakeholders",
                    "Define success criteria",
                    "Assess technical requirements",
                    "Develop training strategy",
                    "Establish data migration plan"
                ],
                "typical_duration": "8-12 weeks for manufacturing implementation"
            },
            "meeting_requirements": {
                "key_personnel_vendor": [
                    "Implementation Project Manager",
                    "Technical Implementation Specialist",
                    "Data Migration Expert",
                    "Training Coordinator",
                    "Manufacturing Industry Consultant"
                ],
                "key_personnel_client": [
                    "IT Director/Manager",
                    "Operations Manager",
                    "Plant Supervisors",
                    "System End Users Representatives",
                    "Executive Sponsor"
                ],
                "recommended_preparation": [
                    "Current process documentation",
                    "Legacy system information",
                    "Organizational chart",
                    "Implementation timeline constraints",
                    "Training facility information"
                ]
            },
            "expected_responses": {
                "should_acknowledge_constraints": True,
                "should_confirm_specialist_availability": True,
                "should_offer_pre_meeting_materials": True,
                "should_suggest_preparation_steps": True,
                "should_explain_meeting_structure": True
            }
        }