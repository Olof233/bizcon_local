"""
Order management tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random
import datetime
from dateutil.relativedelta import relativedelta
import uuid

from .base import BusinessTool


class OrderManagementTool(BusinessTool):
    """
    Order management tool for checking order status, creating orders, and handling order-related operations.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the order management tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="order_management",
            name="Order Management",
            description="Check order status, create new orders, modify existing orders, and handle returns",
            parameters={
                "order_id": {
                    "type": "string",
                    "description": "Order ID to look up",
                    "required": False
                },
                "customer_id": {
                    "type": "string",
                    "description": "Customer ID to look up orders for",
                    "required": False
                },
                "company_name": {
                    "type": "string",
                    "description": "Company name to look up orders for",
                    "required": False
                },
                "time_period": {
                    "type": "string",
                    "description": "Time period to retrieve orders for (e.g., '30d', '90d', '6m', '1y', 'all')",
                    "required": False
                },
                "status": {
                    "type": "string",
                    "description": "Filter orders by status (e.g., 'pending', 'processing', 'shipped', 'delivered', 'cancelled')",
                    "required": False
                },
                "create_order": {
                    "type": "boolean",
                    "description": "Whether to create a new order",
                    "required": False
                },
                "update_order": {
                    "type": "boolean",
                    "description": "Whether to update an existing order",
                    "required": False
                },
                "cancel_order": {
                    "type": "boolean",
                    "description": "Whether to cancel an existing order",
                    "required": False
                },
                "product_id": {
                    "type": "string",
                    "description": "Product ID for the order",
                    "required": False
                },
                "product_name": {
                    "type": "string",
                    "description": "Product name for the order",
                    "required": False
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity for the order",
                    "required": False
                },
                "license_count": {
                    "type": "integer",
                    "description": "License count for software products",
                    "required": False
                },
                "shipping_address": {
                    "type": "object",
                    "description": "Shipping address for physical products",
                    "required": False
                },
                "billing_address": {
                    "type": "object",
                    "description": "Billing address for the order",
                    "required": False
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method for the order",
                    "required": False
                },
                "urgency": {
                    "type": "string",
                    "description": "Urgency level for the order (e.g., 'standard', 'expedited', 'rush')",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Initialize mock order database
        self._initialize_order_database()
    
    def _initialize_order_database(self) -> None:
        """Initialize the mock order database."""
        # Current date used for generating relative dates
        now = datetime.datetime.now()
        
        self.order_database = {
            "ORD-45678": {
                "order_id": "ORD-45678",
                "customer_id": "CUS-10001",
                "company_name": "Acme Corp",
                "order_date": (now - relativedelta(years=2, months=3)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-ENT-001",
                        "product_name": "Enterprise Suite",
                        "license_count": 500,
                        "unit_price": 350.00,
                        "total_price": 175000.00
                    }
                ],
                "subtotal": 175000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 175000.00,
                "payment_method": "Invoice NET-30",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=2, months=3, days=-25)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "123 Manufacturing Way",
                    "city": "Industrial Park",
                    "state": "CA",
                    "zip": "90210",
                    "country": "USA"
                },
                "notes": "Initial enterprise license purchase",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=2, months=3, days=-1)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=2, months=3, days=-1)).strftime("%Y-%m-%d")
            },
            "ORD-52341": {
                "order_id": "ORD-52341",
                "customer_id": "CUS-10001",
                "company_name": "Acme Corp",
                "order_date": (now - relativedelta(years=1, months=5)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-DAM-001",
                        "product_name": "Data Analytics Module",
                        "license_count": 50,
                        "unit_price": 500.00,
                        "total_price": 25000.00
                    }
                ],
                "subtotal": 25000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 25000.00,
                "payment_method": "Credit Card",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=1, months=5)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "123 Manufacturing Way",
                    "city": "Industrial Park",
                    "state": "CA",
                    "zip": "90210",
                    "country": "USA"
                },
                "notes": "Additional module for data team",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=1, months=5, days=-1)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=1, months=5, days=-1)).strftime("%Y-%m-%d")
            },
            "ORD-67890": {
                "order_id": "ORD-67890",
                "customer_id": "CUS-10001",
                "company_name": "Acme Corp",
                "order_date": (now - relativedelta(months=2)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-API-001",
                        "product_name": "API Access Premium",
                        "license_count": 10,
                        "unit_price": 1500.00,
                        "total_price": 15000.00
                    }
                ],
                "subtotal": 15000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 15000.00,
                "payment_method": "Invoice NET-30",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(months=1, days=5)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "123 Manufacturing Way",
                    "city": "Industrial Park",
                    "state": "CA",
                    "zip": "90210",
                    "country": "USA"
                },
                "notes": "API access add-on for integration project",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(months=2, days=-1)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(months=2, days=-1)).strftime("%Y-%m-%d")
            },
            "ORD-34567": {
                "order_id": "ORD-34567",
                "customer_id": "CUS-10002",
                "company_name": "TechCorp Solutions",
                "order_date": (now - relativedelta(years=1, months=6)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-PRE-001",
                        "product_name": "Premium Suite",
                        "license_count": 200,
                        "unit_price": 400.00,
                        "total_price": 80000.00
                    }
                ],
                "subtotal": 80000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 80000.00,
                "payment_method": "Wire Transfer",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=1, months=6, days=-10)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "456 Tech Boulevard",
                    "city": "Silicon Valley",
                    "state": "CA",
                    "zip": "94025",
                    "country": "USA"
                },
                "notes": "Initial subscription",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=1, months=6, days=-2)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=1, months=6, days=-2)).strftime("%Y-%m-%d")
            },
            "ORD-38901": {
                "order_id": "ORD-38901",
                "customer_id": "CUS-10002",
                "company_name": "TechCorp Solutions",
                "order_date": (now - relativedelta(months=9)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-INT-001",
                        "product_name": "Integration Pack",
                        "license_count": 1,
                        "unit_price": 12000.00,
                        "total_price": 12000.00
                    }
                ],
                "subtotal": 12000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 12000.00,
                "payment_method": "Credit Card",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(months=9)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "456 Tech Boulevard",
                    "city": "Silicon Valley",
                    "state": "CA",
                    "zip": "94025",
                    "country": "USA"
                },
                "notes": "Integration add-on for third-party systems",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(months=9, days=-1)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(months=9, days=-1)).strftime("%Y-%m-%d")
            },
            "ORD-23456": {
                "order_id": "ORD-23456",
                "customer_id": "CUS-10003",
                "company_name": "MegaRetail Inc",
                "order_date": (now - relativedelta(years=3, months=1)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-ENT-001",
                        "product_name": "Enterprise Suite",
                        "license_count": 1000,
                        "unit_price": 350.00,
                        "total_price": 350000.00
                    }
                ],
                "subtotal": 350000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 350000.00,
                "payment_method": "Invoice NET-45",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=3, months=0, days=5)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "789 Retail Row",
                    "city": "Commerce City",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                },
                "notes": "Enterprise-wide deployment",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=3, months=1, days=-3)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=3, months=1, days=-2)).strftime("%Y-%m-%d")
            },
            "ORD-27890": {
                "order_id": "ORD-27890",
                "customer_id": "CUS-10003",
                "company_name": "MegaRetail Inc",
                "order_date": (now - relativedelta(years=2)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-POS-001",
                        "product_name": "POS Integration Module",
                        "license_count": 500,
                        "unit_price": 150.00,
                        "total_price": 75000.00
                    }
                ],
                "subtotal": 75000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 75000.00,
                "payment_method": "Invoice NET-30",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=2, days=-28)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "789 Retail Row",
                    "city": "Commerce City",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                },
                "notes": "POS integration for all retail locations",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=2, days=-2)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=2, days=-2)).strftime("%Y-%m-%d")
            },
            "ORD-29012": {
                "order_id": "ORD-29012",
                "customer_id": "CUS-10003",
                "company_name": "MegaRetail Inc",
                "order_date": (now - relativedelta(years=1)).strftime("%Y-%m-%d"),
                "status": "Delivered",
                "products": [
                    {
                        "product_id": "PROD-CIM-001",
                        "product_name": "Customer Insights Module",
                        "license_count": 50,
                        "unit_price": 700.00,
                        "total_price": 35000.00
                    }
                ],
                "subtotal": 35000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 35000.00,
                "payment_method": "Credit Card",
                "payment_status": "Paid",
                "payment_date": (now - relativedelta(years=1)).strftime("%Y-%m-%d"),
                "shipping_address": None,
                "billing_address": {
                    "street": "789 Retail Row",
                    "city": "Commerce City",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                },
                "notes": "Analytics add-on for marketing department",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now - relativedelta(years=1, days=-1)).strftime("%Y-%m-%d"),
                "actual_delivery_date": (now - relativedelta(years=1, days=-1)).strftime("%Y-%m-%d")
            },
            "ORD-72345": {
                "order_id": "ORD-72345",
                "customer_id": "CUS-10001",
                "company_name": "Acme Corp",
                "order_date": (now - relativedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "Processing",
                "products": [
                    {
                        "product_id": "PROD-SUP-001",
                        "product_name": "Premium Support Plan",
                        "license_count": 1,
                        "unit_price": 20000.00,
                        "total_price": 20000.00
                    }
                ],
                "subtotal": 20000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 20000.00,
                "payment_method": "Invoice NET-30",
                "payment_status": "Pending",
                "payment_date": None,
                "shipping_address": None,
                "billing_address": {
                    "street": "123 Manufacturing Way",
                    "city": "Industrial Park",
                    "state": "CA",
                    "zip": "90210",
                    "country": "USA"
                },
                "notes": "Annual support plan renewal",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now + relativedelta(days=2)).strftime("%Y-%m-%d"),
                "actual_delivery_date": None
            },
            "ORD-75678": {
                "order_id": "ORD-75678",
                "customer_id": "CUS-10002",
                "company_name": "TechCorp Solutions",
                "order_date": (now - relativedelta(days=1)).strftime("%Y-%m-%d"),
                "status": "Pending",
                "products": [
                    {
                        "product_id": "PROD-TRN-001",
                        "product_name": "Advanced Training Package",
                        "license_count": 10,
                        "unit_price": 500.00,
                        "total_price": 5000.00
                    }
                ],
                "subtotal": 5000.00,
                "tax": 0.00,
                "shipping": 0.00,
                "total": 5000.00,
                "payment_method": "Credit Card",
                "payment_status": "Authorized",
                "payment_date": None,
                "shipping_address": None,
                "billing_address": {
                    "street": "456 Tech Boulevard",
                    "city": "Silicon Valley",
                    "state": "CA",
                    "zip": "94025",
                    "country": "USA"
                },
                "notes": "Training for new team members",
                "delivery_method": "Electronic",
                "tracking_number": None,
                "expected_delivery_date": (now + relativedelta(days=3)).strftime("%Y-%m-%d"),
                "actual_delivery_date": None
            }
        }
        
        # Create lookup indexes
        self._create_indexes()
    
    def _create_indexes(self) -> None:
        """Create lookup indexes for efficient querying."""
        self.customer_orders = {}
        self.company_orders = {}
        
        for order_id, order_data in self.order_database.items():
            # Index by customer ID
            customer_id = order_data["customer_id"]
            if customer_id not in self.customer_orders:
                self.customer_orders[customer_id] = []
            self.customer_orders[customer_id].append(order_id)
            
            # Index by company name
            company_name = order_data["company_name"]
            if company_name not in self.company_orders:
                self.company_orders[company_name] = []
            self.company_orders[company_name].append(order_id)
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the order management operation.
        
        Args:
            parameters: Dictionary with parameters
                - order_id: Order ID to look up
                - customer_id: Customer ID to look up orders for
                - company_name: Company name to look up orders for
                - time_period: Time period to retrieve orders for
                - status: Filter orders by status
                - create_order: Whether to create a new order
                - update_order: Whether to update an existing order
                - cancel_order: Whether to cancel an existing order
                - product_id: Product ID for the order
                - product_name: Product name for the order
                - quantity: Quantity for the order
                - license_count: License count for software products
                - shipping_address: Shipping address for physical products
                - billing_address: Billing address for the order
                - payment_method: Payment method for the order
                - urgency: Urgency level for the order
        
        Returns:
            Order information or operation result
        """
        # Check if we need to create, update or cancel an order
        if parameters.get("create_order"):
            return self._create_order(parameters)
        
        if parameters.get("update_order"):
            return self._update_order(parameters)
        
        if parameters.get("cancel_order"):
            return self._cancel_order(parameters)
        
        # Lookup existing order(s)
        if "order_id" in parameters:
            # Look up a specific order
            order_id = parameters["order_id"]
            return self._get_order_by_id(order_id)
        
        # Look up multiple orders
        return self._get_orders(parameters)
    
    def _get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """
        Get an order by its ID.
        
        Args:
            order_id: Order ID to look up
            
        Returns:
            Order information or error message
        """
        if order_id in self.order_database:
            return {
                "status": "success",
                "order": self.order_database[order_id]
            }
        else:
            return {
                "status": "error",
                "message": f"Order {order_id} not found."
            }
    
    def _get_orders(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get multiple orders based on filter criteria.
        
        Args:
            parameters: Filter parameters
                
        Returns:
            List of order information or error message
        """
        order_ids = []
        
        # Get orders by customer ID or company name
        if "customer_id" in parameters:
            customer_id = parameters["customer_id"]
            if customer_id in self.customer_orders:
                order_ids = self.customer_orders[customer_id]
            else:
                return {
                    "status": "error",
                    "message": f"No orders found for customer {customer_id}."
                }
        elif "company_name" in parameters:
            company_name = parameters["company_name"]
            if company_name in self.company_orders:
                order_ids = self.company_orders[company_name]
            else:
                return {
                    "status": "error",
                    "message": f"No orders found for company '{company_name}'."
                }
        else:
            # Return all orders if no customer filter
            order_ids = list(self.order_database.keys())
        
        # Apply time period filter if specified
        time_period = parameters.get("time_period", "all").lower()
        filter_date = None
        
        if time_period != "all":
            now = datetime.datetime.now()
            
            if time_period == "30d":
                filter_date = now - relativedelta(days=30)
            elif time_period == "90d":
                filter_date = now - relativedelta(days=90)
            elif time_period == "6m":
                filter_date = now - relativedelta(months=6)
            elif time_period == "1y":
                filter_date = now - relativedelta(years=1)
        
        # Apply status filter if specified
        status_filter = parameters.get("status")
        
        # Filter and sort the orders
        filtered_orders = []
        
        for order_id in order_ids:
            order = self.order_database[order_id]
            
            # Apply time period filter
            if filter_date:
                order_date = datetime.datetime.strptime(order["order_date"], "%Y-%m-%d")
                if order_date < filter_date:
                    continue
            
            # Apply status filter
            if status_filter and order["status"].lower() != status_filter.lower():
                continue
            
            filtered_orders.append(order)
        
        # Sort by order date (newest first)
        filtered_orders.sort(key=lambda x: x["order_date"], reverse=True)
        
        return {
            "status": "success",
            "order_count": len(filtered_orders),
            "orders": filtered_orders
        }
    
    def _create_order(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order.
        
        Args:
            parameters: Order parameters
                
        Returns:
            New order information or error message
        """
        # Validate required parameters
        required_params = ["customer_id", "product_id", "product_name"]
        missing_params = [param for param in required_params if param not in parameters]
        
        if missing_params:
            return {
                "status": "error",
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }
        
        # Get customer information
        customer_id = parameters["customer_id"]
        company_name = None
        
        # In a real implementation, we would look up the customer information from a database
        # For the mock implementation, we'll use a simple mapping
        customer_map = {
            "CUS-10001": "Acme Corp",
            "CUS-10002": "TechCorp Solutions",
            "CUS-10003": "MegaRetail Inc"
        }
        
        if customer_id in customer_map:
            company_name = customer_map[customer_id]
        else:
            # In a mock system, we'll just use a placeholder
            company_name = "Unknown Company"
        
        # Generate a new order ID
        new_order_id = f"ORD-{random.randint(80000, 99999)}"
        
        # Calculate pricing based on product and quantity
        product_id = parameters["product_id"]
        product_name = parameters["product_name"]
        license_count = parameters.get("license_count", 1)
        
        # In a real implementation, we would look up the product pricing from a database
        # For the mock implementation, we'll use some simple price calculations
        unit_price = 0.0
        if "ENT" in product_id:
            unit_price = 350.00
        elif "PRE" in product_id:
            unit_price = 400.00
        elif "API" in product_id:
            unit_price = 1500.00
        elif "DAM" in product_id or "CIM" in product_id:
            unit_price = 700.00
        elif "INT" in product_id:
            unit_price = 12000.00
        elif "POS" in product_id:
            unit_price = 150.00
        elif "SUP" in product_id:
            unit_price = 20000.00
        elif "TRN" in product_id:
            unit_price = 500.00
        else:
            unit_price = 1000.00  # Default price for unknown products
        
        total_price = unit_price * license_count
        
        # Create the new order
        now = datetime.datetime.now()
        
        # Determine delivery estimates based on urgency
        urgency = parameters.get("urgency", "standard").lower()
        delivery_days = 5  # Default for standard
        
        if urgency == "expedited":
            delivery_days = 3
        elif urgency == "rush":
            delivery_days = 1
        
        new_order = {
            "order_id": new_order_id,
            "customer_id": customer_id,
            "company_name": company_name,
            "order_date": now.strftime("%Y-%m-%d"),
            "status": "Pending",
            "products": [
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "license_count": license_count,
                    "unit_price": unit_price,
                    "total_price": total_price
                }
            ],
            "subtotal": total_price,
            "tax": 0.00,  # For simplicity, no tax for software licenses
            "shipping": 0.00,  # For simplicity, no shipping for digital products
            "total": total_price,
            "payment_method": parameters.get("payment_method", "Invoice NET-30"),
            "payment_status": "Pending",
            "payment_date": None,
            "shipping_address": parameters.get("shipping_address"),
            "billing_address": parameters.get("billing_address", {
                "street": "Unknown",
                "city": "Unknown",
                "state": "Unknown",
                "zip": "Unknown",
                "country": "Unknown"
            }),
            "notes": parameters.get("notes", ""),
            "delivery_method": "Electronic",
            "tracking_number": None,
            "expected_delivery_date": (now + relativedelta(days=delivery_days)).strftime("%Y-%m-%d"),
            "actual_delivery_date": None
        }
        
        # Add to database
        self.order_database[new_order_id] = new_order
        
        # Update indexes
        if customer_id not in self.customer_orders:
            self.customer_orders[customer_id] = []
        self.customer_orders[customer_id].append(new_order_id)
        
        if company_name not in self.company_orders:
            self.company_orders[company_name] = []
        self.company_orders[company_name].append(new_order_id)
        
        return {
            "status": "success",
            "message": f"Order {new_order_id} created successfully.",
            "order": new_order
        }
    
    def _update_order(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing order.
        
        Args:
            parameters: Order parameters
                
        Returns:
            Updated order information or error message
        """
        # Validate required parameters
        if "order_id" not in parameters:
            return {
                "status": "error",
                "message": "Missing required parameter: order_id"
            }
        
        order_id = parameters["order_id"]
        
        if order_id not in self.order_database:
            return {
                "status": "error",
                "message": f"Order {order_id} not found."
            }
        
        # Get the existing order
        order = self.order_database[order_id]
        
        # Check if the order can be updated
        if order["status"] in ["Delivered", "Cancelled"]:
            return {
                "status": "error",
                "message": f"Cannot update order {order_id} because it is already {order['status']}."
            }
        
        # Update allowed fields
        updatable_fields = ["status", "payment_method", "payment_status", "notes"]
        
        for field in updatable_fields:
            if field in parameters:
                order[field] = parameters[field]
        
        # If payment status changed to Paid, update payment date
        if "payment_status" in parameters and parameters["payment_status"] == "Paid":
            order["payment_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # If status changed to Delivered, update actual delivery date
        if "status" in parameters and parameters["status"] == "Delivered":
            order["actual_delivery_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Update the database
        self.order_database[order_id] = order
        
        return {
            "status": "success",
            "message": f"Order {order_id} updated successfully.",
            "order": order
        }
    
    def _cancel_order(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            parameters: Order parameters
                
        Returns:
            Cancelled order information or error message
        """
        # Validate required parameters
        if "order_id" not in parameters:
            return {
                "status": "error",
                "message": "Missing required parameter: order_id"
            }
        
        order_id = parameters["order_id"]
        
        if order_id not in self.order_database:
            return {
                "status": "error",
                "message": f"Order {order_id} not found."
            }
        
        # Get the existing order
        order = self.order_database[order_id]
        
        # Check if the order can be cancelled
        if order["status"] in ["Delivered", "Cancelled"]:
            return {
                "status": "error",
                "message": f"Cannot cancel order {order_id} because it is already {order['status']}."
            }
        
        # Cancel the order
        order["status"] = "Cancelled"
        order["notes"] = (order["notes"] + " - " + parameters.get("cancellation_reason", "Cancelled by customer")).strip()
        
        # Update the database
        self.order_database[order_id] = order
        
        return {
            "status": "success",
            "message": f"Order {order_id} cancelled successfully.",
            "order": order
        }