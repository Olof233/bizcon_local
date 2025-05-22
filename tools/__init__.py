"""
Tools package for bizCon framework.
"""
from typing import Dict, List, Any, Optional

from .base import BusinessTool
from .knowledge_base import KnowledgeBaseTool
from .product_catalog import ProductCatalogTool
from .pricing_calculator import PricingCalculatorTool
from .scheduler import SchedulerTool
from .customer_history import CustomerHistoryTool
from .document_retrieval import DocumentRetrievalTool
from .order_management import OrderManagementTool
from .support_ticket import SupportTicketTool


def get_default_tools() -> Dict[str, BusinessTool]:
    """
    Get the default set of business tools.
    
    Returns:
        Dictionary of tool_id to tool instance
    """
    return {
        "knowledge_base": KnowledgeBaseTool(),
        "product_catalog": ProductCatalogTool(),
        "pricing_calculator": PricingCalculatorTool(),
        "scheduler": SchedulerTool(),
        "customer_history": CustomerHistoryTool(),
        "document_retrieval": DocumentRetrievalTool(),
        "order_management": OrderManagementTool(),
        "support_ticket": SupportTicketTool()
    }


def get_tool_by_id(tool_id: str) -> Optional[BusinessTool]:
    """
    Get a tool instance by ID.
    
    Args:
        tool_id: Tool ID
        
    Returns:
        Tool instance or None if not found
    """
    tools = get_default_tools()
    return tools.get(tool_id)