"""
Pricing calculator tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import math

from .base import BusinessTool


class PricingCalculatorTool(BusinessTool):
    """
    Pricing calculator tool for generating product pricing quotes.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the pricing calculator tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="pricing_calculator",
            name="Pricing Calculator",
            description="Calculate pricing for products and services based on configuration options",
            parameters={
                "product_id": {
                    "type": "string",
                    "description": "Product ID to calculate pricing for",
                    "required": True
                },
                "users": {
                    "type": "integer",
                    "description": "Number of users",
                    "required": False
                },
                "term_length": {
                    "type": "integer",
                    "description": "Contract term length in months (12, 24, or 36)",
                    "required": False
                },
                "tier": {
                    "type": "string",
                    "description": "Product tier (e.g., 'standard', 'professional', 'enterprise')",
                    "required": False
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Additional features to include",
                    "required": False
                },
                "deployment": {
                    "type": "string",
                    "description": "Deployment type ('cloud' or 'on_premise')",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Load the pricing data
        self._load_pricing_data()
    
    def _load_pricing_data(self) -> None:
        """Load pricing data from files."""
        self.pricing_data = {}
        
        # Path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricing")
        
        # Load pricing data files
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    try:
                        file_path = os.path.join(data_dir, filename)
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            # Handle both list and dict formats
                            if isinstance(data, list):
                                # Convert list to dict using plan_id as key
                                for item in data:
                                    if isinstance(item, dict) and "plan_id" in item:
                                        self.pricing_data[item["plan_id"]] = item
                            elif isinstance(data, dict):
                                self.pricing_data.update(data)
                    except Exception as e:
                        print(f"Error loading pricing data file {filename}: {e}")
        
        # Create fallback data if no files were loaded
        if not self.pricing_data:
            self.pricing_data = {
                "data_analytics_enterprise": {
                    "model": "per_user_subscription",
                    "base_price": {
                        "standard": 800,
                        "professional": 1000,
                        "enterprise": 1200,
                        "enterprise_plus": 1500
                    },
                    "discount_tiers": {
                        "1-19": 0,
                        "20-49": 0.10,
                        "50-99": 0.15,
                        "100-249": 0.20,
                        "250+": 0.25
                    },
                    "term_discounts": {
                        "12": 0,
                        "24": 0.10,
                        "36": 0.15
                    },
                    "additional_features": {
                        "advanced_security": 200,
                        "financial_compliance": 300,
                        "ai_analytics": 500,
                        "priority_support": 100,
                        "custom_integrations": 400
                    },
                    "deployment_options": {
                        "cloud": 0,
                        "on_premise": 5000  # One-time fee
                    }
                },
                "data_management_healthcare": {
                    "model": "per_user_subscription",
                    "base_price": {
                        "clinical_practice": 1200,
                        "hospital": 1500,
                        "enterprise_health_system": 1800
                    },
                    "discount_tiers": {
                        "1-19": 0,
                        "20-49": 0.10,
                        "50-99": 0.15,
                        "100-249": 0.20,
                        "250+": 0.25
                    },
                    "term_discounts": {
                        "12": 0,
                        "24": 0.10,
                        "36": 0.15
                    },
                    "additional_features": {
                        "patient_portal_integration": 300,
                        "advanced_analytics": 500,
                        "telehealth_module": 400,
                        "research_data_warehouse": 800,
                        "custom_compliance_reporting": 350
                    },
                    "deployment_options": {
                        "cloud": 0,
                        "on_premise": 8000  # One-time fee
                    }
                }
            }
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the pricing calculation.
        
        Args:
            parameters: Dictionary with parameters
                - product_id: Product ID to calculate pricing for
                - users: Number of users
                - term_length: Contract term length in months
                - tier: Product tier
                - features: Additional features to include
                - deployment: Deployment type
        
        Returns:
            Detailed pricing breakdown
        """
        product_id = parameters.get("product_id")
        users = parameters.get("users", 1)
        term_length = parameters.get("term_length", 12)
        tier = parameters.get("tier", "").lower()
        features = parameters.get("features", [])
        deployment = parameters.get("deployment", "cloud").lower()
        
        # Check if we have pricing for this product
        if product_id not in self.pricing_data:
            return {"error": f"Pricing information not available for product '{product_id}'"}
        
        pricing = self.pricing_data[product_id]
        
        # Get base price based on tier
        if not tier and "base_price" in pricing:
            # Default to the lowest tier if not specified
            tier = list(pricing["base_price"].keys())[0]
        
        if "base_price" in pricing and tier in pricing["base_price"]:
            base_price = pricing["base_price"][tier]
        else:
            return {"error": f"Invalid tier '{tier}' for product '{product_id}'"}
        
        # Calculate user volume discount
        discount_rate = 0
        if "discount_tiers" in pricing:
            for tier_range, rate in pricing["discount_tiers"].items():
                min_users, max_users = map(lambda x: int(x) if x != "+" else float("inf"), tier_range.split("-"))
                if min_users <= users <= max_users:
                    discount_rate = rate
                    break
        
        # Calculate term discount
        term_discount = 0
        if "term_discounts" in pricing and str(term_length) in pricing["term_discounts"]:
            term_discount = pricing["term_discounts"][str(term_length)]
        
        # Calculate additional feature costs
        feature_costs = []
        if "additional_features" in pricing:
            for feature in features:
                if feature in pricing["additional_features"]:
                    feature_price = pricing["additional_features"][feature]
                    feature_costs.append({
                        "feature": feature,
                        "price": feature_price,
                        "total": feature_price * users if pricing["model"] == "per_user_subscription" else feature_price
                    })
        
        # Calculate deployment cost
        deployment_cost = 0
        if "deployment_options" in pricing and deployment in pricing["deployment_options"]:
            deployment_cost = pricing["deployment_options"][deployment]
        
        # Calculate subtotal and discounts
        if pricing["model"] == "per_user_subscription":
            subtotal = base_price * users
            volume_discount = subtotal * discount_rate
            term_discount_amount = (subtotal - volume_discount) * term_discount
        else:
            subtotal = base_price
            volume_discount = 0
            term_discount_amount = subtotal * term_discount
        
        # Add feature costs
        for feature in feature_costs:
            subtotal += feature["total"]
        
        # Calculate total with discounts
        total = subtotal - volume_discount - term_discount_amount + deployment_cost
        
        # Build the response
        annual_total = total
        monthly_total = total / 12
        
        return {
            "product_id": product_id,
            "tier": tier,
            "users": users,
            "term_length": term_length,
            "pricing_details": {
                "base_price_per_user": base_price if pricing["model"] == "per_user_subscription" else None,
                "base_price_flat": base_price if pricing["model"] != "per_user_subscription" else None,
                "subtotal": subtotal,
                "volume_discount_rate": f"{discount_rate:.0%}",
                "volume_discount_amount": volume_discount,
                "term_discount_rate": f"{term_discount:.0%}",
                "term_discount_amount": term_discount_amount,
                "additional_features": feature_costs,
                "deployment_option": deployment,
                "deployment_cost": deployment_cost
            },
            "total": {
                "annual": math.ceil(annual_total),
                "monthly": math.ceil(monthly_total),
                "currency": "USD"
            },
            "note": "This is an estimated price. Contact sales for a detailed quote."
        }