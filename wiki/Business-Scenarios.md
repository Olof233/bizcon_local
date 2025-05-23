# Business Scenarios

bizCon includes 8 carefully designed business scenarios that test LLMs across different professional contexts. Each scenario involves multi-turn conversations, tool integration, and domain-specific knowledge requirements.

## 📋 Scenario Overview

| Scenario | ID | Complexity | Industry | Key Skills Tested |
|----------|----|-----------:|----------|-------------------|
| [Product Inquiry](#product-inquiry) | `product_inquiry_001` | Medium | Retail/Tech | Product knowledge, comparison, recommendations |
| [Technical Support](#technical-support) | `technical_support_001` | High | Technology | Troubleshooting, tool usage, escalation |
| [Contract Negotiation](#contract-negotiation) | `contract_negotiation_001` | High | Legal/Sales | Negotiation, pricing, terms analysis |
| [Appointment Scheduling](#appointment-scheduling) | `appointment_scheduling_001` | Medium | Healthcare | Calendar coordination, conflict resolution |
| [Compliance Inquiry](#compliance-inquiry) | `compliance_inquiry_001` | High | Finance/Legal | Regulatory knowledge, documentation |
| [Implementation Planning](#implementation-planning) | `implementation_planning_001` | High | Technology | Project scoping, timeline estimation |
| [Service Complaints](#service-complaints) | `service_complaints_001` | Medium | Customer Service | Empathy, problem-solving, retention |
| [Multi-Department Coordination](#multi-department) | `multi_department_001` | Very High | Enterprise | Cross-functional communication |

## 🎯 Detailed Scenario Descriptions

### Product Inquiry

**Purpose**: Tests the model's ability to understand complex product requirements and provide tailored recommendations.

**Conversation Flow**:
1. Customer asks about enterprise software solutions
2. Model should probe for specific requirements
3. Customer provides budget and feature needs
4. Model recommends suitable products with comparisons
5. Customer asks follow-up questions about integration

**Required Tools**:
- Product Catalog
- Pricing Calculator
- Knowledge Base

**Evaluation Focus**:
- Accurate product information retrieval
- Relevant recommendations based on requirements
- Clear feature comparisons
- Professional consultative approach

**Example Interaction**:
```
Customer: "I need a CRM solution for my 50-person sales team"
AI: [Retrieves product catalog] "I can help you find the right CRM. 
     What's your budget range and key features needed?"
Customer: "Budget is $10-15k/year, need pipeline management and reporting"
AI: [Uses pricing calculator] "Based on your needs, I recommend..."
```

### Technical Support

**Purpose**: Evaluates troubleshooting abilities and technical problem-solving skills.

**Conversation Flow**:
1. Customer reports a technical issue
2. Model performs initial diagnosis
3. Customer provides error details
4. Model suggests troubleshooting steps
5. Issue escalation if unresolved

**Required Tools**:
- Knowledge Base
- Support Ticket System
- Customer History

**Evaluation Focus**:
- Systematic troubleshooting approach
- Clear technical communication
- Appropriate tool usage for diagnosis
- Escalation judgment

**Example Interaction**:
```
Customer: "Our API integration stopped working this morning"
AI: [Checks customer history] "I see you're using our v2.3 API. 
     Can you share any error messages?"
Customer: "Getting 401 authentication errors"
AI: [Searches knowledge base] "This often indicates expired credentials..."
```

### Contract Negotiation

**Purpose**: Tests negotiation skills, pricing flexibility, and business acumen.

**Conversation Flow**:
1. Customer inquires about enterprise pricing
2. Model presents standard terms
3. Customer negotiates for better rates
4. Model counters with value propositions
5. Agreement on final terms

**Required Tools**:
- Pricing Calculator
- Document Retrieval
- Customer History

**Evaluation Focus**:
- Negotiation strategy
- Value articulation
- Flexible pricing within bounds
- Professional relationship management

**Example Interaction**:
```
Customer: "Your standard price seems high for our startup"
AI: [Retrieves pricing tiers] "I understand budget concerns. 
     Let me check startup discount options..."
Customer: "We need at least 30% off to make this work"
AI: "I can offer 25% with annual commitment, plus free onboarding..."
```

### Appointment Scheduling

**Purpose**: Assesses calendar coordination and scheduling conflict resolution.

**Conversation Flow**:
1. Customer requests appointment
2. Model checks availability
3. Scheduling conflict arises
4. Model proposes alternatives
5. Confirmation and follow-up

**Required Tools**:
- Appointment Scheduler
- Customer History

**Evaluation Focus**:
- Efficient scheduling process
- Conflict resolution skills
- Clear communication of options
- Professional courtesy

**Example Interaction**:
```
Customer: "I need to schedule a demo for next Tuesday at 2 PM"
AI: [Checks scheduler] "I see that slot is taken. 
     Would 3 PM work, or should we look at Wednesday?"
Customer: "Tuesday is better, any morning slots?"
AI: "Yes, I have 10 AM and 11:30 AM available..."
```

### Compliance Inquiry

**Purpose**: Tests regulatory knowledge and ability to provide compliance guidance.

**Conversation Flow**:
1. Customer asks about compliance requirements
2. Model identifies relevant regulations
3. Customer describes specific scenario
4. Model provides detailed guidance
5. Documentation recommendations

**Required Tools**:
- Knowledge Base
- Document Retrieval

**Evaluation Focus**:
- Regulatory accuracy
- Risk awareness communication
- Appropriate disclaimers
- Document references

**Example Interaction**:
```
Customer: "Does our data processing need GDPR compliance?"
AI: [Searches regulations] "If you process EU resident data, yes. 
     Let me explain the key requirements..."
Customer: "We have some EU customers but servers are in US"
AI: "Data location doesn't exempt you from GDPR. You'll need..."
```

### Implementation Planning

**Purpose**: Evaluates project scoping and technical planning capabilities.

**Conversation Flow**:
1. Customer describes project needs
2. Model assesses requirements
3. Detailed scoping questions
4. Timeline and resource estimation
5. Implementation roadmap

**Required Tools**:
- Product Catalog
- Knowledge Base
- Pricing Calculator

**Evaluation Focus**:
- Requirement gathering skills
- Realistic timeline estimates
- Resource planning accuracy
- Risk identification

**Example Interaction**:
```
Customer: "We want to migrate 10TB to your cloud platform"
AI: "I'll help plan this migration. What's your current infrastructure?"
Customer: "On-premise servers, mixed Windows/Linux"
AI: [Calculates requirements] "For 10TB, I estimate 2-3 weeks..."
```

### Service Complaints

**Purpose**: Tests complaint handling, empathy, and customer retention skills.

**Conversation Flow**:
1. Customer expresses dissatisfaction
2. Model acknowledges and empathizes
3. Investigation of issue
4. Resolution proposal
5. Retention efforts

**Required Tools**:
- Customer History
- Support Ticket System
- Order Management

**Evaluation Focus**:
- Empathetic communication
- Problem resolution approach
- Retention strategies
- Service recovery

**Example Interaction**:
```
Customer: "This is the third outage this month! Unacceptable!"
AI: [Reviews history] "I sincerely apologize for the disruptions. 
     Let me investigate and ensure this is resolved..."
Customer: "We're considering switching providers"
AI: "I understand your frustration. Here's what I can offer..."
```

### Multi-Department Coordination

**Purpose**: Tests ability to coordinate across different business functions.

**Conversation Flow**:
1. Complex request spanning departments
2. Initial assessment and routing
3. Coordination requirements identified
4. Multi-stakeholder communication
5. Integrated solution delivery

**Required Tools**:
- All available tools
- Cross-functional data access

**Evaluation Focus**:
- Holistic problem understanding
- Cross-functional coordination
- Communication clarity
- Solution integration

**Example Interaction**:
```
Customer: "We need sales data integrated with our support metrics"
AI: "This requires coordination between Sales and Support teams. 
     Let me gather requirements from both perspectives..."
Customer: "Also need finance approval for the integration cost"
AI: [Coordinates across systems] "I'll set up a meeting with all stakeholders..."
```

## 🎮 Running Specific Scenarios

### CLI Usage

```bash
# Run single scenario
bizcon run --scenarios product_inquiry_001

# Run multiple scenarios
bizcon run --scenarios product_inquiry_001 technical_support_001

# Run all scenarios
bizcon run --all-scenarios
```

### Python API

```python
from bizcon import run_evaluation

# Run specific scenarios
results = run_evaluation(
    scenarios=["product_inquiry_001", "contract_negotiation_001"],
    models=["gpt-4", "claude-3-opus"]
)
```

## 📊 Scenario Metrics

Each scenario is evaluated on:
- **Completion Rate**: Successfully completing all conversation turns
- **Tool Usage Score**: Appropriate and effective tool utilization
- **Response Quality**: Accuracy and completeness of information
- **Business Outcome**: Achievement of scenario objectives

## 🔧 Creating Custom Scenarios

To add your own scenarios:

1. Create a new file in `scenarios/`
2. Extend the `BusinessScenario` base class
3. Define conversation flow and evaluation criteria

```python
from scenarios.base import BusinessScenario, register_scenario

@register_scenario
class CustomScenario(BusinessScenario):
    def __init__(self):
        super().__init__()
        self.id = "custom_scenario_001"
        self.name = "Custom Business Scenario"
        self.conversation_flow = [...]
```

---

<p align="center">
  <strong>Explore the tools that power these scenarios</strong><br>
  <a href="Business-Tools">View Business Tools →</a>
</p>