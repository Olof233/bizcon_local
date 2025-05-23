# Getting Started with bizCon

This guide will walk you through installing bizCon and running your first business conversation evaluation.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **API Keys** for the LLM providers you want to test (OpenAI, Anthropic, Mistral)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bizcon.git
cd bizcon
```

### 2. Install bizCon

You have three installation options:

#### Basic Installation
```bash
pip install -e .
```

#### With Advanced Features (Recommended)
Includes Plotly for interactive dashboards:
```bash
pip install -e ".[advanced]"
```

#### All Features
Includes all optional dependencies:
```bash
pip install -e ".[all]"
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Mistral
MISTRAL_API_KEY=your_mistral_api_key_here
```

Alternatively, export them as environment variables:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
export MISTRAL_API_KEY="your_mistral_api_key_here"
```

## 🏃‍♂️ Quick Start

### 1. Test Framework Installation

First, verify the framework is working correctly (no API keys needed):

```bash
python test_framework.py
```

This runs a complete evaluation using mock models to ensure everything is installed properly.

### 2. Run Your First Evaluation

#### Using the CLI

```bash
# Evaluate a single model on one scenario
bizcon run --provider openai --model gpt-4 --scenarios product_inquiry_001

# Evaluate multiple models using configuration file
bizcon run --config config/models.yaml --scenarios product_inquiry_001
```

#### Using Python Script

```bash
# Run with default configuration
python run.py --config config/models.yaml

# Run specific scenarios
python run.py --scenarios product_inquiry_001 technical_support_001 --runs 3

# Run with parallel execution
python run.py --config config/models.yaml --parallel --verbose
```

### 3. View Results

After evaluation completes, you'll find results in the `results/` directory:

```
results/
├── run_20250523_150000/
│   ├── raw_results.json          # Detailed evaluation data
│   ├── report.html               # Interactive HTML report
│   ├── report.md                 # Markdown summary
│   ├── overall_scores.csv        # Overall model scores
│   ├── category_scores.csv       # Scores by evaluation category
│   └── scenario_scores.csv       # Scores by business scenario
```

Open `report.html` in your browser to see the interactive visualization.

## 📊 Understanding the Output

### HTML Report
The HTML report includes:
- **Overall Performance Chart** - Bar chart comparing total scores
- **Category Breakdown** - Performance across 5 evaluation dimensions
- **Scenario Performance** - Success rates for each business scenario
- **Detailed Metrics** - Token usage, costs, and response times

### CSV Files
- **overall_scores.csv** - Summary of each model's total score
- **category_scores.csv** - Breakdown by evaluation category
- **scenario_scores.csv** - Performance on individual scenarios

### Markdown Report
A text-based summary suitable for documentation or sharing in text format.

## 🎯 Example Commands

### List Available Options

```bash
# List all available scenarios
python run.py --list-scenarios

# List configured models
python run.py --list-models
```

### Run Specific Tests

```bash
# Test a single model quickly
python examples/quick_test.py --provider openai --model gpt-4

# Compare two models
python examples/basic_comparison.py

# Run industry benchmark
python examples/industry_benchmark.py
```

### Advanced Usage

```bash
# Run with custom output directory
python run.py --config config/models.yaml --output my_results/

# Run subset of scenarios with multiple iterations
python run.py --scenarios product_inquiry_001 support_001 --runs 5

# Generate only CSV output
python run.py --config config/models.yaml --format csv
```

## 🔧 Configuration Files

### Model Configuration (`config/models.yaml`)

```yaml
models:
  - provider: openai
    name: gpt-4
    temperature: 0.7
    max_tokens: 2048
    
  - provider: anthropic
    name: claude-3-opus
    temperature: 0.7
    max_tokens: 2048
```

### Evaluation Configuration (`config/evaluation.yaml`)

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

## 🎓 Next Steps

1. **Explore Scenarios** - Learn about the [8 business scenarios](Business-Scenarios)
2. **Understand Tools** - See how [business tools](Business-Tools) work
3. **Customize Evaluation** - Configure [evaluation settings](Configuration)
4. **View Dashboards** - Try the [advanced visualization features](Advanced-Features)

## 🆘 Troubleshooting

### Common Issues

**Import Error**: Make sure you installed with `pip install -e .`

**API Key Error**: Verify your API keys are set correctly:
```python
import os
print(os.getenv("OPENAI_API_KEY"))  # Should show your key (partially)
```

**No Results Generated**: Check the console output for errors. Run with `--verbose` flag:
```bash
python run.py --config config/models.yaml --verbose
```

### Getting Help

- Check the [FAQ](FAQ) for common questions
- Review [error messages](FAQ#error-messages) 
- Open an [issue](https://github.com/yourusername/bizcon/issues) for bugs

---

<p align="center">
  <strong>Ready to dive deeper?</strong><br>
  <a href="Architecture">Explore the Architecture →</a>
</p>