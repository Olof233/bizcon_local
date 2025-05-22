"""
Support ticket tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random
import datetime
import uuid

from .base import BusinessTool


class SupportTicketTool(BusinessTool):
    """
    Support ticket tool for checking and creating support tickets.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the support ticket tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="support_ticket",
            name="Support Ticket System",
            description="Check existing tickets or create new support tickets",
            parameters={
                "check_organization": {
                    "type": "string",
                    "description": "Organization name to check for existing tickets",
                    "required": False
                },
                "issue_type": {
                    "type": "string",
                    "description": "Type of issue (e.g., 'authentication', 'performance', 'data', 'integration')",
                    "required": False
                },
                "severity": {
                    "type": "string",
                    "description": "Issue severity ('low', 'medium', 'high', 'critical')",
                    "required": False
                },
                "ticket_id": {
                    "type": "string",
                    "description": "Specific ticket ID to check",
                    "required": False
                },
                "create_ticket": {
                    "type": "boolean",
                    "description": "Whether to create a new ticket",
                    "required": False
                },
                "customer_name": {
                    "type": "string",
                    "description": "Customer name for the new ticket",
                    "required": False
                },
                "issue_description": {
                    "type": "string",
                    "description": "Description of the issue",
                    "required": False
                },
                "component": {
                    "type": "string",
                    "description": "System component with the issue",
                    "required": False
                },
                "environment": {
                    "type": "string",
                    "description": "Environment (production, staging, development)",
                    "required": False
                },
                "version": {
                    "type": "string",
                    "description": "Software version with the issue",
                    "required": False
                },
                "workaround_requested": {
                    "type": "boolean",
                    "description": "Whether a workaround is requested",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Initialize mock ticket database
        self._initialize_ticket_database()
    
    def _initialize_ticket_database(self) -> None:
        """Initialize the mock ticket database."""
        self.ticket_database = {
            "Acme Corp": [
                {
                    "ticket_id": "INC-54321",
                    "created_at": "2025-05-20T14:23:15Z",
                    "status": "Open",
                    "issue_type": "authentication",
                    "severity": "medium",
                    "description": "SSO authentication issues after identity provider update",
                    "affected_users": "All users",
                    "assigned_to": "Authentication Team",
                    "environment": "Production",
                    "component": "Identity Service",
                    "version": "3.5.2",
                    "resolution_eta": "2025-05-22T18:00:00Z",
                    "updates": [
                        {
                            "timestamp": "2025-05-20T15:12:33Z",
                            "author": "Support Engineer",
                            "note": "Confirmed issue with Okta SSO integration. Working with Okta on resolution."
                        },
                        {
                            "timestamp": "2025-05-21T09:45:12Z",
                            "author": "Authentication Team Lead",
                            "note": "Identified root cause as certificate expiration. New certificate being deployed."
                        }
                    ]
                }
            ],
            "MegaRetail Inc": [
                {
                    "ticket_id": "INC-56789",
                    "created_at": "2025-05-21T08:17:22Z",
                    "status": "In Progress",
                    "issue_type": "performance",
                    "severity": "high",
                    "description": "Order processing API experiencing high latency during peak hours",
                    "affected_users": "All retail stores",
                    "assigned_to": "Platform Engineering",
                    "environment": "Production",
                    "component": "Order Processing Service",
                    "version": "2.3.0",
                    "resolution_eta": "2025-05-23T12:00:00Z",
                    "updates": [
                        {
                            "timestamp": "2025-05-21T10:23:45Z",
                            "author": "Support Engineer",
                            "note": "Initial investigation shows database connection pool saturation. Increasing pool size as temporary measure."
                        }
                    ]
                }
            ]
        }
        
        # Create known outages/incidents
        self.known_issues = [
            {
                "incident_id": "INC-GLOBAL-123",
                "status": "In Progress",
                "issue_type": "authentication",
                "description": "Okta SSO integration experiencing intermittent failures due to Okta service disruption",
                "affected_customers": ["Acme Corp", "TechCorp", "GlobalFinance"],
                "started_at": "2025-05-22T08:45:00Z",
                "estimated_resolution": "2025-05-22T14:30:00Z",
                "workaround": "Temporary direct login credentials can be provided for critical users"
            },
            {
                "incident_id": "INC-GLOBAL-124",
                "status": "Investigating",
                "issue_type": "performance",
                "description": "API latency increased for inventory services in US-East region",
                "affected_customers": ["MegaRetail Inc", "SupplyChain Co", "DistributorsUnited"],
                "started_at": "2025-05-21T14:20:00Z",
                "estimated_resolution": "2025-05-22T20:00:00Z",
                "workaround": "Use batch operations with smaller payload sizes and implement exponential backoff"
            }
        ]
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the support ticket operation.
        
        Args:
            parameters: Dictionary with parameters
                - check_organization: Organization to check for existing tickets
                - issue_type: Type of issue
                - severity: Issue severity
                - ticket_id: Specific ticket ID to check
                - create_ticket: Whether to create a new ticket
                - customer_name: Customer name for the new ticket
                - issue_description: Description of the issue
                - component: System component with the issue
                - environment: Environment
                - version: Software version
                - workaround_requested: Whether a workaround is requested
        
        Returns:
            Ticket information or creation result
        """
        # Check for a specific ticket by ID
        if "ticket_id" in parameters:
            return self._get_ticket_by_id(parameters["ticket_id"])
        
        # Check for existing tickets for an organization
        if "check_organization" in parameters:
            org_name = parameters["check_organization"]
            issue_type = parameters.get("issue_type")
            severity = parameters.get("severity")
            
            # Check for global incidents that might affect this organization
            matching_incidents = self._check_for_incidents(org_name, issue_type)
            if matching_incidents:
                return {
                    "matching_incidents": matching_incidents,
                    "organization": org_name,
                    "message": f"Found {len(matching_incidents)} active incidents that may affect your organization"
                }
            
            # Check for organization-specific tickets
            return self._get_tickets_for_organization(org_name, issue_type, severity)
        
        # Create a new ticket
        if parameters.get("create_ticket", False):
            return self._create_ticket(parameters)
        
        # If no specific operation was requested, return an error
        return {
            "error": "Invalid operation. Please specify check_organization, ticket_id, or create_ticket=true"
        }
    
    def _get_ticket_by_id(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get a specific ticket by ID.
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Ticket information
        """
        # Look through all organizations
        for org, tickets in self.ticket_database.items():
            for ticket in tickets:
                if ticket["ticket_id"] == ticket_id:
                    return {
                        "found": True,
                        "ticket": ticket,
                        "organization": org
                    }
        
        # Check if it's a global incident
        for incident in self.known_issues:
            if incident["incident_id"] == ticket_id:
                return {
                    "found": True,
                    "incident": incident,
                    "is_global_incident": True
                }
        
        return {
            "found": False,
            "message": f"No ticket found with ID {ticket_id}"
        }
    
    def _get_tickets_for_organization(self, 
                                     org_name: str, 
                                     issue_type: Optional[str] = None,
                                     severity: Optional[str] = None) -> Dict[str, Any]:
        """
        Get tickets for an organization, optionally filtered by type and severity.
        
        Args:
            org_name: Organization name
            issue_type: Issue type filter
            severity: Severity filter
            
        Returns:
            List of matching tickets
        """
        if org_name not in self.ticket_database:
            return {
                "found": False,
                "organization": org_name,
                "message": "No tickets found for this organization"
            }
        
        tickets = self.ticket_database[org_name]
        
        # Apply filters
        if issue_type:
            tickets = [t for t in tickets if t["issue_type"] == issue_type]
        
        if severity:
            tickets = [t for t in tickets if t["severity"] == severity]
        
        return {
            "found": len(tickets) > 0,
            "organization": org_name,
            "tickets": tickets,
            "count": len(tickets)
        }
    
    def _check_for_incidents(self, 
                            org_name: str, 
                            issue_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Check for global incidents that might affect an organization.
        
        Args:
            org_name: Organization name
            issue_type: Issue type
            
        Returns:
            List of matching incidents
        """
        matching_incidents = []
        
        for incident in self.known_issues:
            # Check if this organization is affected
            if org_name in incident["affected_customers"]:
                # Apply issue type filter if provided
                if issue_type and incident["issue_type"] != issue_type:
                    continue
                    
                matching_incidents.append(incident)
        
        return matching_incidents
    
    def _create_ticket(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new support ticket.
        
        Args:
            parameters: Dictionary with ticket creation parameters
            
        Returns:
            Ticket creation result
        """
        customer_name = parameters.get("customer_name")
        if not customer_name:
            return {"error": "customer_name is required to create a ticket"}
        
        issue_description = parameters.get("issue_description")
        if not issue_description:
            return {"error": "issue_description is required to create a ticket"}
        
        # Generate a ticket ID
        ticket_id = f"INC-{random.randint(10000, 99999)}"
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Create the ticket
        new_ticket = {
            "ticket_id": ticket_id,
            "created_at": timestamp,
            "status": "Open",
            "issue_type": parameters.get("issue_type", "general"),
            "severity": parameters.get("severity", "medium"),
            "description": issue_description,
            "environment": parameters.get("environment", "Production"),
            "component": parameters.get("component", "Unknown"),
            "version": parameters.get("version", "Unknown"),
            "assigned_to": self._assign_team(parameters),
            "updates": []
        }
        
        # Calculate estimated resolution time based on severity
        severity = parameters.get("severity", "medium")
        eta_hours = {
            "low": random.randint(48, 72),
            "medium": random.randint(24, 48),
            "high": random.randint(4, 24),
            "critical": random.randint(1, 4)
        }.get(severity, 24)
        
        eta = datetime.datetime.now() + datetime.timedelta(hours=eta_hours)
        new_ticket["resolution_eta"] = eta.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Add workaround information if requested
        if parameters.get("workaround_requested"):
            workaround = self._generate_workaround(parameters)
            new_ticket["workaround"] = workaround
        
        # Add the ticket to the database
        if customer_name not in self.ticket_database:
            self.ticket_database[customer_name] = []
            
        self.ticket_database[customer_name].append(new_ticket)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Ticket {ticket_id} created successfully",
            "ticket": new_ticket
        }
    
    def _assign_team(self, parameters: Dict[str, Any]) -> str:
        """
        Assign a support team based on the issue details.
        
        Args:
            parameters: Issue parameters
            
        Returns:
            Team assignment
        """
        issue_type = parameters.get("issue_type", "general")
        component = parameters.get("component", "Unknown")
        severity = parameters.get("severity", "medium")
        
        # Mapping of issue types to teams
        team_mapping = {
            "authentication": "Identity & Access Management Team",
            "performance": "Performance Engineering Team",
            "data": "Data Services Team",
            "integration": "Integration Services Team",
            "billing": "Billing Support Team",
            "security": "Security Response Team"
        }
        
        # Component-specific assignments
        component_mapping = {
            "inventory_api": "Inventory Services Team",
            "identity_service": "Identity & Access Management Team",
            "order_processing": "Order Management Team",
            "reporting": "Analytics & Reporting Team"
        }
        
        # Get the team based on component first, then issue type
        assigned_team = component_mapping.get(component, team_mapping.get(issue_type, "General Support"))
        
        # For critical issues, add escalation info
        if severity == "critical":
            assigned_team += " (Escalated to Senior Engineering)"
            
        return assigned_team
    
    def _generate_workaround(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a workaround based on the issue details.
        
        Args:
            parameters: Issue parameters
            
        Returns:
            Workaround information
        """
        issue_type = parameters.get("issue_type", "general")
        component = parameters.get("component", "Unknown")
        
        # Generic workarounds by issue type
        workarounds = {
            "authentication": {
                "steps": [
                    "Provide temporary direct authentication credentials",
                    "Bypass SSO for critical users",
                    "Use API tokens for automated processes"
                ],
                "estimated_setup_time": "30 minutes",
                "limitations": "Reduced security features, manual user setup required"
            },
            "performance": {
                "steps": [
                    "Reduce batch sizes",
                    "Implement caching for frequently accessed data",
                    "Schedule operations during off-peak hours",
                    "Implement exponential backoff retry strategy"
                ],
                "estimated_setup_time": "1-2 hours",
                "limitations": "Reduced throughput, increased complexity"
            },
            "integration": {
                "steps": [
                    "Switch to alternative endpoints",
                    "Implement client-side throttling",
                    "Use asynchronous processing for non-critical operations"
                ],
                "estimated_setup_time": "2-4 hours",
                "limitations": "May require code changes, potential data synchronization delays"
            }
        }
        
        # Component-specific workarounds
        component_workarounds = {
            "inventory_api": {
                "steps": [
                    "Use individual item updates instead of batch",
                    "Implement delta updates (only changed quantities)",
                    "Reduce payload size by limiting fields",
                    "Increase timeout settings on client side"
                ],
                "estimated_setup_time": "1-2 hours",
                "limitations": "Higher API call volume, potential rate limiting"
            }
        }
        
        # Get the appropriate workaround
        workaround = component_workarounds.get(component, workarounds.get(issue_type, {
            "steps": [
                "Contact support for custom workaround",
                "Check knowledge base for similar issues"
            ],
            "estimated_setup_time": "Varies",
            "limitations": "Generic solution may not address specific needs"
        }))
        
        # Add availability time
        now = datetime.datetime.now()
        availability_minutes = random.randint(15, 60)
        availability_time = now + datetime.timedelta(minutes=availability_minutes)
        
        workaround["available_from"] = availability_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return workaround