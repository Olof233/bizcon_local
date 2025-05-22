"""
Product catalog tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random

from .base import BusinessTool


class ProductCatalogTool(BusinessTool):
    """
    Product catalog tool for retrieving product information.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the product catalog tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="product_catalog",
            name="Product Catalog",
            description="Retrieve detailed information about products and services from the company catalog",
            parameters={
                "product_id": {
                    "type": "string",
                    "description": "Specific product ID to look up",
                    "required": False
                },
                "product_category": {
                    "type": "string",
                    "description": "Product category to search (e.g., 'data_analytics', 'cloud_services')",
                    "required": False
                },
                "industry": {
                    "type": "string",
                    "description": "Industry vertical to filter products by (e.g., 'healthcare', 'financial_services')",
                    "required": False
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Specific features to look for in products",
                    "required": False
                }
            },
            error_rate=error_rate
        )
        
        # Load the product catalog data
        self._load_product_catalog()
    
    def _load_product_catalog(self) -> None:
        """Load product catalog data from files."""
        self.product_data = []
        
        # Path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products")
        
        # Load product catalog files
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    try:
                        file_path = os.path.join(data_dir, filename)
                        with open(file_path, "r") as f:
                            products = json.load(f)
                            if isinstance(products, list):
                                self.product_data.extend(products)
                            else:
                                self.product_data.append(products)
                    except Exception as e:
                        print(f"Error loading product catalog file {filename}: {e}")
        
        # Create fallback data if no files were loaded
        if not self.product_data:
            self.product_data = [
                {
                    "product_id": "data_analytics_enterprise",
                    "name": "DataInsight Enterprise",
                    "category": "data_analytics",
                    "description": "Enterprise-grade data analytics platform for large organizations with advanced security and compliance features.",
                    "key_features": [
                        "Real-time data processing",
                        "Advanced visualization tools",
                        "Machine learning capabilities",
                        "Role-based access controls",
                        "Customizable dashboards",
                        "Automated reporting",
                        "Data integration with 200+ sources",
                        "Advanced security features",
                        "Compliance monitoring"
                    ],
                    "benefits": [
                        "Increase operational efficiency",
                        "Enhance decision making with data-driven insights",
                        "Improve regulatory compliance",
                        "Reduce data processing time by up to 70%",
                        "Centralize data management"
                    ],
                    "industries": [
                        "financial_services",
                        "healthcare",
                        "retail",
                        "manufacturing",
                        "telecommunications"
                    ],
                    "versions": [
                        "Standard",
                        "Professional",
                        "Enterprise",
                        "Enterprise Plus"
                    ]
                },
                {
                    "product_id": "data_management_healthcare",
                    "name": "HealthData Manager",
                    "category": "data_management",
                    "description": "Comprehensive data management solution designed specifically for healthcare organizations with HIPAA compliance built-in.",
                    "key_features": [
                        "HIPAA-compliant data storage",
                        "Patient data management",
                        "Electronic health record integration",
                        "Secure sharing capabilities",
                        "Audit logging",
                        "Advanced encryption (AES-256)",
                        "Role-based access controls",
                        "Multi-factor authentication",
                        "Automated compliance reporting"
                    ],
                    "benefits": [
                        "Ensure regulatory compliance",
                        "Streamline patient data management",
                        "Improve data security",
                        "Enhance care coordination",
                        "Reduce administrative overhead"
                    ],
                    "industries": [
                        "healthcare",
                        "insurance",
                        "pharmaceuticals"
                    ],
                    "versions": [
                        "Clinical Practice",
                        "Hospital",
                        "Enterprise Health System"
                    ],
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
                        "compliance": [
                            "HIPAA",
                            "HITECH",
                            "GDPR",
                            "SOC 2"
                        ]
                    }
                }
            ]
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the product catalog lookup.
        
        Args:
            parameters: Dictionary with parameters
                - product_id: Specific product ID to look up
                - product_category: Product category to search
                - industry: Industry vertical to filter by
                - features: Specific features to look for
        
        Returns:
            Product information matching the query parameters
        """
        product_id = parameters.get("product_id")
        product_category = parameters.get("product_category")
        industry = parameters.get("industry")
        features = parameters.get("features", [])
        
        # If product_id is provided, look up the specific product
        if product_id:
            product = next((p for p in self.product_data if p.get("product_id") == product_id), None)
            if product:
                return product
            else:
                return {"error": f"Product with ID '{product_id}' not found"}
        
        # Otherwise, filter products based on criteria
        filtered_products = self.product_data.copy()
        
        # Filter by category
        if product_category:
            filtered_products = [p for p in filtered_products if p.get("category") == product_category]
        
        # Filter by industry
        if industry:
            filtered_products = [p for p in filtered_products if industry in p.get("industries", [])]
        
        # Filter by features
        if features:
            # Calculate feature match score for each product
            scored_products = []
            for product in filtered_products:
                product_features = product.get("key_features", [])
                # Look in security_features too if available
                if "security_features" in product:
                    security = product["security_features"]
                    if "authentication" in security:
                        product_features.extend(security["authentication"])
                    if "compliance" in security:
                        product_features.extend(security["compliance"])
                
                # Flatten product features to strings for comparison
                flat_features = []
                for feature in product_features:
                    if isinstance(feature, str):
                        flat_features.append(feature.lower())
                    elif isinstance(feature, dict):
                        # Extract values from nested feature dictionaries
                        for value in feature.values():
                            if isinstance(value, str):
                                flat_features.append(value.lower())
                            elif isinstance(value, list):
                                flat_features.extend([v.lower() for v in value if isinstance(v, str)])
                
                # Count matching features
                match_count = 0
                for requested_feature in features:
                    requested_feature = requested_feature.lower()
                    if any(requested_feature in feature for feature in flat_features):
                        match_count += 1
                
                if match_count > 0:
                    scored_products.append((product, match_count))
            
            # Sort by match count and extract just the products
            scored_products.sort(key=lambda x: x[1], reverse=True)
            filtered_products = [p[0] for p in scored_products]
        
        # Return results
        if filtered_products:
            if len(filtered_products) == 1:
                return filtered_products[0]
            else:
                # Return a summary of matching products
                return [
                    {
                        "product_id": p.get("product_id"),
                        "name": p.get("name"),
                        "category": p.get("category"),
                        "description": p.get("description"),
                        "key_features": p.get("key_features")[:5] if len(p.get("key_features", [])) > 5 else p.get("key_features", [])
                    }
                    for p in filtered_products[:3]  # Limit to top 3 products
                ]
        else:
            return {"message": "No products found matching your criteria"}