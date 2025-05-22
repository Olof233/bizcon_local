"""
Product inquiry business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class EnterpriseProductInquiry(BusinessScenario):
    """
    Enterprise product inquiry scenario.
    
    Tests how well the model handles detailed enterprise product inquiries,
    requiring the use of product catalogs and pricing calculators.
    """
    
    def __init__(self, scenario_id: str = "product_inquiry_001"):
        """
        Initialize the enterprise product inquiry scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Enterprise Software Product Inquiry",
            description="Customer inquiring about enterprise data analytics software features, pricing, and implementation",
            industry="Enterprise Software",
            complexity="medium",
            tools_required=["product_catalog", "pricing_calculator", "knowledge_base"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Hi, I'm looking for information about your enterprise data analytics platform. We're a mid-sized financial services company with about 500 employees. Can you tell me about the key features and how it might help us analyze customer transaction data?",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_category": "data_analytics",
                            "industry": "financial_services"
                        }
                    }
                ]
            },
            {
                "user_message": "That sounds promising. What's the pricing structure for this solution? We'd need to support around 50 concurrent users, and we'd want the advanced security features you mentioned.",
                "expected_tool_calls": [
                    {
                        "tool_id": "pricing_calculator",
                        "parameters": {
                            "product_id": "data_analytics_enterprise",
                            "users": 50,
                            "features": ["advanced_security", "financial_compliance"]
                        }
                    }
                ]
            },
            {
                "user_message": "The pricing seems reasonable. How long does the implementation typically take, and what kind of support do you provide during the process? Also, do you offer any training for our team?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "implementation timeline data analytics enterprise financial",
                            "categories": ["implementation", "training", "support"]
                        }
                    }
                ]
            },
            {
                "user_message": "Great, this all sounds good. Is there a way we could schedule a demo with one of your technical specialists? We'd like to see how the platform handles some specific financial use cases we have.",
                "expected_tool_calls": [
                    {
                        "tool_id": "scheduler",
                        "parameters": {
                            "meeting_type": "product_demo",
                            "product_id": "data_analytics_enterprise",
                            "industry": "financial_services",
                            "participants": ["technical_specialist"]
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
        # Load product data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        product_file = os.path.join(data_dir, "products", "enterprise_software.json")
        
        with open(product_file, 'r') as f:
            product_data = json.load(f)
        
        # Extract relevant information for ground truth
        analytics_product = next((p for p in product_data 
                                 if p.get("category") == "data_analytics" 
                                 and p.get("name") == "DataInsight Enterprise"), {})
        
        return {
            "product_information": {
                "name": analytics_product.get("name", "DataInsight Enterprise"),
                "key_features": analytics_product.get("key_features", []),
                "benefits": analytics_product.get("benefits", []),
                "industries": analytics_product.get("industries", ["financial_services"]),
            },
            "pricing_information": {
                "model": "per_user_subscription",
                "base_price": 1200,  # Annual per user
                "discount_tiers": {
                    "20-49": 0.10,  # 10% discount
                    "50-99": 0.15,  # 15% discount
                    "100+": 0.25    # 25% discount
                },
                "additional_features": {
                    "advanced_security": 200,
                    "financial_compliance": 300,
                    "ai_analytics": 500
                }
            },
            "implementation_information": {
                "typical_timeline": "10-12 weeks",
                "phases": [
                    "Initial assessment (1-2 weeks)",
                    "System configuration (3-4 weeks)",
                    "Data migration (2-3 weeks)",
                    "Testing (2 weeks)",
                    "Training and deployment (2 weeks)"
                ],
                "support_included": [
                    "Dedicated implementation manager",
                    "24/7 technical support during implementation",
                    "Knowledge base access",
                    "Weekly progress meetings"
                ],
                "training_options": [
                    "On-site training workshop (2 days)",
                    "Virtual training sessions (8 hours total)",
                    "Self-paced learning modules",
                    "Admin-specific advanced training"
                ]
            }
        }


class ProductCustomizationInquiry(BusinessScenario):
    """
    Product customization inquiry scenario.
    
    Tests how well the model handles complex product customization requests,
    requiring deep product knowledge and technical understanding.
    """
    
    def __init__(self, scenario_id: str = "product_inquiry_002"):
        """
        Initialize the product customization inquiry scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Enterprise Product Customization Inquiry",
            description="Customer inquiring about customizing enterprise software for specific regulatory requirements",
            industry="Healthcare",
            complexity="complex",
            tools_required=["product_catalog", "knowledge_base", "document_retrieval"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "Hello, we're a healthcare provider considering your data management platform. We need to ensure it can be customized to meet HIPAA compliance requirements and integrate with our existing Epic EHR system. Can you tell me if this is possible?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "HIPAA compliance Epic EHR integration",
                            "categories": ["compliance", "integrations", "healthcare"]
                        }
                    }
                ]
            },
            {
                "user_message": "That's helpful. We would need to customize the patient data fields and access controls. Do you have technical documentation about the API or customization options for healthcare-specific requirements?",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "technical_documentation",
                            "keywords": ["API", "customization", "healthcare", "HIPAA", "data fields", "access control"]
                        }
                    }
                ]
            },
            {
                "user_message": "I see. What about the data encryption standards? We need to ensure that all patient data is encrypted both at rest and in transit, and that the encryption meets HIPAA requirements.",
                "expected_tool_calls": [
                    {
                        "tool_id": "product_catalog",
                        "parameters": {
                            "product_id": "data_management_healthcare",
                            "features": ["encryption", "security"]
                        }
                    }
                ]
            },
            {
                "user_message": "One more question - do you offer a validation environment where we can test these customizations before deploying to production? And would we have access to your healthcare compliance specialists during implementation?",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "validation environment healthcare implementation specialists",
                            "categories": ["implementation", "testing", "support", "healthcare"]
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
            "compliance_information": {
                "hipaa_compliant": True,
                "compliance_features": [
                    "Role-based access controls",
                    "Audit logging of all data access",
                    "Data encryption (AES-256)",
                    "Automatic session timeouts",
                    "Secure authentication options including MFA",
                    "Business Associate Agreement (BAA) available"
                ],
                "certifications": [
                    "HITRUST CSF Certified",
                    "SOC 2 Type II",
                    "ISO 27001"
                ]
            },
            "integration_capabilities": {
                "epic_ehr_integration": {
                    "supported": True,
                    "integration_methods": [
                        "FHIR API",
                        "HL7 interfaces",
                        "Epic's App Orchard ecosystem"
                    ],
                    "data_exchange": [
                        "Patient demographics",
                        "Clinical data",
                        "Scheduling information",
                        "Billing data"
                    ]
                },
                "api_capabilities": {
                    "rest_api": True,
                    "graphql_api": True,
                    "custom_webhooks": True,
                    "batch_processing": True
                }
            },
            "customization_options": {
                "data_fields": {
                    "custom_fields": True,
                    "field_level_encryption": True,
                    "conditional_visibility": True,
                    "dynamic_forms": True
                },
                "access_controls": {
                    "custom_roles": True,
                    "field_level_permissions": True,
                    "contextual_access": True,
                    "department_segregation": True
                },
                "workflow_customization": {
                    "custom_approval_flows": True,
                    "conditional_logic": True,
                    "automated_alerts": True
                }
            },
            "security_features": {
                "encryption": {
                    "at_rest": "AES-256",
                    "in_transit": "TLS 1.3",
                    "key_management": "FIPS 140-2 validated"
                },
                "authentication": [
                    "SAML 2.0",
                    "OAuth 2.0",
                    "LDAP",
                    "Active Directory integration",
                    "Multi-factor authentication"
                ],
                "monitoring": [
                    "Real-time threat detection",
                    "Behavioral analysis",
                    "Automated vulnerability scanning"
                ]
            },
            "implementation_support": {
                "validation_environment": True,
                "healthcare_specialists": True,
                "implementation_timeline": "12-16 weeks for healthcare implementations",
                "support_team": [
                    "Healthcare compliance specialist",
                    "Technical integration engineer",
                    "Clinical workflow consultant",
                    "Project manager with healthcare experience"
                ]
            }
        }