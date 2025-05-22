"""
Technical support business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class StandardTechnicalSupport(BusinessScenario):
    """
    Standard technical support scenario.
    
    Tests how well the model handles common technical support inquiries,
    requiring troubleshooting skills and product knowledge.
    """
    
    def __init__(self, scenario_id: str = "support_001"):
        """
        Initialize the standard technical support scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Standard Technical Support Inquiry",
            description="Customer experiencing login issues with software platform",
            industry="General",
            complexity="simple",
            tools_required=["knowledge_base", "support_ticket"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "I'm having trouble logging into our account. When I enter my credentials on the login page, it just refreshes and doesn't give me any error message. I've tried clearing my browser cache already.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "login issues browser refresh no error message",
                            "categories": ["troubleshooting", "authentication", "common_issues"]
                        }
                    }
                ]
            },
            {
                "user_message": "I'm using Chrome version 112.0.5615.121 on Windows 11. And yes, we have SSO enabled for our organization. I didn't realize that could be causing an issue.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "SSO login issues Chrome Windows 11",
                            "categories": ["troubleshooting", "authentication", "sso"]
                        }
                    }
                ]
            },
            {
                "user_message": "I tried the incognito window as suggested, but I'm still having the same issue. I also asked my colleague to try logging in from her computer, and she's experiencing the same problem. So it seems to be affecting our entire organization.",
                "expected_tool_calls": [
                    {
                        "tool_id": "support_ticket",
                        "parameters": {
                            "check_organization": "Acme Corp",
                            "issue_type": "authentication",
                            "severity": "medium"
                        }
                    }
                ]
            },
            {
                "user_message": "That's very helpful to know there's an ongoing issue with our SSO provider. How long do you think it will take to resolve? We have an important client presentation this afternoon and need access to the system.",
                "expected_tool_calls": [
                    {
                        "tool_id": "support_ticket",
                        "parameters": {
                            "create_ticket": True,
                            "customer_name": "Acme Corp",
                            "issue_description": "Unable to login due to SSO provider issue. Urgent access needed for client presentation.",
                            "severity": "high",
                            "workaround_requested": True
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
            "login_troubleshooting": {
                "common_issues": [
                    "Browser cache/cookies",
                    "Outdated browser version",
                    "Password expiration",
                    "Account lockout due to failed attempts",
                    "SSO configuration issues",
                    "Network restrictions"
                ],
                "diagnostic_steps": [
                    "Clear browser cache and cookies",
                    "Try incognito/private browsing mode",
                    "Verify account status in admin console",
                    "Check SSO provider status",
                    "Test with alternate browser",
                    "Verify network allowing authentication endpoints"
                ]
            },
            "sso_integration": {
                "supported_providers": [
                    "Okta",
                    "Azure AD",
                    "Google Workspace",
                    "OneLogin",
                    "Ping Identity"
                ],
                "known_issues": {
                    "silent_failures": "Often caused by misconfigured SAML attributes or certificate expiration",
                    "infinite_redirects": "Can occur when return URL is misconfigured",
                    "timeout_errors": "Usually related to network latency or provider availability"
                },
                "current_status": {
                    "incident": "Okta partial outage affecting authentication services",
                    "started": "2025-05-22T08:45:00Z",
                    "estimated_resolution": "2025-05-22T14:30:00Z",
                    "affected_services": ["SAML authentication", "MFA verification"],
                    "status_page": "https://status.okta.com/"
                }
            },
            "workarounds": {
                "temporary_access": {
                    "direct_login_option": True,
                    "requires_admin_approval": True,
                    "duration": "24 hours",
                    "setup_time": "15-30 minutes"
                },
                "alternative_access": {
                    "mobile_application": "Not affected by SSO issue",
                    "api_access": "Available with direct authentication",
                    "read-only_mode": "Available without authentication for shared resources"
                }
            },
            "support_process": {
                "ticket_creation": "Automatic for SSO-related issues",
                "escalation_path": [
                    "Tier 1: Authentication Specialist",
                    "Tier 2: SSO Integration Engineer",
                    "Tier 3: Identity Platform Engineer"
                ],
                "response_time_sla": {
                    "high_severity": "30 minutes",
                    "medium_severity": "2 hours",
                    "low_severity": "8 hours"
                },
                "proactive_notifications": "Sent to organization admins for authentication issues"
            }
        }


class ComplexIntegrationSupport(BusinessScenario):
    """
    Complex integration support scenario.
    
    Tests how well the model handles complex technical integration issues,
    requiring deep technical knowledge and multi-system understanding.
    """
    
    def __init__(self, scenario_id: str = "support_002"):
        """
        Initialize the complex integration support scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="API Integration Troubleshooting",
            description="Enterprise customer experiencing data synchronization failures with API integration",
            industry="Retail",
            complexity="complex",
            tools_required=["knowledge_base", "support_ticket", "document_retrieval"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "We've been experiencing intermittent failures with the inventory synchronization between our e-commerce platform and your order management system. The API calls are timing out, and we're seeing data discrepancies. This started yesterday after we deployed the latest version of your SDK.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "inventory synchronization API timeout SDK latest version",
                            "categories": ["api", "integration", "troubleshooting", "retail"]
                        }
                    }
                ]
            },
            {
                "user_message": "We're using SDK version 4.2.1 on our Node.js backend, which is running on AWS Lambda. The logs show timeout errors when making batch update calls to the /inventory/batch endpoint. The payloads are fairly large - around 2MB with about 5,000 SKUs in each batch. Here's an example of the error message: 'Error: ConnectTimeoutError: Connect Timeout Error'.",
                "expected_tool_calls": [
                    {
                        "tool_id": "document_retrieval",
                        "parameters": {
                            "document_type": "technical_documentation",
                            "keywords": ["SDK 4.2.1", "Node.js", "inventory batch API", "timeout", "ConnectTimeoutError", "Lambda"]
                        }
                    }
                ]
            },
            {
                "user_message": "We tried reducing the batch size to 1,000 SKUs, and it's more reliable but still fails occasionally. Our retry logic is set to 3 attempts with exponential backoff. We're also seeing higher than normal latency even when calls succeed - around 8-10 seconds versus the usual 2-3 seconds. Our Lambda functions have a 30-second timeout.",
                "expected_tool_calls": [
                    {
                        "tool_id": "support_ticket",
                        "parameters": {
                            "create_ticket": True,
                            "customer_name": "MegaRetail Inc",
                            "issue_description": "Inventory API timeout issues with SDK 4.2.1 on Node.js/Lambda. Large batches (5000 SKUs) consistently fail, smaller batches (1000 SKUs) intermittently fail. Higher than normal latency (8-10s vs 2-3s).",
                            "severity": "high",
                            "environment": "production",
                            "component": "inventory_api",
                            "version": "4.2.1"
                        }
                    }
                ]
            },
            {
                "user_message": "Thank you for the information. Is there anything we can do immediately to stabilize our integration while your team investigates? We're heading into our busiest sales period and need reliable inventory synchronization to avoid overselling products.",
                "expected_tool_calls": [
                    {
                        "tool_id": "knowledge_base",
                        "parameters": {
                            "query": "inventory API performance optimization workaround high volume",
                            "categories": ["best_practices", "optimization", "retail", "high_volume"]
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
            "api_issue_diagnosis": {
                "known_issues": {
                    "sdk_4_2_1": {
                        "bug_confirmed": True,
                        "description": "Memory leak in connection pooling for large batch operations",
                        "conditions": [
                            "Node.js environments",
                            "Batch operations > 1000 items",
                            "Serverless deployments (Lambda/Azure Functions)"
                        ],
                        "issue_number": "SDK-4532",
                        "status": "Fix in progress, expected in 4.2.2"
                    },
                    "backend_scaling": {
                        "incident": "Partial degradation in inventory service",
                        "started": "2025-05-21T14:20:00Z",
                        "affected_regions": ["us-east-1", "eu-west-1"],
                        "status": "Mitigated but under monitoring"
                    }
                },
                "technical_details": {
                    "root_cause": "Connection pool exhaustion combined with increased payload size",
                    "impact": "Exponential latency increase with batch size",
                    "monitoring_data": "95th percentile response time increased from 2.3s to 12.7s"
                }
            },
            "immediate_solutions": {
                "sdk_configuration": {
                    "timeout_setting": "Increase from default 30s to 60s",
                    "connection_pool": "Limit to 5 concurrent connections",
                    "keep_alive": "Set to false for Lambda environments"
                },
                "batch_optimization": {
                    "recommended_size": "500 items per batch for stability",
                    "throttling": "Implement 1 second delay between batch requests",
                    "circuit_breaker": "Implement with 50% failure threshold"
                },
                "alternative_endpoints": {
                    "single_item_api": "/inventory/items/{sku} for critical items",
                    "delta_updates": "/inventory/delta for changed quantities only",
                    "priority_queue": "/inventory/priority available for enterprise customers"
                }
            },
            "long_term_solutions": {
                "sdk_upgrade": {
                    "version": "4.2.2",
                    "release_date": "2025-05-25",
                    "changelog": "Fixed connection pooling memory leak in batch operations"
                },
                "architecture_recommendations": [
                    "Move from batch to streaming updates",
                    "Implement event-based synchronization",
                    "Deploy dedicated synchronization service",
                    "Consider webhook-based approach for inventory changes"
                ],
                "capacity_planning": {
                    "peak_handling": "Pre-notification of high volume periods",
                    "reserved_capacity": "Available for enterprise customers",
                    "scheduled_maintenance": "Blackout window available"
                }
            },
            "support_details": {
                "ticket_info": {
                    "id": "INC-57392",
                    "priority": "High",
                    "assigned_to": "Enterprise Integration Team",
                    "status": "In Progress"
                },
                "response_plan": {
                    "immediate_contact": "Senior Integration Engineer within 1 hour",
                    "temporary_access": "Dedicated API instance offered",
                    "monitoring": "Enhanced telemetry enabled for customer endpoints"
                },
                "escalation_path": {
                    "technical": "API Platform Team",
                    "business": "Customer Success Manager notification"
                }
            }
        }