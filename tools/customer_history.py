"""
Customer history tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random
import datetime
from dateutil.relativedelta import relativedelta

from .base import BusinessTool


class CustomerHistoryTool(BusinessTool):
    """
    Customer history tool for accessing customer account information and interaction history.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the customer history tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="customer_history",
            name="Customer History",
            description="Retrieve customer account information, purchase history, and support interactions",
            parameters={
                "customer_id": {
                    "type": "string",
                    "description": "Customer ID to look up",
                    "required": False
                },
                "company_name": {
                    "type": "string",
                    "description": "Company name to look up",
                    "required": False
                },
                "email": {
                    "type": "string",
                    "description": "Customer email to look up",
                    "required": False
                },
                "history_type": {
                    "type": "string",
                    "description": "Type of history to retrieve (e.g., 'purchases', 'support', 'billing', 'usage', 'all')",
                    "required": False
                },
                "time_period": {
                    "type": "string",
                    "description": "Time period to retrieve history for (e.g., '3m', '6m', '1y', '2y', 'all')",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Initialize mock customer database
        self._initialize_customer_database()
    
    def _initialize_customer_database(self) -> None:
        """Initialize the mock customer database."""
        # Current date used for generating relative dates
        now = datetime.datetime.now()
        
        self.customer_database = {
            "CUS-10001": {
                "customer_id": "CUS-10001",
                "company_name": "Acme Corp",
                "industry": "Manufacturing",
                "tier": "Enterprise",
                "contract_start": (now - relativedelta(years=2, months=3)).strftime("%Y-%m-%d"),
                "contract_end": (now + relativedelta(months=9)).strftime("%Y-%m-%d"),
                "primary_contact": {
                    "name": "John Smith",
                    "email": "john.smith@acmecorp.com",
                    "phone": "+1-555-123-4567",
                    "role": "IT Director"
                },
                "billing_contact": {
                    "name": "Amanda Johnson",
                    "email": "amanda.johnson@acmecorp.com",
                    "phone": "+1-555-123-4590",
                    "role": "Finance Manager"
                },
                "account_manager": "Sarah Williams",
                "customer_success_manager": "Michael Chen",
                "purchase_history": [
                    {
                        "order_id": "ORD-45678",
                        "date": (now - relativedelta(years=2, months=3)).strftime("%Y-%m-%d"),
                        "product": "Enterprise Suite",
                        "license_count": 500,
                        "amount": 175000.00,
                        "status": "Completed"
                    },
                    {
                        "order_id": "ORD-52341",
                        "date": (now - relativedelta(years=1, months=5)).strftime("%Y-%m-%d"),
                        "product": "Data Analytics Module",
                        "license_count": 50,
                        "amount": 25000.00,
                        "status": "Completed"
                    },
                    {
                        "order_id": "ORD-67890",
                        "date": (now - relativedelta(months=2)).strftime("%Y-%m-%d"),
                        "product": "API Access Premium",
                        "license_count": 10,
                        "amount": 15000.00,
                        "status": "Completed"
                    }
                ],
                "support_history": [
                    {
                        "ticket_id": "INC-54321",
                        "date": (now - relativedelta(months=6, days=15)).strftime("%Y-%m-%d"),
                        "issue_type": "Authentication",
                        "severity": "Medium",
                        "status": "Resolved",
                        "resolution_time": "3 days",
                        "satisfaction_score": 4
                    },
                    {
                        "ticket_id": "INC-58765",
                        "date": (now - relativedelta(months=3, days=8)).strftime("%Y-%m-%d"),
                        "issue_type": "Performance",
                        "severity": "High",
                        "status": "Resolved",
                        "resolution_time": "1 day",
                        "satisfaction_score": 5
                    },
                    {
                        "ticket_id": "INC-62143",
                        "date": (now - relativedelta(days=10)).strftime("%Y-%m-%d"),
                        "issue_type": "Feature Request",
                        "severity": "Low",
                        "status": "In Progress",
                        "resolution_time": "Ongoing",
                        "satisfaction_score": None
                    }
                ],
                "billing_history": [
                    {
                        "invoice_id": "INV-87654",
                        "date": (now - relativedelta(years=2, months=3)).strftime("%Y-%m-%d"),
                        "amount": 175000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=2, months=3, days=-5)).strftime("%Y-%m-%d")
                    },
                    {
                        "invoice_id": "INV-92345",
                        "date": (now - relativedelta(years=1, months=5)).strftime("%Y-%m-%d"),
                        "amount": 25000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=1, months=5, days=-7)).strftime("%Y-%m-%d")
                    },
                    {
                        "invoice_id": "INV-98765",
                        "date": (now - relativedelta(months=2)).strftime("%Y-%m-%d"),
                        "amount": 15000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(months=2, days=-3)).strftime("%Y-%m-%d")
                    }
                ],
                "usage_metrics": {
                    "active_users": 432,
                    "api_calls_monthly_avg": 870000,
                    "storage_used": "1.2 TB",
                    "feature_adoption": {
                        "analytics_dashboard": "85%",
                        "mobile_app": "62%",
                        "automated_workflows": "45%",
                        "integrations": "73%"
                    },
                    "login_frequency": "Daily",
                    "peak_usage_times": "Weekdays 9am-11am, 1pm-3pm EST"
                }
            },
            "CUS-10002": {
                "customer_id": "CUS-10002",
                "company_name": "TechCorp Solutions",
                "industry": "Technology",
                "tier": "Premium",
                "contract_start": (now - relativedelta(years=1, months=6)).strftime("%Y-%m-%d"),
                "contract_end": (now + relativedelta(years=1, months=6)).strftime("%Y-%m-%d"),
                "primary_contact": {
                    "name": "Lisa Chen",
                    "email": "lisa.chen@techcorp.com",
                    "phone": "+1-555-987-6543",
                    "role": "CTO"
                },
                "billing_contact": {
                    "name": "Robert Miller",
                    "email": "robert.miller@techcorp.com",
                    "phone": "+1-555-987-6500",
                    "role": "CFO"
                },
                "account_manager": "James Wilson",
                "customer_success_manager": "Emily Rodriguez",
                "purchase_history": [
                    {
                        "order_id": "ORD-34567",
                        "date": (now - relativedelta(years=1, months=6)).strftime("%Y-%m-%d"),
                        "product": "Premium Suite",
                        "license_count": 200,
                        "amount": 80000.00,
                        "status": "Completed"
                    },
                    {
                        "order_id": "ORD-38901",
                        "date": (now - relativedelta(months=9)).strftime("%Y-%m-%d"),
                        "product": "Integration Pack",
                        "license_count": 1,
                        "amount": 12000.00,
                        "status": "Completed"
                    }
                ],
                "support_history": [
                    {
                        "ticket_id": "INC-43210",
                        "date": (now - relativedelta(months=10)).strftime("%Y-%m-%d"),
                        "issue_type": "Integration",
                        "severity": "High",
                        "status": "Resolved",
                        "resolution_time": "4 days",
                        "satisfaction_score": 3
                    },
                    {
                        "ticket_id": "INC-45678",
                        "date": (now - relativedelta(months=5)).strftime("%Y-%m-%d"),
                        "issue_type": "Bug",
                        "severity": "Medium",
                        "status": "Resolved",
                        "resolution_time": "2 days",
                        "satisfaction_score": 4
                    }
                ],
                "billing_history": [
                    {
                        "invoice_id": "INV-76543",
                        "date": (now - relativedelta(years=1, months=6)).strftime("%Y-%m-%d"),
                        "amount": 80000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=1, months=6, days=-4)).strftime("%Y-%m-%d")
                    },
                    {
                        "invoice_id": "INV-78901",
                        "date": (now - relativedelta(months=9)).strftime("%Y-%m-%d"),
                        "amount": 12000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(months=9, days=-6)).strftime("%Y-%m-%d")
                    }
                ],
                "usage_metrics": {
                    "active_users": 178,
                    "api_calls_monthly_avg": 420000,
                    "storage_used": "750 GB",
                    "feature_adoption": {
                        "analytics_dashboard": "92%",
                        "mobile_app": "85%",
                        "automated_workflows": "76%",
                        "integrations": "90%"
                    },
                    "login_frequency": "Daily",
                    "peak_usage_times": "Weekdays 8am-5pm PST"
                }
            },
            "CUS-10003": {
                "customer_id": "CUS-10003",
                "company_name": "MegaRetail Inc",
                "industry": "Retail",
                "tier": "Enterprise",
                "contract_start": (now - relativedelta(years=3, months=1)).strftime("%Y-%m-%d"),
                "contract_end": (now + relativedelta(months=11)).strftime("%Y-%m-%d"),
                "primary_contact": {
                    "name": "David Wilson",
                    "email": "david.wilson@megaretail.com",
                    "phone": "+1-555-456-7890",
                    "role": "VP of Operations"
                },
                "billing_contact": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@megaretail.com",
                    "phone": "+1-555-456-7899",
                    "role": "Finance Director"
                },
                "account_manager": "Thomas Brown",
                "customer_success_manager": "Jennifer Lee",
                "purchase_history": [
                    {
                        "order_id": "ORD-23456",
                        "date": (now - relativedelta(years=3, months=1)).strftime("%Y-%m-%d"),
                        "product": "Enterprise Suite",
                        "license_count": 1000,
                        "amount": 350000.00,
                        "status": "Completed"
                    },
                    {
                        "order_id": "ORD-27890",
                        "date": (now - relativedelta(years=2)).strftime("%Y-%m-%d"),
                        "product": "POS Integration Module",
                        "license_count": 500,
                        "amount": 75000.00,
                        "status": "Completed"
                    },
                    {
                        "order_id": "ORD-29012",
                        "date": (now - relativedelta(years=1)).strftime("%Y-%m-%d"),
                        "product": "Customer Insights Module",
                        "license_count": 50,
                        "amount": 35000.00,
                        "status": "Completed"
                    }
                ],
                "support_history": [
                    {
                        "ticket_id": "INC-32109",
                        "date": (now - relativedelta(years=2, months=6)).strftime("%Y-%m-%d"),
                        "issue_type": "Performance",
                        "severity": "Critical",
                        "status": "Resolved",
                        "resolution_time": "1 day",
                        "satisfaction_score": 5
                    },
                    {
                        "ticket_id": "INC-34567",
                        "date": (now - relativedelta(years=1, months=4)).strftime("%Y-%m-%d"),
                        "issue_type": "Data Synchronization",
                        "severity": "High",
                        "status": "Resolved",
                        "resolution_time": "2 days",
                        "satisfaction_score": 4
                    },
                    {
                        "ticket_id": "INC-56789",
                        "date": (now - relativedelta(days=1)).strftime("%Y-%m-%d"),
                        "issue_type": "Performance",
                        "severity": "High",
                        "status": "In Progress",
                        "resolution_time": "Ongoing",
                        "satisfaction_score": None
                    }
                ],
                "billing_history": [
                    {
                        "invoice_id": "INV-65432",
                        "date": (now - relativedelta(years=3, months=1)).strftime("%Y-%m-%d"),
                        "amount": 350000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=3, months=1, days=-10)).strftime("%Y-%m-%d")
                    },
                    {
                        "invoice_id": "INV-67890",
                        "date": (now - relativedelta(years=2)).strftime("%Y-%m-%d"),
                        "amount": 75000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=2, days=-15)).strftime("%Y-%m-%d")
                    },
                    {
                        "invoice_id": "INV-69012",
                        "date": (now - relativedelta(years=1)).strftime("%Y-%m-%d"),
                        "amount": 35000.00,
                        "status": "Paid",
                        "payment_date": (now - relativedelta(years=1, days=-5)).strftime("%Y-%m-%d")
                    }
                ],
                "usage_metrics": {
                    "active_users": 875,
                    "api_calls_monthly_avg": 1500000,
                    "storage_used": "3.5 TB",
                    "feature_adoption": {
                        "analytics_dashboard": "95%",
                        "mobile_app": "78%",
                        "automated_workflows": "88%",
                        "integrations": "92%"
                    },
                    "login_frequency": "Daily",
                    "peak_usage_times": "Weekdays 7am-10pm EST, Weekends 9am-6pm EST"
                }
            }
        }
        
        # Create lookup indexes
        self._create_indexes()
    
    def _create_indexes(self) -> None:
        """Create lookup indexes for efficient querying."""
        self.company_index = {}
        self.email_index = {}
        
        for customer_id, customer_data in self.customer_database.items():
            # Index by company name
            company_name = customer_data["company_name"]
            self.company_index[company_name] = customer_id
            
            # Index by email addresses
            primary_email = customer_data["primary_contact"]["email"]
            self.email_index[primary_email] = customer_id
            
            billing_email = customer_data["billing_contact"]["email"]
            self.email_index[billing_email] = customer_id
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the customer history retrieval operation.
        
        Args:
            parameters: Dictionary with parameters
                - customer_id: Customer ID to look up
                - company_name: Company name to look up
                - email: Customer email to look up
                - history_type: Type of history to retrieve
                - time_period: Time period to retrieve history for
        
        Returns:
            Customer information and history data
        """
        # Determine the customer ID from provided parameters
        customer_id = None
        
        if "customer_id" in parameters:
            customer_id = parameters["customer_id"]
        elif "company_name" in parameters:
            company_name = parameters["company_name"]
            customer_id = self.company_index.get(company_name)
        elif "email" in parameters:
            email = parameters["email"]
            customer_id = self.email_index.get(email)
        
        if not customer_id or customer_id not in self.customer_database:
            return {
                "status": "error",
                "message": "Customer not found. Please verify the customer ID, company name, or email address."
            }
        
        # Get the customer data
        customer_data = self.customer_database[customer_id]
        
        # Determine what history to include
        history_type = parameters.get("history_type", "all").lower()
        
        # Apply time period filter if specified
        time_period = parameters.get("time_period", "all").lower()
        filter_date = None
        
        if time_period != "all":
            now = datetime.datetime.now()
            
            if time_period == "3m":
                filter_date = now - relativedelta(months=3)
            elif time_period == "6m":
                filter_date = now - relativedelta(months=6)
            elif time_period == "1y":
                filter_date = now - relativedelta(years=1)
            elif time_period == "2y":
                filter_date = now - relativedelta(years=2)
        
        # Prepare the response
        response = {
            "customer_id": customer_data["customer_id"],
            "company_name": customer_data["company_name"],
            "industry": customer_data["industry"],
            "tier": customer_data["tier"],
            "contract_start": customer_data["contract_start"],
            "contract_end": customer_data["contract_end"],
            "primary_contact": customer_data["primary_contact"],
            "account_manager": customer_data["account_manager"],
            "customer_success_manager": customer_data["customer_success_manager"]
        }
        
        # Add requested history sections
        if history_type in ["purchases", "all"]:
            if filter_date:
                response["purchase_history"] = [
                    purchase for purchase in customer_data["purchase_history"]
                    if datetime.datetime.strptime(purchase["date"], "%Y-%m-%d") >= filter_date
                ]
            else:
                response["purchase_history"] = customer_data["purchase_history"]
        
        if history_type in ["support", "all"]:
            if filter_date:
                response["support_history"] = [
                    ticket for ticket in customer_data["support_history"]
                    if datetime.datetime.strptime(ticket["date"], "%Y-%m-%d") >= filter_date
                ]
            else:
                response["support_history"] = customer_data["support_history"]
        
        if history_type in ["billing", "all"]:
            if filter_date:
                response["billing_history"] = [
                    invoice for invoice in customer_data["billing_history"]
                    if datetime.datetime.strptime(invoice["date"], "%Y-%m-%d") >= filter_date
                ]
            else:
                response["billing_history"] = customer_data["billing_history"]
        
        if history_type in ["usage", "all"]:
            response["usage_metrics"] = customer_data["usage_metrics"]
        
        return response