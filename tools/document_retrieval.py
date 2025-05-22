"""
Document retrieval tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random
import datetime
import re

from .base import BusinessTool


class DocumentRetrievalTool(BusinessTool):
    """
    Document retrieval tool for accessing company documentation.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the document retrieval tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="document_retrieval",
            name="Document Retrieval",
            description="Retrieve company documentation including technical documentation, legal documents, and product guides",
            parameters={
                "document_type": {
                    "type": "string",
                    "description": "Type of document to retrieve (e.g., 'technical_documentation', 'legal_documentation', 'product_guide', 'api_reference')",
                    "required": True
                },
                "keywords": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Keywords to search for in documents",
                    "required": True
                },
                "version": {
                    "type": "string",
                    "description": "Specific version of documentation to retrieve",
                    "required": False
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Initialize mock document database
        self._initialize_document_database()
    
    def _initialize_document_database(self) -> None:
        """Initialize the mock document database."""
        self.document_database = {
            "technical_documentation": [
                {
                    "id": "TD-API-001",
                    "title": "API Reference Guide",
                    "version": "4.2.1",
                    "updated_at": "2025-03-15",
                    "summary": "Complete reference for REST API endpoints, parameters, and response formats",
                    "sections": [
                        {
                            "title": "Authentication",
                            "content": "API uses OAuth 2.0 for authentication. Tokens expire after 1 hour. Implement refresh token flow for continuous access.",
                            "keywords": ["authentication", "OAuth", "token", "security"]
                        },
                        {
                            "title": "Rate Limiting",
                            "content": "Default rate limits are 100 requests per minute per API key. Enterprise customers receive 500 requests per minute. Implement exponential backoff for rate limit errors.",
                            "keywords": ["rate limit", "throttling", "performance", "error handling"]
                        },
                        {
                            "title": "Inventory Batch API",
                            "content": "The /inventory/batch endpoint allows updating multiple inventory items in a single request. Maximum payload size is 2MB. For serverless environments, connection pooling should be disabled to prevent memory leaks. Known issue in SDK 4.2.1 causes connection pool exhaustion with large batch sizes.",
                            "keywords": ["inventory", "batch", "connection pool", "memory leak", "SDK 4.2.1", "Lambda"]
                        },
                        {
                            "title": "Error Handling",
                            "content": "Implement retry logic with exponential backoff. ConnectTimeoutError indicates network connectivity issues or backend service degradation. Check status page for service disruptions.",
                            "keywords": ["error", "retry", "timeout", "ConnectTimeoutError", "backoff"]
                        }
                    ]
                },
                {
                    "id": "TD-SDK-002",
                    "title": "Node.js SDK Implementation Guide",
                    "version": "4.2.1",
                    "updated_at": "2025-04-02",
                    "summary": "Guide for implementing the Node.js SDK in various environments",
                    "sections": [
                        {
                            "title": "Installation",
                            "content": "Install via npm: npm install @company/sdk@4.2.1",
                            "keywords": ["installation", "npm", "setup"]
                        },
                        {
                            "title": "Configuration",
                            "content": "Configure the SDK with your API key and environment settings. In serverless environments, set keepAlive: false to prevent connection issues.",
                            "keywords": ["configuration", "serverless", "Lambda", "keepAlive"]
                        },
                        {
                            "title": "Known Issues",
                            "content": "Version 4.2.1 has a known memory leak in the connection pool when processing large batch operations. Fix scheduled for version 4.2.2 (release date: May 25, 2025). Workaround: Limit batch sizes to 500 items and disable connection pooling.",
                            "keywords": ["known issues", "memory leak", "connection pool", "batch", "4.2.1", "workaround"]
                        },
                        {
                            "title": "Best Practices",
                            "content": "For high-volume operations, implement rate limiting on client side. Use delta updates to reduce payload size. Implement retry with exponential backoff. Set appropriate timeouts based on operation type.",
                            "keywords": ["best practices", "performance", "optimization", "high volume", "timeout"]
                        }
                    ]
                }
            ],
            "legal_documentation": [
                {
                    "id": "LD-SLA-001",
                    "title": "Service Level Agreement",
                    "version": "2025-01",
                    "updated_at": "2025-01-10",
                    "summary": "Service level commitments and remedies for service disruptions",
                    "sections": [
                        {
                            "title": "Uptime Commitments",
                            "content": "Standard tier: 99.5% uptime measured monthly, excluding scheduled maintenance. Premium tier: 99.9% uptime including scheduled maintenance with 72-hour advance notice.",
                            "keywords": ["uptime", "SLA", "99.5%", "99.9%", "scheduled maintenance"]
                        },
                        {
                            "title": "Service Credits",
                            "content": "Standard tier: 10% of monthly fees for each 0.1% below commitment. Premium tier: 15% of monthly fees for each 0.1% below commitment. Credits must be requested within 15 days of incident.",
                            "keywords": ["service credits", "SLA", "compensation", "premium", "standard"]
                        },
                        {
                            "title": "Premium SLA Terms",
                            "content": "Premium SLA available for 15% additional fee on base subscription. Includes 99.9% uptime guarantee, enhanced monitoring, and priority support with 4-hour response time.",
                            "keywords": ["premium SLA", "99.9%", "uptime", "enhanced", "pricing"]
                        }
                    ]
                },
                {
                    "id": "LD-DPA-001",
                    "title": "Data Processing Agreement",
                    "version": "2025-GDPR",
                    "updated_at": "2025-02-15",
                    "summary": "Terms governing the processing of customer data under GDPR and other privacy regulations",
                    "sections": [
                        {
                            "title": "Roles and Responsibilities",
                            "content": "Customer is the Data Controller. We act as the Data Processor. Customer retains full ownership and control over all customer data processed by our systems.",
                            "keywords": ["GDPR", "data controller", "data processor", "roles", "responsibilities"]
                        },
                        {
                            "title": "Sub-processors",
                            "content": "Current list of sub-processors available at company.com/subprocessors. Customer will be notified 30 days in advance of any new sub-processor additions.",
                            "keywords": ["sub-processor", "GDPR", "third party", "notification"]
                        },
                        {
                            "title": "Data Transfer Mechanisms",
                            "content": "Transfers outside the EEA are protected by EU Standard Contractual Clauses. We are certified under the EU-US Data Privacy Framework.",
                            "keywords": ["data transfer", "EEA", "EU", "Standard Contractual Clauses", "Privacy Shield"]
                        },
                        {
                            "title": "Breach Notification",
                            "content": "We will notify Customer without undue delay upon becoming aware of a personal data breach, and no later than 36 hours after discovery, providing sufficient information to meet GDPR 72-hour notification requirements.",
                            "keywords": ["breach", "notification", "GDPR", "72 hour", "data breach"]
                        }
                    ]
                },
                {
                    "id": "LD-MSA-001",
                    "title": "Master Services Agreement",
                    "version": "2025-Enterprise",
                    "updated_at": "2025-01-15",
                    "summary": "Standard terms for enterprise customers",
                    "sections": [
                        {
                            "title": "Intellectual Property",
                            "content": "Standard terms: We retain ownership of all IP in platform and customizations. For financial services customers: joint ownership of customer-specific algorithms and models can be negotiated with custom IP addendum.",
                            "keywords": ["intellectual property", "ownership", "customization", "financial services"]
                        },
                        {
                            "title": "Business Continuity",
                            "content": "Standard terms include 8-hour RTO and 4-hour RPO. Financial services tier available with 4-hour RTO and 15-minute RPO for 20% premium. Custom requirements available with minimum achievable RTO of 2 hours.",
                            "keywords": ["business continuity", "disaster recovery", "RTO", "RPO", "financial services"]
                        },
                        {
                            "title": "Payment Terms",
                            "content": "Standard: Annual payment in advance with net-30 terms. Enterprise options include quarterly payments (2% premium) and extended payment terms (net-45 at no cost, net-60 with 1% premium).",
                            "keywords": ["payment terms", "quarterly", "net-30", "net-60", "premium"]
                        },
                        {
                            "title": "Governing Law",
                            "content": "Standard jurisdiction is California. Acceptable alternatives include New York, Delaware, Texas, Illinois, or customer's primary jurisdiction for enterprise customers. New York law has no impact on compliance guarantees for financial services firms.",
                            "keywords": ["governing law", "jurisdiction", "California", "New York", "financial services"]
                        }
                    ]
                }
            ],
            "api_reference": [
                {
                    "id": "API-REF-001",
                    "title": "REST API Reference",
                    "version": "v3",
                    "updated_at": "2025-04-10",
                    "summary": "Complete reference for all REST API endpoints",
                    "sections": [
                        {
                            "title": "Authentication Endpoints",
                            "content": "POST /auth/token - Request access token. POST /auth/refresh - Refresh expired token.",
                            "keywords": ["authentication", "token", "refresh", "OAuth"]
                        },
                        {
                            "title": "Inventory Endpoints",
                            "content": "GET /inventory/items - List inventory items. POST /inventory/items - Create item. PUT /inventory/items/{id} - Update item. POST /inventory/batch - Batch update (limit 2MB payload). POST /inventory/delta - Delta updates for changed quantities only.",
                            "keywords": ["inventory", "API", "batch", "delta", "update"]
                        }
                    ]
                }
            ]
        }
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the document retrieval request.
        
        Args:
            parameters: Dictionary with parameters
                - document_type: Type of document to retrieve
                - keywords: Keywords to search for
                - version: Specific version of documentation
                - max_results: Maximum number of results to return
        
        Returns:
            Matching document sections
        """
        document_type = parameters["document_type"]
        keywords = parameters["keywords"]
        version = parameters.get("version")
        max_results = parameters.get("max_results", 5)
        
        # Check if document type exists
        if document_type not in self.document_database:
            return {
                "error": f"Document type '{document_type}' not found",
                "available_types": list(self.document_database.keys())
            }
        
        # Get all documents of the specified type
        documents = self.document_database[document_type]
        
        # Filter by version if specified
        if version:
            documents = [doc for doc in documents if doc["version"] == version]
        
        # No documents found
        if not documents:
            return {
                "found": False,
                "message": f"No documents found for type '{document_type}'" + (f" with version '{version}'" if version else "")
            }
        
        # Search for matching sections
        matching_sections = []
        for doc in documents:
            for section in doc["sections"]:
                score = self._calculate_match_score(section, keywords)
                if score > 0:
                    matching_sections.append({
                        "document_id": doc["id"],
                        "document_title": doc["title"],
                        "document_version": doc["version"],
                        "section_title": section["title"],
                        "content": section["content"],
                        "relevance_score": score
                    })
        
        # Sort by relevance score
        matching_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Limit results
        matching_sections = matching_sections[:max_results]
        
        return {
            "found": len(matching_sections) > 0,
            "document_type": document_type,
            "matching_sections": matching_sections,
            "count": len(matching_sections)
        }
    
    def _calculate_match_score(self, section: Dict[str, Any], keywords: List[str]) -> float:
        """
        Calculate match score between section and keywords.
        
        Args:
            section: Document section
            keywords: Search keywords
            
        Returns:
            Match score (0-1)
        """
        # Check section keywords
        section_keywords = section.get("keywords", [])
        direct_keyword_matches = sum(1 for k in keywords if k.lower() in [sk.lower() for sk in section_keywords])
        
        # Check section content
        content = section["content"].lower()
        title = section["title"].lower()
        
        # Count keyword occurrences in content
        content_matches = 0
        title_matches = 0
        
        for keyword in keywords:
            keyword = keyword.lower()
            
            # Exact keyword matches in content
            content_matches += content.count(keyword) * 2
            
            # Exact keyword matches in title
            title_matches += title.count(keyword) * 3
            
            # Partial matches in content (for multi-word keywords)
            if " " in keyword:
                parts = keyword.split()
                partial_matches = all(part in content for part in parts)
                if partial_matches:
                    content_matches += 1
        
        # Calculate final score
        total_score = direct_keyword_matches * 5 + content_matches + title_matches
        
        # Normalize score to 0-1 range
        max_possible_score = len(keywords) * 10  # Arbitrary maximum score
        normalized_score = min(total_score / max_possible_score, 1.0)
        
        return normalized_score