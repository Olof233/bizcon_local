"""
Knowledge base tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import re

from .base import BusinessTool


class KnowledgeBaseTool(BusinessTool):
    """
    Knowledge base tool for retrieving business information.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the knowledge base tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="knowledge_base",
            name="Knowledge Base",
            description="Search the company knowledge base for information about products, services, policies, and procedures",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query string",
                    "required": True
                },
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Categories to search within (e.g., 'products', 'policies', 'implementation', 'training', 'support')",
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
        
        # Load the knowledge base data
        self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> None:
        """Load knowledge base data from files."""
        self.kb_data = {}
        
        # Path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base")
        
        # Load knowledge base files
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".json"):
                    try:
                        file_path = os.path.join(data_dir, filename)
                        with open(file_path, "r") as f:
                            category = filename.split(".")[0]
                            self.kb_data[category] = json.load(f)
                    except Exception as e:
                        print(f"Error loading knowledge base file {filename}: {e}")
        
        # Create fallback data if no files were loaded
        if not self.kb_data:
            self.kb_data = {
                "technical_faq": [
                    {
                        "id": "faq-001",
                        "question": "What is the typical implementation timeline for enterprise deployments?",
                        "answer": "Our enterprise software implementations typically take 10-12 weeks, divided into several phases: initial assessment (1-2 weeks), system configuration (3-4 weeks), data migration (2-3 weeks), testing (2 weeks), and training and deployment (2 weeks). Each implementation is assigned a dedicated implementation manager who coordinates the process.",
                        "categories": ["implementation", "enterprise", "timeline"]
                    },
                    {
                        "id": "faq-002",
                        "question": "What training options are available for new customers?",
                        "answer": "We offer multiple training options to ensure your team gets the most out of our solutions: 1) On-site training workshops (typically 2 days), 2) Virtual training sessions (8 hours total, scheduled flexibly), 3) Self-paced learning modules in our customer portal, and 4) Admin-specific advanced training. All enterprise plans include a training package, with additional sessions available for purchase.",
                        "categories": ["training", "implementation", "support"]
                    },
                    {
                        "id": "faq-003",
                        "question": "What support is included during implementation?",
                        "answer": "During implementation, customers receive premium support including: a dedicated implementation manager, 24/7 technical support with priority response times, access to our complete knowledge base and implementation guides, and weekly progress meetings. For healthcare implementations, we also provide compliance specialists to ensure all regulatory requirements are met.",
                        "categories": ["implementation", "support", "healthcare"]
                    },
                    {
                        "id": "faq-004",
                        "question": "Do you offer validation environments for testing?",
                        "answer": "Yes, all enterprise customers receive access to a dedicated validation environment that mirrors their production setup. This allows for thorough testing of configurations, customizations, and integrations before deploying to production. The validation environment is maintained throughout your subscription and can be used for testing upgrades and new features.",
                        "categories": ["implementation", "testing", "validation", "healthcare"]
                    }
                ]
            }
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the knowledge base search.
        
        Args:
            parameters: Dictionary with parameters
                - query: Search query string
                - categories: Optional list of categories to search within
                - max_results: Optional maximum number of results to return
        
        Returns:
            List of knowledge base articles matching the query
        """
        query = parameters.get("query", "").lower()
        categories = parameters.get("categories", [])
        max_results = parameters.get("max_results", 3)
        
        if not query:
            return {"error": "Query is required"}
        
        # Search for relevant articles
        results = []
        
        for category, articles in self.kb_data.items():
            # Skip if categories specified and this category not included
            if categories and not any(cat in categories for cat in [category] + [article.get("categories", []) for article in articles]):
                continue
                
            for article in articles:
                # Check if query terms match article content
                article_text = (
                    article.get("question", "") + " " + 
                    article.get("answer", "") + " " + 
                    " ".join(article.get("categories", []))
                ).lower()
                
                # Simple keyword matching (could be enhanced with more sophisticated search)
                query_terms = query.split()
                matches = sum(1 for term in query_terms if term in article_text)
                
                if matches > 0:
                    # Calculate a simple relevance score
                    relevance = matches / len(query_terms)
                    
                    # Add category match bonus
                    if categories:
                        article_categories = article.get("categories", [])
                        category_matches = sum(1 for cat in categories if cat in article_categories)
                        relevance += 0.2 * (category_matches / len(categories))
                    
                    results.append({
                        "id": article.get("id"),
                        "question": article.get("question"),
                        "answer": article.get("answer"),
                        "categories": article.get("categories", []),
                        "relevance": relevance
                    })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        results = results[:max_results]
        
        # Remove relevance scores from final output
        for result in results:
            del result["relevance"]
        
        return results