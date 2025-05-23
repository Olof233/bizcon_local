# Business Tools

bizCon simulates 8 enterprise business tools that LLMs can interact with during conversations. These tools test the models' ability to integrate with business systems and use them effectively to solve real-world problems.

## 🛠️ Tool Overview

| Tool | Purpose | Key Functions | Data Source |
|------|---------|---------------|-------------|
| [Knowledge Base](#knowledge-base) | FAQ & documentation search | Search, retrieve articles | `/data/knowledge_base/` |
| [Product Catalog](#product-catalog) | Product information system | Search, filter, compare | `/data/products/` |
| [Pricing Calculator](#pricing-calculator) | Dynamic pricing computation | Calculate, apply discounts | `/data/pricing/` |
| [Appointment Scheduler](#appointment-scheduler) | Calendar management | Check availability, book | In-memory calendar |
| [Customer History](#customer-history) | Past interaction lookup | Search, retrieve history | Mock customer data |
| [Document Retrieval](#document-retrieval) | Contract/document access | Search, retrieve docs | Mock documents |
| [Order Management](#order-management) | Order processing system | Create, update, track | Mock order data |
| [Support Ticket](#support-ticket) | Ticket management | Create, update, search | Mock ticket data |

## 📚 Tool Descriptions

### Knowledge Base

**Purpose**: Provides access to company documentation, FAQs, and technical guides.

**Functions**:
```python
{
    "name": "search_knowledge_base",
    "description": "Search company knowledge base for information",
    "parameters": {
        "query": "Search query string",
        "category": "Optional: docs, faq, guides"
    }
}
```

**Example Usage**:
```json
{
    "tool": "search_knowledge_base",
    "arguments": {
        "query": "API authentication",
        "category": "docs"
    }
}
```

**Response Format**:
```json
{
    "results": [
        {
            "title": "API Authentication Guide",
            "content": "To authenticate with our API...",
            "relevance": 0.95,
            "category": "docs"
        }
    ]
}
```

**Mock Data**: Technical documentation, FAQs about products, troubleshooting guides

### Product Catalog

**Purpose**: Enterprise product information management system.

**Functions**:
```python
{
    "name": "search_products",
    "description": "Search and filter product catalog",
    "parameters": {
        "query": "Product search terms",
        "filters": {
            "category": "Software category",
            "price_range": "Min-max price",
            "features": ["Required features"]
        }
    }
}
```

**Example Usage**:
```json
{
    "tool": "search_products",
    "arguments": {
        "query": "CRM",
        "filters": {
            "category": "Sales",
            "price_range": "1000-5000"
        }
    }
}
```

**Response Format**:
```json
{
    "products": [
        {
            "id": "prod_001",
            "name": "SalesPro CRM",
            "description": "Enterprise CRM solution",
            "price": 3500,
            "features": ["Pipeline management", "Reporting"],
            "category": "Sales"
        }
    ]
}
```

**Mock Data**: Enterprise software products with detailed specifications

### Pricing Calculator

**Purpose**: Calculates dynamic pricing based on various factors.

**Functions**:
```python
{
    "name": "calculate_price",
    "description": "Calculate pricing with discounts and terms",
    "parameters": {
        "product_id": "Product identifier",
        "quantity": "Number of licenses/units",
        "term": "Subscription term (monthly/annual)",
        "discount_code": "Optional discount code"
    }
}
```

**Example Usage**:
```json
{
    "tool": "calculate_price",
    "arguments": {
        "product_id": "prod_001",
        "quantity": 50,
        "term": "annual",
        "discount_code": "STARTUP30"
    }
}
```

**Response Format**:
```json
{
    "base_price": 175000,
    "discount": 52500,
    "final_price": 122500,
    "per_user_price": 2450,
    "term": "annual",
    "savings": "30% startup discount applied"
}
```

**Mock Data**: Pricing tiers, discount rules, volume pricing

### Appointment Scheduler

**Purpose**: Manages calendar availability and appointment booking.

**Functions**:
```python
{
    "name": "check_availability",
    "description": "Check calendar availability",
    "parameters": {
        "date": "YYYY-MM-DD",
        "duration": "Minutes (30, 60, etc.)",
        "time_preference": "morning/afternoon/evening"
    }
}

{
    "name": "book_appointment",
    "description": "Book an appointment slot",
    "parameters": {
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "duration": "Minutes",
        "attendee": "Attendee name",
        "purpose": "Meeting purpose"
    }
}
```

**Example Usage**:
```json
{
    "tool": "check_availability",
    "arguments": {
        "date": "2025-05-25",
        "duration": 60,
        "time_preference": "morning"
    }
}
```

**Response Format**:
```json
{
    "available_slots": [
        {"time": "09:00", "duration": 60},
        {"time": "10:30", "duration": 60},
        {"time": "11:00", "duration": 60}
    ],
    "date": "2025-05-25"
}
```

**Mock Data**: Pre-populated calendar with realistic availability patterns

### Customer History

**Purpose**: Retrieves past customer interactions and purchase history.

**Functions**:
```python
{
    "name": "get_customer_history",
    "description": "Retrieve customer interaction history",
    "parameters": {
        "customer_id": "Customer identifier",
        "history_type": "all/purchases/support/interactions",
        "limit": "Number of records"
    }
}
```

**Example Usage**:
```json
{
    "tool": "get_customer_history",
    "arguments": {
        "customer_id": "cust_12345",
        "history_type": "support",
        "limit": 5
    }
}
```

**Response Format**:
```json
{
    "customer": {
        "id": "cust_12345",
        "name": "Acme Corp",
        "tier": "Enterprise"
    },
    "history": [
        {
            "date": "2025-05-15",
            "type": "support",
            "description": "API integration issue",
            "resolved": true
        }
    ]
}
```

**Mock Data**: Customer profiles with transaction and support history

### Document Retrieval

**Purpose**: Access contracts, agreements, and business documents.

**Functions**:
```python
{
    "name": "search_documents",
    "description": "Search and retrieve business documents",
    "parameters": {
        "query": "Search terms",
        "document_type": "contract/agreement/policy/guide",
        "customer_id": "Optional customer filter"
    }
}
```

**Example Usage**:
```json
{
    "tool": "search_documents",
    "arguments": {
        "query": "service level agreement",
        "document_type": "contract",
        "customer_id": "cust_12345"
    }
}
```

**Response Format**:
```json
{
    "documents": [
        {
            "id": "doc_001",
            "title": "Enterprise SLA",
            "type": "contract",
            "summary": "99.9% uptime guarantee...",
            "last_updated": "2025-01-15"
        }
    ]
}
```

**Mock Data**: Template contracts, SLAs, policies

### Order Management

**Purpose**: Process and track customer orders.

**Functions**:
```python
{
    "name": "create_order",
    "description": "Create a new order",
    "parameters": {
        "customer_id": "Customer identifier",
        "products": [{"id": "product_id", "quantity": 1}],
        "payment_terms": "Payment terms"
    }
}

{
    "name": "get_order_status",
    "description": "Check order status",
    "parameters": {
        "order_id": "Order identifier"
    }
}
```

**Example Usage**:
```json
{
    "tool": "create_order",
    "arguments": {
        "customer_id": "cust_12345",
        "products": [
            {"id": "prod_001", "quantity": 50}
        ],
        "payment_terms": "net30"
    }
}
```

**Response Format**:
```json
{
    "order_id": "ord_78901",
    "status": "pending",
    "total": 122500,
    "created": "2025-05-23T10:30:00Z",
    "payment_terms": "net30"
}
```

**Mock Data**: Order templates, status workflows

### Support Ticket

**Purpose**: Create and manage customer support tickets.

**Functions**:
```python
{
    "name": "create_ticket",
    "description": "Create a support ticket",
    "parameters": {
        "customer_id": "Customer identifier",
        "subject": "Ticket subject",
        "description": "Issue description",
        "priority": "low/medium/high/critical"
    }
}

{
    "name": "update_ticket",
    "description": "Update ticket status",
    "parameters": {
        "ticket_id": "Ticket identifier",
        "status": "open/in_progress/resolved/closed",
        "notes": "Update notes"
    }
}
```

**Example Usage**:
```json
{
    "tool": "create_ticket",
    "arguments": {
        "customer_id": "cust_12345",
        "subject": "API Authentication Error",
        "description": "Getting 401 errors when...",
        "priority": "high"
    }
}
```

**Response Format**:
```json
{
    "ticket_id": "tkt_45678",
    "status": "open",
    "priority": "high",
    "assigned_to": "Tech Support Team",
    "created": "2025-05-23T11:00:00Z"
}
```

**Mock Data**: Ticket templates, priority matrices

## 🔄 Tool Integration

### OpenAI Function Calling Format

All tools follow OpenAI's function calling specification:

```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "What the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
}
```

### Error Handling

Tools can simulate errors based on configuration:

```yaml
tools:
  error_rate: 0.1  # 10% chance of tool errors
  error_types:
    - "timeout"
    - "not_found"
    - "permission_denied"
```

## 📊 Tool Usage Metrics

The framework tracks:
- **Call Frequency**: How often each tool is used
- **Success Rate**: Percentage of successful tool calls
- **Response Time**: Tool execution latency
- **Relevance Score**: How well tool results match the query

## 🧪 Testing Tools

### Mock Mode
Tools operate with mock data by default:
```python
tool = KnowledgeBase(mock_mode=True)
result = tool.execute(query="API docs")
```

### Real Integration
Tools can be extended for real system integration:
```python
class RealKnowledgeBase(KnowledgeBase):
    def execute(self, **kwargs):
        # Connect to real knowledge base
        return real_system_response
```

## 🔧 Adding Custom Tools

To create new tools:

1. Create a new file in `tools/`
2. Extend the `BusinessTool` base class
3. Implement required methods

```python
from tools.base import BusinessTool, register_tool

@register_tool
class CustomTool(BusinessTool):
    def get_definition(self):
        return {
            "name": "custom_tool",
            "description": "What it does",
            "parameters": {...}
        }
    
    def execute(self, **kwargs):
        # Tool logic here
        return {"result": "data"}
```

---

<p align="center">
  <strong>Learn how tools are evaluated</strong><br>
  <a href="Evaluation-System">View Evaluation System →</a>
</p>