"""
Implementation planning business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class EnterpriseImplementationPlanning(BusinessScenario):
    """
    Enterprise implementation planning scenario.
    
    Tests how well the model handles complex project planning discussions
    for enterprise software implementation, requiring technical knowledge,
    project management skills, and business acumen.
    """
    
    def __init__(self, scenario_id: str = "implementation_001"):
        """
        Initialize the enterprise implementation planning scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Enterprise Software Implementation Planning",
            description="Enterprise customer planning a complex software implementation across multiple departments",
            industry="Manufacturing",
            complexity="complex",
            tools_required=["document_retrieval", "product_catalog", "pricing_calculator"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "We're planning to implement your ERP system across our manufacturing operations in North America. Our team has reviewed the product documentation, but we need help creating a phased implementation plan that minimizes disruption to our production lines. Can you help us plan this out?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "implementation_guide",
                            "keywords": ["manufacturing", "ERP", "phased implementation", "production"]
                        }
                    }
                ]
            },
            {
                "user_message": "We have 8 manufacturing facilities and about 2,500 users who will need access to the system. Our IT infrastructure is primarily on-premise, but we're open to cloud-based solutions if they offer advantages. Our primary concerns are integration with our existing MES systems and ensuring minimal downtime during the transition.",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_type": "ERP",
                            "industry": "Manufacturing",
                            "deployment_options": ["on-premise", "cloud"],
                            "integration_capabilities": ["MES"]
                        }
                    }
                ]
            },
            {
                "user_message": "Based on your recommendation of a hybrid approach, we'd like to understand the licensing and cost structure. We'd need full access for 500 power users, limited dashboard access for 1,500 operational staff, and mobile app access for 500 field technicians. What would the implementation and annual costs look like?",
                "expected_tool_calls": [
                    {
                        "tool_id": "pricing_calculator",
                        "parameters": {
                            "product_name": "Enterprise ERP Suite",
                            "deployment_type": "hybrid",
                            "users": {
                                "power_users": 500,
                                "dashboard_users": 1500,
                                "mobile_users": 500
                            },
                            "modules": ["manufacturing", "inventory", "quality", "maintenance", "analytics"],
                            "term_length": "annual"
                        }
                    }
                ]
            },
            {
                "user_message": "That's helpful. Now let's talk about the implementation timeline. We'd like to start with a pilot at our smallest facility in Q3, then roll out to three more facilities in Q4, and complete the remaining facilities by the end of Q1 next year. Is this timeline realistic, and what resources would we need to allocate from our side?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "implementation_timeline",
                            "keywords": ["manufacturing", "ERP", "phased rollout", "resource requirements", "pilot"]
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
            "implementation_approach": {
                "recommended_strategy": "Phased hybrid deployment",
                "phases": [
                    {
                        "name": "Assessment & Planning",
                        "duration": "6-8 weeks",
                        "key_activities": [
                            "Business process mapping",
                            "Gap analysis",
                            "Infrastructure assessment",
                            "Data migration planning",
                            "Integration requirements documentation"
                        ]
                    },
                    {
                        "name": "Pilot Implementation",
                        "duration": "10-12 weeks",
                        "key_activities": [
                            "Core system configuration",
                            "Integration development",
                            "User acceptance testing",
                            "Training program development",
                            "Pilot deployment at smallest facility"
                        ]
                    },
                    {
                        "name": "Phase 1 Rollout",
                        "duration": "12-14 weeks",
                        "key_activities": [
                            "Pilot learnings incorporation",
                            "Deployment to 3 mid-sized facilities",
                            "Data migration execution",
                            "User training execution",
                            "Go-live support"
                        ]
                    },
                    {
                        "name": "Phase 2 Rollout",
                        "duration": "16-20 weeks",
                        "key_activities": [
                            "Deployment to remaining 4 facilities",
                            "Advanced features activation",
                            "Cross-facility reporting implementation",
                            "System optimization",
                            "Transition to support"
                        ]
                    }
                ]
            },
            "deployment_options": {
                "hybrid_approach": {
                    "core_components": "On-premise for critical manufacturing operations",
                    "cloud_components": "Reporting, analytics, and mobile access",
                    "advantages": [
                        "Lower latency for production-critical functions",
                        "Data residency compliance",
                        "Flexible scaling for reporting and analytics",
                        "Enhanced disaster recovery capabilities"
                    ]
                },
                "full_cloud": {
                    "advantages": [
                        "Faster implementation timeline",
                        "Reduced infrastructure management",
                        "Automatic updates and patches",
                        "Lower upfront capital expenditure"
                    ],
                    "considerations": [
                        "Higher bandwidth requirements",
                        "Potential latency concerns for real-time operations",
                        "Data residency and compliance challenges",
                        "Long-term total cost of ownership"
                    ]
                },
                "full_on_premise": {
                    "advantages": [
                        "Maximum control over infrastructure",
                        "No internet dependency for operations",
                        "Potentially lower long-term costs for large deployments",
                        "Customized security controls"
                    ],
                    "considerations": [
                        "Higher upfront investment",
                        "Longer implementation timeline",
                        "Internal IT resource requirements",
                        "Manual update management"
                    ]
                }
            },
            "integration_requirements": {
                "mes_integration": {
                    "complexity": "Medium to High",
                    "approach": "API-based with middleware for legacy systems",
                    "standard_connectors": [
                        "SAP Manufacturing Integration",
                        "GE Proficy",
                        "Siemens SIMATIC IT",
                        "Rockwell FactoryTalk"
                    ],
                    "data_flow": "Bi-directional with near real-time synchronization",
                    "implementation_time": "6-8 weeks per integration point"
                },
                "other_systems": {
                    "plm_integration": "Medium complexity, standard connectors available",
                    "quality_management": "Low complexity, built-in integration",
                    "warehouse_management": "Medium complexity, may require customization",
                    "financial_systems": "Medium complexity, standard connectors with customization"
                }
            },
            "resource_requirements": {
                "customer_resources": {
                    "executive_sponsor": "5% time allocation throughout project",
                    "project_manager": "100% dedicated throughout implementation",
                    "business_analysts": "2-3 resources, 75% allocation during assessment and testing",
                    "it_infrastructure": "2 resources, 50% allocation throughout project",
                    "it_integration": "1-2 resources, 75% allocation during integration phases",
                    "power_users": "1-2 per department, 50% allocation during testing and training",
                    "training_coordination": "1 resource, 50% allocation during training phases"
                },
                "vendor_resources": {
                    "implementation_manager": "100% dedicated throughout project",
                    "solution_architects": "2 resources, 100% during design, 50% during implementation",
                    "technical_consultants": "2-4 resources depending on phase",
                    "integration_specialists": "1-2 resources during integration phases",
                    "training_specialists": "1-2 resources during training phases",
                    "go_live_support": "3-5 resources during go-live periods"
                }
            },
            "pricing_structure": {
                "software_licensing": {
                    "power_user_license": "$2,500 per user annually",
                    "operational_dashboard_license": "$800 per user annually",
                    "mobile_user_license": "$1,200 per user annually",
                    "volume_discounts": {
                        "tier_1": "1-500 users: 0%",
                        "tier_2": "501-1000 users: 10%",
                        "tier_3": "1001-2000 users: 15%",
                        "tier_4": "2001+ users: 20%"
                    }
                },
                "implementation_services": {
                    "implementation_base_fee": "$350,000",
                    "per_facility_cost": "$75,000",
                    "integration_development": {
                        "standard_connector": "$25,000 per connector",
                        "custom_integration": "$40,000-$100,000 depending on complexity"
                    },
                    "training_services": {
                        "train_the_trainer": "$30,000 for program development",
                        "end_user_training": "$400 per user"
                    }
                },
                "infrastructure": {
                    "on_premise_components": "Customer responsible for hardware and infrastructure",
                    "cloud_components": {
                        "base_platform_fee": "$15,000 monthly",
                        "data_storage": "$0.20 per GB per month",
                        "transaction_volume": "Included up to 10M transactions monthly"
                    }
                },
                "ongoing_costs": {
                    "annual_maintenance": "22% of license costs",
                    "support_tiers": {
                        "standard": "Included in maintenance",
                        "premium": "Additional 5% of license costs",
                        "platinum": "Additional 10% of license costs"
                    },
                    "managed_services_options": {
                        "basic_monitoring": "$8,000 monthly",
                        "full_administration": "$22,000 monthly",
                        "continuous_optimization": "$35,000 monthly"
                    }
                }
            },
            "risk_mitigation": {
                "common_challenges": [
                    "Data migration quality issues",
                    "User adoption resistance",
                    "Integration complexity underestimation",
                    "Business process standardization across facilities",
                    "Production disruption during cutover"
                ],
                "recommended_controls": {
                    "data_migration": "Multiple test migrations with quality validation",
                    "user_adoption": "Early stakeholder engagement and champion program",
                    "integration": "Phased integration approach with thorough testing",
                    "process_standardization": "Pre-implementation process harmonization workshops",
                    "production_disruption": "Weekend cutover with fallback procedures"
                },
                "contingency_planning": {
                    "rollback_procedures": "Documented for each phase and facility",
                    "parallel_operations": "Recommended for 2 weeks post go-live",
                    "extended_support": "24/7 support during cutover periods",
                    "escalation_process": "Tiered response protocol with executive visibility"
                }
            }
        }


class MidMarketImplementationPlanning(BusinessScenario):
    """
    Mid-market implementation planning scenario.
    
    Tests how well the model handles implementation planning for mid-sized
    businesses with more constrained resources and different requirements.
    """
    
    def __init__(self, scenario_id: str = "implementation_002"):
        """
        Initialize the mid-market implementation planning scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Mid-Market Software Implementation Planning",
            description="Mid-sized business planning a focused software implementation with limited resources",
            industry="Professional Services",
            complexity="medium",
            tools_required=["document_retrieval", "product_catalog", "pricing_calculator"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Our consulting firm is looking to implement your project management and resource planning software. We have about 120 employees, mostly consultants, and we need better visibility into project profitability and resource utilization. What would be the best approach for a company our size?",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_type": "Project Management",
                            "industry": "Professional Services",
                            "company_size": "mid-market",
                            "key_features": ["resource planning", "project profitability", "utilization tracking"]
                        }
                    }
                ]
            },
            {
                "user_message": "The Professional Services Automation suite sounds ideal. We're currently using QuickBooks for accounting, Salesforce for CRM, and a mix of Excel and Microsoft Project for project management. Would we be able to integrate with these systems? Also, we'd prefer a cloud-based solution for easier access from client sites.",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "integration_guide",
                            "keywords": ["Professional Services Automation", "QuickBooks", "Salesforce", "Microsoft Project", "cloud"]
                        }
                    }
                ]
            },
            {
                "user_message": "Great, those integrations would work for us. In terms of pricing, we'd need 20 administrative users (partners and project managers), 80 standard users (consultants), and 20 limited users (administrative staff). What would the licensing and implementation costs look like?",
                "expected_tool_calls": [
                    {
                        "tool_id": "pricing_calculator",
                        "parameters": {
                            "product_name": "Professional Services Automation Suite",
                            "deployment_type": "cloud",
                            "users": {
                                "administrative_users": 20,
                                "standard_users": 80,
                                "limited_users": 20
                            },
                            "integrations": ["QuickBooks", "Salesforce"],
                            "term_length": "annual"
                        }
                    }
                ]
            },
            {
                "user_message": "That pricing works for our budget. How long would the implementation take, and what kind of resources would we need to commit from our side? We have a small IT team of just 3 people, and they're already stretched thin with other projects.",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "implementation_guide",
                            "keywords": ["Professional Services Automation", "implementation timeline", "resource requirements", "small IT team"]
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
            "recommended_solution": {
                "product": "Professional Services Automation Suite",
                "edition": "Business Edition",
                "deployment": "Cloud-based SaaS",
                "core_modules": [
                    "Project Management",
                    "Resource Planning",
                    "Time & Expense Tracking",
                    "Project Accounting",
                    "Client Portal",
                    "Analytics & Reporting"
                ],
                "optional_modules": [
                    "Advanced Revenue Recognition",
                    "Skills Management",
                    "Scenario Planning",
                    "Mobile App Pro"
                ]
            },
            "implementation_approach": {
                "recommended_strategy": "Accelerated implementation with phased module activation",
                "timeline": {
                    "total_duration": "8-10 weeks",
                    "phases": [
                        {
                            "name": "Discovery & Setup",
                            "duration": "2 weeks",
                            "activities": [
                                "Business process review",
                                "System configuration planning",
                                "Integration planning",
                                "Data migration mapping"
                            ]
                        },
                        {
                            "name": "Core Implementation",
                            "duration": "3 weeks",
                            "activities": [
                                "System configuration",
                                "Core data migration",
                                "Primary integrations setup",
                                "Administrator training"
                            ]
                        },
                        {
                            "name": "Validation & Training",
                            "duration": "2 weeks",
                            "activities": [
                                "User acceptance testing",
                                "Report configuration",
                                "End-user training",
                                "Go-live preparation"
                            ]
                        },
                        {
                            "name": "Go-Live & Stabilization",
                            "duration": "1-3 weeks",
                            "activities": [
                                "Go-live cutover",
                                "Post-implementation support",
                                "Process refinement",
                                "Secondary feature activation"
                            ]
                        }
                    ]
                }
            },
            "integration_capabilities": {
                "pre_built_connectors": {
                    "quickbooks": {
                        "sync_direction": "Bi-directional",
                        "data_synced": ["Projects", "Clients", "Invoices", "Expenses"],
                        "implementation_effort": "Low - uses standard connector",
                        "typical_setup_time": "3-5 days"
                    },
                    "salesforce": {
                        "sync_direction": "Bi-directional",
                        "data_synced": ["Accounts", "Opportunities", "Contacts", "Projects"],
                        "implementation_effort": "Low to Medium - configuration required",
                        "typical_setup_time": "5-7 days"
                    },
                    "microsoft_365": {
                        "sync_direction": "Bi-directional",
                        "data_synced": ["Calendar", "Tasks", "Project files"],
                        "implementation_effort": "Low - uses standard connector",
                        "typical_setup_time": "2-3 days"
                    }
                },
                "data_migration": {
                    "excel_project_data": {
                        "complexity": "Medium",
                        "approach": "Template-based import",
                        "typical_effort": "3-5 days depending on data volume and complexity"
                    },
                    "microsoft_project": {
                        "complexity": "Medium",
                        "approach": "Standard import utility with mapping",
                        "typical_effort": "2-4 days per project template type"
                    }
                }
            },
            "resource_requirements": {
                "customer_resources": {
                    "executive_sponsor": "5% time allocation throughout project",
                    "project_owner": "30-50% allocation throughout implementation",
                    "departmental_representatives": "10-15% allocation during requirements and testing",
                    "it_resource": "20% allocation for integration support",
                    "power_users": "15-20% allocation during testing and training phases"
                },
                "vendor_resources": {
                    "implementation_consultant": "Dedicated throughout implementation",
                    "integration_specialist": "As needed for specific integration work",
                    "training_specialist": "During training phases",
                    "technical_support": "Available throughout and post-implementation"
                }
            },
            "pricing_structure": {
                "subscription_licensing": {
                    "administrative_user": "$120 per user per month",
                    "standard_user": "$65 per user per month",
                    "limited_user": "$25 per user per month",
                    "volume_discounts": {
                        "tier_1": "1-50 users: 0%",
                        "tier_2": "51-100 users: 10%",
                        "tier_3": "101-200 users: 15%",
                        "tier_4": "201+ users: 20%"
                    }
                },
                "implementation_services": {
                    "fixed_price_package": "$35,000 for standard implementation",
                    "includes": [
                        "System configuration",
                        "Data migration from Excel and Microsoft Project",
                        "Standard integration setup",
                        "Administrator and end-user training",
                        "Go-live support"
                    ],
                    "additional_services": {
                        "custom_report_development": "$1,500 per report",
                        "custom_integration_development": "$5,000-$15,000 depending on complexity",
                        "additional_training": "$2,500 per day"
                    }
                },
                "ongoing_costs": {
                    "standard_support": "Included in subscription",
                    "premium_support": "$12,000 annually",
                    "additional_storage": "$50 per 100GB per month",
                    "optional_modules": {
                        "advanced_revenue_recognition": "$15 per administrative user per month",
                        "skills_management": "$10 per standard user per month",
                        "scenario_planning": "$20 per administrative user per month",
                        "mobile_app_pro": "$10 per user per month"
                    }
                }
            },
            "best_practices": {
                "for_professional_services": {
                    "critical_processes": [
                        "Resource allocation and forecasting",
                        "Time tracking compliance",
                        "Project budget monitoring",
                        "Milestone-based invoicing",
                        "Utilization reporting"
                    ],
                    "key_metrics": [
                        "Billable utilization",
                        "Project margin",
                        "Employee utilization",
                        "Realization rate",
                        "Client satisfaction"
                    ]
                },
                "change_management": {
                    "approach": "Middle-out adoption strategy",
                    "key_components": [
                        "Early power user involvement",
                        "Clear communication of benefits",
                        "Process simplification focus",
                        "Incremental feature rollout",
                        "Concrete success metrics"
                    ]
                },
                "quick_wins": [
                    "Weekly utilization dashboards for management",
                    "Automated timesheet reminders",
                    "Project budget vs. actual tracking",
                    "Resource capacity visualization",
                    "Client-ready project status reports"
                ]
            }
        }