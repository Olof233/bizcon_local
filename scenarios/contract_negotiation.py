"""
Contract negotiation business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class StandardContractNegotiation(BusinessScenario):
    """
    Standard contract negotiation scenario.
    
    Tests how well the model handles common contract negotiation questions,
    requiring knowledge of terms, pricing, and policies.
    """
    
    def __init__(self, scenario_id: str = "contract_001"):
        """
        Initialize the standard contract negotiation scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Standard SaaS Contract Negotiation",
            description="Customer negotiating terms for a standard SaaS subscription agreement",
            industry="General",
            complexity="medium",
            tools_required=["knowledge_base", "pricing_calculator", "document_retrieval"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "We're ready to move forward with your CRM solution, but I have some questions about the contract terms. We need a 3-year agreement for 50 users, but the standard agreement only offers yearly renewals. Can we lock in pricing for the full 3 years?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "multi-year contract pricing lock terms",
                            "categories": ["contracts", "pricing", "policies"]
                        }
                    }
                ]
            },
            {
                "user_message": "That works for us. Another concern is the SLA - your standard agreement mentions 99.5% uptime, but we really need 99.9% given how critical this system will be for our sales team. Is that possible, and would it affect our pricing?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "legal_documentation",
                            "keywords": ["SLA", "uptime", "99.9%", "service credits", "premium support"]
                        }
                    },
                    {
                        "tool_id": "pricing_calculator",
                        "parameters": {
                            "product_id": "crm_professional",
                            "users": 50,
                            "term_length": 36,
                            "add_ons": ["premium_sla"]
                        }
                    }
                ]
            },
            {
                "user_message": "I understand there's an additional cost. What about the limitation of liability clause? The standard agreement caps liability at 12 months of fees, but our legal team is requesting at least 24 months for significant breaches like data security incidents.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "limitation of liability data security breach contract terms negotiation",
                            "categories": ["contracts", "legal", "security"]
                        }
                    }
                ]
            },
            {
                "user_message": "Thank you for that clarification. One final question - we have strict requirements about data ownership. Can you confirm that we retain full ownership of all our customer data, and that you'll delete all copies upon contract termination?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "legal_documentation",
                            "keywords": ["data ownership", "contract termination", "data deletion", "retention policy"]
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
            "contract_terms": {
                "multi_year_options": {
                    "available_terms": [1, 2, 3, 5],
                    "discount_rates": {
                        "1_year": "standard pricing",
                        "2_year": "5% discount",
                        "3_year": "10% discount",
                        "5_year": "15% discount"
                    },
                    "price_lock_guarantee": True,
                    "exceptions": "Significant infrastructure cost increases (capped at 3% annually)"
                },
                "renewal_terms": {
                    "auto_renewal": True,
                    "renewal_notice_period": "60 days",
                    "renewal_price_cap": "Maximum 5% increase"
                }
            },
            "service_level_agreement": {
                "standard_tier": {
                    "uptime_commitment": "99.5%",
                    "scheduled_maintenance": "Excluded from calculation",
                    "service_credits": "10% of monthly fees for each 0.1% below commitment",
                    "support_response_time": "8 business hours"
                },
                "premium_tier": {
                    "uptime_commitment": "99.9%",
                    "scheduled_maintenance": "Included in calculation",
                    "service_credits": "15% of monthly fees for each 0.1% below commitment",
                    "support_response_time": "4 business hours",
                    "cost_increase": "15% premium on base subscription"
                },
                "measurement_period": "Monthly",
                "credit_request_process": "Must be submitted within 15 days of incident"
            },
            "liability_provisions": {
                "standard_limitation": "12 months of fees paid",
                "negotiable_range": "12-24 months of fees paid",
                "enhanced_data_protection": {
                    "available": True,
                    "cap_for_data_breaches": "24 months of fees paid",
                    "requires": "Enterprise tier or additional cyber liability rider"
                },
                "exclusions": [
                    "Gross negligence",
                    "Willful misconduct",
                    "Intellectual property infringement",
                    "Confidentiality breaches"
                ]
            },
            "data_ownership": {
                "customer_ownership_statement": "Customer retains all ownership, right, title, and interest in and to Customer Data",
                "vendor_license": "Limited license to use data only to provide services",
                "termination_provisions": {
                    "data_return_period": "30 days upon request",
                    "data_deletion_timeline": "90 days after termination",
                    "deletion_certification": "Available upon request",
                    "data_formats": ["CSV", "SQL", "JSON", "Native format"]
                },
                "data_retention_policy": {
                    "backups": "Retained for 90 days after deletion for disaster recovery purposes only",
                    "anonymized_data": "May be retained for aggregate analytics"
                }
            }
        }


class EnterpriseAgreementNegotiation(BusinessScenario):
    """
    Enterprise agreement negotiation scenario.
    
    Tests how well the model handles complex enterprise contract negotiations,
    requiring advanced knowledge of legal terms and business implications.
    """
    
    def __init__(self, scenario_id: str = "contract_002"):
        """
        Initialize the enterprise agreement negotiation scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Enterprise Software Agreement Negotiation",
            description="Large enterprise negotiating a complex software implementation with custom terms",
            industry="Financial Services",
            complexity="complex",
            tools_required=["knowledge_base", "document_retrieval", "pricing_calculator"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Our legal team has reviewed your Master Services Agreement for the enterprise data platform implementation. We have concerns about several clauses. First, regarding the intellectual property rights for customizations we'll be developing - your standard terms state that all customizations belong to you, but we need joint ownership for the financial models we'll be implementing.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "intellectual property customization ownership enterprise agreement financial services",
                            "categories": ["contracts", "legal", "enterprise", "customization"]
                        }
                    }
                ]
            },
            {
                "user_message": "That's helpful. Next, we need more specific business continuity guarantees. As a financial institution, we're subject to regulatory requirements that mandate specific RPO and RTO metrics. Your standard agreement mentions 'reasonable efforts,' but we need concrete recovery time objectives of less than 4 hours and recovery point objectives of less than 15 minutes.",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "legal_documentation",
                            "keywords": ["business continuity", "disaster recovery", "RPO", "RTO", "financial services", "regulatory requirements"]
                        }
                    }
                ]
            },
            {
                "user_message": "Regarding payment terms, your agreement requires annual payment in advance, but our procurement policies require quarterly payments. Can we modify this? Additionally, we need net-60 payment terms rather than the standard net-30.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "payment terms quarterly net-60 enterprise agreement",
                            "categories": ["contracts", "billing", "enterprise"]
                        }
                    },
                    {
                        "tool_id": "pricing_calculator",
                        "parameters": {
                            "product_id": "data_platform_enterprise",
                            "users": 500,
                            "term_length": 36,
                            "payment_frequency": "quarterly",
                            "custom_terms": ["net_60"]
                        }
                    }
                ]
            },
            {
                "user_message": "Finally, regarding the governing law - your agreement specifies California law, but as a New York based financial institution, we require New York law and jurisdiction. Is this acceptable? Also, would this affect any of the regulatory compliance guarantees?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "governing law jurisdiction New York financial services compliance",
                            "categories": ["legal", "contracts", "compliance", "financial_services"]
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
            "intellectual_property": {
                "standard_terms": "Vendor maintains ownership of all IP in platform and customizations",
                "negotiable_options": [
                    "Joint ownership of customer-specific customizations",
                    "Customer ownership of customer-specific algorithms and models",
                    "Perpetual license to customizations without ownership"
                ],
                "financial_services_policy": {
                    "proprietary_models": "Customer ownership permitted",
                    "platform_extensions": "Joint ownership considered for significant developments",
                    "conditions": "Additional license fees may apply for commercial reuse"
                },
                "documentation_required": "Custom IP addendum to Master Services Agreement"
            },
            "business_continuity": {
                "standard_terms": {
                    "recovery_time_objective": "8 business hours",
                    "recovery_point_objective": "4 hours",
                    "disaster_recovery_testing": "Annual"
                },
                "financial_services_tier": {
                    "available": True,
                    "recovery_time_objective": "4 hours",
                    "recovery_point_objective": "15 minutes",
                    "disaster_recovery_testing": "Quarterly",
                    "additional_cost": "20% premium on subscription",
                    "regulatory_documentation": "Available upon request",
                    "third_party_audits": "SOC 2 Type II, ISO 27001"
                },
                "custom_requirements": {
                    "minimum_achievable_RTO": "2 hours",
                    "minimum_achievable_RPO": "5 minutes",
                    "geographical_redundancy": "Available in premium tier",
                    "active-active_configuration": "Available for critical modules"
                }
            },
            "payment_terms": {
                "standard_options": {
                    "frequency": ["Annual", "Semi-annual"],
                    "payment_terms": "Net-30",
                    "discount_for_annual": "3% of total contract value"
                },
                "enterprise_options": {
                    "frequency": ["Annual", "Semi-annual", "Quarterly"],
                    "payment_terms": ["Net-30", "Net-45", "Net-60"],
                    "financial_impact": {
                        "quarterly_payments": "2% premium on total contract value",
                        "net_45_terms": "No additional cost",
                        "net_60_terms": "1% premium on total contract value"
                    }
                },
                "approval_requirements": {
                    "quarterly_payments": "Standard for enterprise tier",
                    "net_60_terms": "Finance director approval required",
                    "documentation": "Custom billing addendum"
                }
            },
            "governing_law": {
                "standard_jurisdiction": "California",
                "acceptable_alternatives": [
                    "New York",
                    "Delaware",
                    "Texas",
                    "Illinois",
                    "Customer's primary jurisdiction (for enterprise customers)"
                ],
                "financial_services_considerations": {
                    "new_york_law_impact": "No impact on compliance guarantees",
                    "regulatory_requirements": "State-specific addendums available if needed",
                    "dispute_resolution": "Arbitration options available regardless of jurisdiction"
                },
                "approval_level": "Legal department review only",
                "typical_response_time": "3-5 business days"
            }
        }