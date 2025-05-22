"""
Compliance inquiry business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class RegulatoryComplianceInquiry(BusinessScenario):
    """
    Regulatory compliance inquiry scenario.
    
    Tests how well the model handles detailed questions about regulatory compliance,
    requiring knowledge of regulations and technical details.
    """
    
    def __init__(self, scenario_id: str = "compliance_001"):
        """
        Initialize the regulatory compliance inquiry scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Financial Regulatory Compliance Inquiry",
            description="Customer inquiring about regulatory compliance features for a financial services solution",
            industry="Financial Services",
            complexity="medium",
            tools_required=["knowledge_base", "document_retrieval"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "We're a mid-sized investment firm looking at your portfolio management platform. We need to ensure it meets SEC regulations, particularly Rule 17a-4 for record keeping. Can you tell me what compliance features your system has?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "SEC compliance Rule 17a-4 record keeping financial services",
                            "categories": ["compliance", "financial_services", "regulations"]
                        }
                    }
                ]
            },
            {
                "user_message": "That's helpful. What about audit trails? We need to ensure that all user actions, especially those related to trade decisions and client account changes, are properly logged and immutable.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "audit trails immutable records financial services",
                            "categories": ["compliance", "security", "financial_services"]
                        }
                    }
                ]
            },
            {
                "user_message": "Good to know. We also need to comply with FINRA regulations. Do you have documentation about how your system helps with FINRA compliance, specifically with supervision requirements under Rule 3110?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "compliance_documentation",
                            "keywords": ["FINRA", "Rule 3110", "supervision", "financial services"]
                        }
                    }
                ]
            },
            {
                "user_message": "One last question - we need to implement strict data access controls based on client sensitivity tiers. Can your system support granular permission levels that align with our compliance requirements for information barriers?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "information barriers granular permissions data access controls financial services",
                            "categories": ["security", "compliance", "access_control"]
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
            "sec_compliance": {
                "rule_17a_4_compliance": True,
                "record_keeping_features": [
                    "Write-once-read-many (WORM) storage option",
                    "Configurable retention periods (3-7 years default)",
                    "Tamper-evident audit trails",
                    "Comprehensive indexing and search",
                    "Automated backup and disaster recovery",
                    "Third-party storage integration options"
                ],
                "documentation_available": [
                    "SEC 17a-4 Compliance Whitepaper",
                    "FINRA 4511 Compliance Guide",
                    "Records Retention Implementation Guide"
                ],
                "certification": "Annual independent compliance audit available"
            },
            "audit_capabilities": {
                "comprehensive_logging": True,
                "logged_events": [
                    "User logins and authentication events",
                    "Account access and permission changes",
                    "Data modifications and viewing",
                    "Trade-related activities",
                    "Report generation and exports",
                    "System configuration changes"
                ],
                "audit_trail_features": [
                    "Tamper-proof record design",
                    "Digital signatures for log integrity",
                    "Centralized log management",
                    "Real-time alerts for suspicious activities",
                    "Advanced filtering and reporting"
                ],
                "retention_period": "Configurable up to 7 years"
            },
            "finra_compliance": {
                "rule_3110_support": {
                    "supervision_features": [
                        "Automated transaction surveillance",
                        "Communication monitoring tools",
                        "Exception reporting",
                        "Escalation workflows",
                        "Role-based review processes"
                    ],
                    "documentation": {
                        "name": "FINRA Rule 3110 Compliance Guide",
                        "sections": [
                            "Supervisory procedures implementation",
                            "Communication review setup",
                            "Transaction monitoring configuration",
                            "Escalation workflow management",
                            "Regulatory reporting"
                        ]
                    }
                }
            },
            "information_barriers": {
                "access_control_model": "Attribute-based access control (ABAC)",
                "permission_levels": [
                    "View-only",
                    "Standard edit",
                    "Advanced edit",
                    "Administrative",
                    "Compliance officer"
                ],
                "segmentation_features": [
                    "Client sensitivity tiering",
                    "Department-based segregation",
                    "Material non-public information (MNPI) controls",
                    "Conflict detection rules",
                    "Cross-barrier approval workflows"
                ],
                "chinese_wall_capabilities": True,
                "monitoring_and_reporting": [
                    "Barrier crossing alerts",
                    "Unauthorized access attempts logging",
                    "Periodic access review reports",
                    "Exception documentation"
                ]
            }
        }


class DataPrivacyComplianceScenario(BusinessScenario):
    """
    Data privacy compliance scenario.
    
    Tests how well the model handles international data privacy regulations
    and complex compliance requirements.
    """
    
    def __init__(self, scenario_id: str = "compliance_002"):
        """
        Initialize the data privacy compliance scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="International Data Privacy Compliance",
            description="Multinational company evaluating data privacy compliance across multiple jurisdictions",
            industry="Technology",
            complexity="complex",
            tools_required=["knowledge_base", "document_retrieval"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Our company is expanding operations to Europe and we need to ensure our customer data handling complies with GDPR. We use your CRM platform for all customer interactions. Can you explain how your system helps with GDPR compliance?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "GDPR compliance CRM customer data",
                            "categories": ["compliance", "data_privacy", "international"]
                        }
                    }
                ]
            },
            {
                "user_message": "Thanks. We're also concerned about data localization requirements in different countries. Some of our customers are in Brazil (LGPD) and California (CCPA). How does your system handle these different privacy regimes simultaneously?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "data localization LGPD CCPA international compliance",
                            "categories": ["compliance", "data_privacy", "international"]
                        }
                    }
                ]
            },
            {
                "user_message": "That makes sense. For GDPR specifically, can you explain your Data Processing Agreement? Also, are you able to act as a data processor while our company remains the data controller?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "legal_documentation",
                            "keywords": ["Data Processing Agreement", "GDPR", "data processor", "data controller"]
                        }
                    }
                ]
            },
            {
                "user_message": "One final question - in the event of a data breach, what mechanisms does your platform have to help us meet the 72-hour notification requirement under GDPR?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "data breach notification GDPR 72 hour requirement",
                            "categories": ["security", "compliance", "incident_response"]
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
            "gdpr_compliance": {
                "core_features": [
                    "Data subject access request (DSAR) management",
                    "Right to be forgotten automation",
                    "Data portability export tools",
                    "Consent management system",
                    "Purpose limitation controls",
                    "Data minimization tools",
                    "Automated data retention policies"
                ],
                "data_processing": {
                    "role": "Data Processor",
                    "customer_role": "Data Controller",
                    "dpa_available": True,
                    "dpa_features": [
                        "Standard contractual clauses",
                        "Processor obligations",
                        "Sub-processor management",
                        "Data transfer provisions",
                        "Security measures documentation"
                    ]
                },
                "certifications": [
                    "ISO 27701 (Privacy Information Management)",
                    "EU-US Data Privacy Framework"
                ]
            },
            "international_compliance": {
                "supported_regulations": [
                    "GDPR (EU)",
                    "CCPA/CPRA (California)",
                    "LGPD (Brazil)",
                    "PIPEDA (Canada)",
                    "PDPA (Singapore)",
                    "Privacy Act (Australia)"
                ],
                "data_localization": {
                    "regional_data_centers": [
                        "European Union (Frankfurt, Dublin)",
                        "North America (US-East, US-West)",
                        "South America (São Paulo)",
                        "Asia Pacific (Singapore, Sydney)"
                    ],
                    "data_residency_controls": True,
                    "geo-fencing_capabilities": "Configurable per customer account"
                },
                "multi-framework_compliance": {
                    "unified_privacy_controls": True,
                    "jurisdiction_specific_settings": True,
                    "automated_regulatory_updates": "Quarterly"
                }
            },
            "breach_notification_support": {
                "incident_response_features": [
                    "Automated breach detection",
                    "Real-time security alerts",
                    "Severity classification system",
                    "Affected data mapping tools",
                    "Timeline tracking for notification deadlines",
                    "Customizable notification workflows",
                    "Documentation and evidence collection"
                ],
                "notification_templates": [
                    "Regulatory authority notifications",
                    "Data subject notifications",
                    "Internal stakeholder communications"
                ],
                "72_hour_compliance_tools": {
                    "countdown_timers": True,
                    "escalation_procedures": True,
                    "role_assignment_for_response_team": True,
                    "impact_assessment_wizard": True
                },
                "post-breach_support": [
                    "Forensic investigation assistance",
                    "Remediation tracking",
                    "Regulatory communication management"
                ]
            }
        }