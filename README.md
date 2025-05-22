# bizCon: Business Conversation Evaluation Framework for LLMs

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Olib-AI/bizcon/actions)
[![GitHub Issues](https://img.shields.io/github/issues/Olib-AI/bizcon)](https://github.com/Olib-AI/bizcon/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Olib-AI/bizcon)](https://github.com/Olib-AI/bizcon/stargazers)

**A comprehensive open-source framework for benchmarking Large Language Models on business conversation capabilities**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [📊 Sample Results](#-sample-results) • [🤝 Contributing](#-contributing) • [💬 Community](#-community)

</div>

---

## 📋 Table of Contents

<details>
<summary><strong>📖 Click to view full navigation</strong></summary>

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🚀 Quick Start](#-quick-start)
- [📖 Documentation](#-documentation)
- [📊 Sample Results](#-sample-results)
- [🏗️ Advanced Usage](#️-advanced-usage)
- [🤝 Contributing](#-contributing)
- [🧪 Testing & Validation](#-testing--validation)
- [💬 Community](#-community)
- [📈 Roadmap](#-roadmap)

</details>

---

## 🎯 Overview

bizCon is a specialized evaluation framework designed to benchmark Large Language Models (LLMs) on realistic business conversation scenarios. Unlike generic benchmarks, bizCon focuses on practical business use cases involving professional communication, tool integration, and domain-specific knowledge.

### Why bizCon?

- **Business-Focused**: Evaluates models on real-world business scenarios
- **Multi-Dimensional**: Assesses 5 key aspects of business communication
- **Tool Integration**: Tests models' ability to use business tools effectively
- **Comparative Analysis**: Benchmark multiple models side-by-side
- **Enterprise-Ready**: Professional reporting and analysis capabilities

## ✨ Key Features

### 🎭 **Diverse Business Scenarios**
- **Product Inquiries**: Enterprise software consultations
- **Technical Support**: Complex troubleshooting and API integration
- **Contract Negotiation**: SaaS agreements and enterprise deals
- **Appointment Scheduling**: Multi-stakeholder coordination
- **Compliance Inquiries**: Regulatory and data privacy questions
- **Implementation Planning**: Software deployment strategies
- **Service Complaints**: Customer service and dispute resolution
- **Multi-Department**: Cross-functional project coordination

### 📊 **Comprehensive Evaluation Metrics**
1. **Response Quality** (25%) - Factual accuracy and completeness
2. **Business Value** (25%) - Strategic insight and actionable recommendations
3. **Communication Style** (20%) - Professionalism and tone appropriateness
4. **Tool Usage** (20%) - Effective integration with business tools
5. **Performance** (10%) - Response time and efficiency

### 🛠️ **Business Tool Ecosystem**
- Knowledge Base Search
- Product Catalog Lookup
- Pricing Calculator
- Appointment Scheduler
- Customer History Access
- Document Retrieval
- Order Management
- Support Ticket System

### 🤖 **Multi-Model Support**

<table>
<tr>
<td><strong>🤖 OpenAI</strong></td>
<td><strong>🧠 Anthropic</strong></td>
<td><strong>🌟 Mistral AI</strong></td>
</tr>
<tr>
<td>• GPT-4<br>• GPT-3.5-turbo<br>• GPT-4-turbo</td>
<td>• Claude-3-opus<br>• Claude-3-sonnet<br>• Claude-3-haiku</td>
<td>• Mistral-large<br>• Mistral-medium<br>• Mistral-small</td>
</tr>
</table>

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Olib-AI/bizcon.git
cd bizcon

# Install dependencies
pip install -e .
```

### Basic Usage

1. **Set up your API keys:**
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export MISTRAL_API_KEY="your-mistral-key"
```

2. **Run a quick test:**
```bash
# 🚀 Test without API keys (uses mock models)
python test_framework.py

# 🧪 Run unit and integration tests
python -m pytest tests/

# 🤖 Test with real models (requires API keys)
python test_with_real_models.py
```

3. **Run a benchmark:**
```bash
# 📊 Compare models on specific scenarios
python run.py --scenarios product_inquiry_001 support_001 --verbose

# 🏃 Run full benchmark with custom config
python run.py --config config/models.yaml --output results/

# 💻 Using CLI interface directly  
bizcon run --config config/models.yaml --output results/
```

4. **Explore available options:**
```bash
# 📋 List all available scenarios
python run.py --list-scenarios
# or: bizcon list-scenarios

# 🤖 List supported models  
python run.py --list-models
# or: bizcon list-models
```

### Configuration

Customize your evaluation in `config/models.yaml`:

```yaml
models:
  - provider: openai
    name: gpt-4
    temperature: 0.7
    max_tokens: 2048
  - provider: anthropic
    name: claude-3-sonnet
    temperature: 0.7
    max_tokens: 2048
```

Adjust evaluation settings in `config/evaluation.yaml`:

```yaml
evaluation:
  parallel: true
  num_runs: 3
  evaluator_weights:
    response_quality: 0.25
    business_value: 0.25
    communication_style: 0.20
    tool_usage: 0.20
    performance: 0.10
```

## 📖 Documentation

### Project Structure

```
bizcon/
├── config/                 # Configuration files
│   ├── models.yaml        # Model configurations
│   └── evaluation.yaml    # Evaluation settings
├── core/                  # Core evaluation pipeline
│   ├── pipeline.py        # Main evaluation orchestrator
│   └── runner.py          # Scenario execution engine
├── models/                # LLM provider integrations
│   ├── openai.py         # OpenAI client
│   ├── anthropic.py      # Anthropic client
│   └── mistral.py        # Mistral AI client
├── scenarios/             # Business conversation scenarios
│   ├── product_inquiry.py
│   ├── technical_support.py
│   └── contract_negotiation.py
├── evaluators/            # Evaluation metrics
│   ├── response_quality.py
│   ├── business_value.py
│   └── communication_style.py
├── tools/                 # Business tool implementations
│   ├── knowledge_base.py
│   ├── scheduler.py
│   └── product_catalog.py
├── visualization/         # Report generation
│   ├── charts.py
│   └── report.py
└── data/                  # Sample business data
    ├── knowledge_base/
    ├── products/
    └── pricing/
```

### Creating Custom Scenarios

```python
from scenarios.base import BusinessScenario

class CustomBusinessScenario(BusinessScenario):
    def __init__(self, scenario_id=None):
        super().__init__(
            scenario_id=scenario_id or "custom_001",
            name="Custom Business Scenario",
            description="Your custom scenario description",
            industry="technology",
            complexity="medium",
            tools_required=["knowledge_base", "scheduler"]
        )
    
    def _initialize_conversation(self):
        return [{
            "user_message": "Your initial customer message",
            "expected_tool_calls": [
                {"tool_id": "knowledge_base", "parameters": {"query": "example"}}
            ]
        }]
    
    def _initialize_ground_truth(self):
        return {
            "expected_facts": ["Key fact 1", "Key fact 2"],
            "business_objective": "Help customer achieve X",
            "expected_tone": "professional"
        }
```

### Adding Custom Evaluators

```python
from evaluators.base import BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    def __init__(self, weight=1.0):
        super().__init__(name="Custom Evaluator", weight=weight)
    
    def evaluate(self, response, scenario, turn_index, conversation_history, tool_calls):
        # Your evaluation logic here
        score = self.calculate_score(response)
        return {
            "score": score,
            "explanation": "Detailed explanation of the score",
            "max_possible": 10.0
        }
```

## 📊 Sample Results

<details>
<summary><strong>📈 Click to view sample benchmark results</strong></summary>

### Overall Model Performance
```
┌─────────────────┬─────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Model           │ Overall │ Response    │ Business    │ Communication│ Tool Usage  │ Performance │
│                 │ Score   │ Quality     │ Value       │ Style       │             │             │
├─────────────────┼─────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ gpt-4           │ 8.2/10  │ 8.5/10      │ 8.1/10      │ 9.0/10      │ 7.8/10      │ 8.0/10      │
│ claude-3-sonnet │ 7.9/10  │ 8.2/10      │ 7.8/10      │ 8.8/10      │ 7.5/10      │ 7.2/10      │
│ claude-3-haiku  │ 7.1/10  │ 7.3/10      │ 6.9/10      │ 8.0/10      │ 6.8/10      │ 8.5/10      │
│ gpt-3.5-turbo   │ 6.8/10  │ 6.5/10      │ 6.2/10      │ 7.5/10      │ 6.0/10      │ 7.8/10      │
└─────────────────┴─────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### Success Rates by Category
- **GPT-4**: Response Quality (89%), Tool Usage (78%), Communication Style (90%)
- **Claude-3-Sonnet**: Response Quality (86%), Tool Usage (75%), Communication Style (88%)
- **Claude-3-Haiku**: Response Quality (73%), Tool Usage (68%), Communication Style (80%)

### Report Outputs
- **📊 Interactive HTML Report**: Charts, breakdowns, and detailed analysis
- **📈 CSV Data Export**: Raw scores for custom analysis and visualization
- **📝 Markdown Summary**: Professional reports for sharing and documentation
- **🎯 Success Rate Analysis**: Model performance across business scenarios

</details>

## 🏗️ Advanced Usage

### Parallel Evaluation
```bash
# Run multiple scenarios in parallel
python run.py --scenarios product_inquiry_001 support_001 contract_001 --parallel

# Or using CLI directly
bizcon run --scenarios product_inquiry_001 support_001 --parallel
```

### Custom Model Parameters
```yaml
models:
  - provider: openai
    name: gpt-4
    temperature: 0.3
    max_tokens: 1024
    parameters:
      seed: 42
      top_p: 0.9
```

### Scenario Categories
```bash
# Run all product inquiry scenarios
python run.py --scenarios product_inquiry_*

# Run scenarios by complexity
python run.py --scenarios complex_*
```

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
- 🐛 **Report Bugs**: Open an issue with detailed reproduction steps
- ✨ **Suggest Features**: Propose new scenarios, evaluators, or tools
- 📝 **Improve Documentation**: Help make our docs clearer
- 🔧 **Submit Code**: Fix bugs or add new features
- 🧪 **Add Test Cases**: Improve our test coverage

### Development Setup
```bash
git clone https://github.com/Olib-AI/bizcon.git
cd bizcon
pip install -e .

# Run framework validation (no API keys needed)
python test_framework.py

# Run full test suite  
python -m pytest tests/
```

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🧪 Testing & Validation

### 🎯 Framework Validation Status

<div align="center">

| Component | Status | Coverage |
|-----------|--------|----------|
| **Unit Tests** | ✅ PASSED (12/12) | Evaluators, Scenarios, Tools |
| **Integration Tests** | ✅ PASSED | End-to-end Pipeline |
| **Framework Tests** | ✅ PASSED | Mock Model Validation |
| **Report Generation** | ✅ WORKING | HTML, Markdown, CSV |
| **CLI Functionality** | ✅ OPERATIONAL | All Commands Available |
| **Data Integrity** | ✅ VERIFIED | JSON Files Valid |

</div>

### Running Tests

<details>
<summary><strong>🧪 Click to view test commands</strong></summary>

```bash
# 🚀 Quick framework validation (no API keys required)
python test_framework.py

# 📊 Full test suite with detailed output
python -m pytest tests/ -v

# 🔍 Test specific components
python -m pytest tests/unit/test_evaluators.py::TestResponseQualityEvaluator
python -m pytest tests/integration/test_pipeline.py

# 🎯 Test with coverage report
python -m pytest tests/ --cov=./ --cov-report=html
```

**No API keys needed** for framework validation - uses MockModelClient for comprehensive testing.

</details>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Community

- **Website**: [www.olib.ai](https://www.olib.ai)
- **GitHub**: [github.com/Olib-AI](https://github.com/Olib-AI)
- **Issues**: [Report bugs or request features](https://github.com/Olib-AI/bizcon/issues)
- **Discussions**: [Join the conversation](https://github.com/Olib-AI/bizcon/discussions)

## 👥 Authors

**[Akram Hasan Sharkar](https://github.com/ibnbd)** - *Author & Lead Developer*  
**[Maya Msahal](https://github.com/Mayamsah)** - *Co-Author & Research Contributor*

*Developed at [Olib AI](https://www.olib.ai)*

## 📖 Research Paper

A detailed research paper describing the methodology, evaluation framework, and empirical results of bizCon will be published on arXiv.org. The paper link will be available here upon publication.

*Citation format will be provided once the paper is published.*

## 🙏 Acknowledgments

- Built with ❤️ by [Akram Hasan Sharkar](https://github.com/ibnbd) and [Maya Msahal](https://github.com/Mayamsah) at [Olib AI](https://www.olib.ai)
- Inspired by the need for better business-focused LLM evaluation
- Thanks to all contributors who help make this project better

## 📈 Roadmap

<details>
<summary><strong>🚀 View upcoming features and release history</strong></summary>

### 🔮 Upcoming Features

| Feature | Priority | Status | ETA |
|---------|----------|--------|-----|
| 🌐 **More LLM Providers** (Cohere, Together AI) | High | Planning | Q2 2024 |
| 📊 **Advanced Visualization Dashboards** | High | In Progress | Q2 2024 |
| 🏭 **Industry-Specific Scenario Packs** | Medium | Planning | Q3 2024 |
| ⚡ **Real-time Evaluation APIs** | Medium | Researching | Q3 2024 |
| 🔗 **Custom Webhook Integrations** | Low | Backlog | Q4 2024 |
| 🌍 **Multi-language Support** | Low | Backlog | Q4 2024 |

### 📋 Version History

- **v0.3.0** *(Current)*: Multi-provider support, tool integration, success rate differentiation
- **v0.2.0**: Added visualization and reporting capabilities
- **v0.1.0**: Initial release with core evaluation framework

</details>

---

<div align="center">

**Made with ❤️ by [Akram Hasan Sharkar](https://github.com/ibnbd) & [Maya Msahal](https://github.com/Mayamsah) at [Olib AI](https://www.olib.ai)**

[⭐ Star us on GitHub](https://github.com/Olib-AI/bizcon) • [📖 Read the Docs](https://github.com/Olib-AI/bizcon/wiki) • [🐛 Report Issues](https://github.com/Olib-AI/bizcon/issues)

</div>