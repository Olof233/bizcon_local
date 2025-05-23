# Frequently Asked Questions (FAQ)

## 🚀 Getting Started

### Q: What is bizCon?

**A:** bizCon is a specialized benchmarking framework designed to evaluate Large Language Models (LLMs) in realistic business conversation scenarios. It tests models on professional communication, business tool integration, and domain-specific knowledge.

### Q: Which LLMs does bizCon support?

**A:** bizCon currently supports:
- **OpenAI**: GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
- **Anthropic**: Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku  
- **Mistral AI**: Mistral-Large, Mistral-Medium, Mistral-Small

Additional providers can be added by implementing the `ModelClient` interface.

### Q: Do I need API keys to use bizCon?

**A:** Not necessarily! You can:
- Test the framework without API keys using `python test_framework.py`
- Use mock models for development and testing
- Only need API keys when evaluating real LLM providers

### Q: How much does it cost to run evaluations?

**A:** Costs depend on:
- Which models you evaluate
- Number of scenarios and runs
- Model token usage

Typical costs:
- Single model, all scenarios, 1 run: ~$5-15
- Full benchmark (3 models, all scenarios, 3 runs): ~$50-150

Use the `--dry-run` flag to estimate costs before running.

## 🔧 Installation Issues

### Q: ImportError when running bizcon

**A:** Make sure you installed in editable mode:
```bash
pip install -e .
```

If issues persist:
```bash
pip uninstall bizcon
pip install -e ".[all]"
```

### Q: Command 'bizcon' not found

**A:** The CLI might not be in your PATH. Try:
1. Use `python -m bizcon` instead
2. Or run directly: `python run.py`
3. Check pip installed it: `pip show bizcon`

### Q: Missing dependencies errors

**A:** Install all dependencies:
```bash
# Basic installation might miss optional deps
pip install -e ".[all]"

# Or install specific groups
pip install -e ".[advanced]"  # For dashboards
pip install -e ".[test]"      # For testing
```

## 🏃‍♂️ Running Evaluations

### Q: How do I run a quick test?

**A:** Several options:
```bash
# Test single model on one scenario
python examples/quick_test.py --provider openai --model gpt-4

# Use the CLI
bizcon run --provider openai --model gpt-4 --scenarios product_inquiry_001

# Test framework (no API keys)
python test_framework.py
```

### Q: Evaluation is taking too long

**A:** Speed up evaluations:
```yaml
# config/evaluation.yaml
evaluation:
  parallel: true       # Enable parallel execution
  max_workers: 8      # Increase workers
  num_runs: 1         # Reduce runs
  timeout: 60         # Lower timeout

scenarios:
  max_turns: 5        # Limit conversation length
```

### Q: How do I run specific scenarios?

**A:** Multiple ways:
```bash
# CLI with scenario IDs
bizcon run --scenarios product_inquiry_001 technical_support_001

# Python script
python run.py --scenarios product_inquiry_001,support_001

# List available scenarios first
python run.py --list-scenarios
```

## 🛠️ Configuration

### Q: How do I customize evaluation weights?

**A:** Edit `config/evaluation.yaml`:
```yaml
evaluator_weights:
  response_quality: 0.30      # Increase quality weight
  business_value: 0.30        # Increase business focus
  communication_style: 0.15   # Reduce style weight
  tool_usage: 0.15           
  performance: 0.10
```

### Q: Can I use different model parameters?

**A:** Yes, in `config/models.yaml`:
```yaml
models:
  - provider: openai
    name: gpt-4
    temperature: 0.5        # Lower = more focused
    max_tokens: 1000       # Limit response length
    top_p: 0.9            
    seed: 42              # For reproducibility
```

### Q: How do I add custom scenarios?

**A:** Create a new file in `scenarios/`:
```python
from scenarios.base import BusinessScenario, register_scenario

@register_scenario
class CustomScenario(BusinessScenario):
    def __init__(self):
        super().__init__()
        self.id = "custom_001"
        self.name = "Custom Scenario"
        # Define conversation flow
```

## 📊 Results & Reports

### Q: Where are evaluation results saved?

**A:** By default in `results/` directory:
```
results/
└── run_20250523_150000/          # Timestamp-based folder
    ├── raw_results.json          # Complete evaluation data
    ├── report.html               # Interactive report
    ├── report.md                 # Markdown summary
    ├── overall_scores.csv        # Model scores
    ├── category_scores.csv       # Dimension breakdown
    └── scenario_scores.csv       # Per-scenario results
```

### Q: How do I view the interactive dashboard?

**A:** After evaluation:
```bash
# Launch dashboard
bizcon dashboard --results results/run_20250523_150000/

# Or specify port
bizcon dashboard --results results/latest/ --port 8080

# Then open browser to http://localhost:8080
```

### Q: Can I export results to Excel?

**A:** Yes, use the DataExporter:
```python
from bizcon.visualization import DataExporter

exporter = DataExporter("results/run_20250523_150000/")
exporter.to_excel("results.xlsx", include_charts=True)
```

## 🐛 Troubleshooting

### Q: API rate limit errors

**A:** Configure rate limiting:
```yaml
# config/evaluation.yaml
performance:
  requests_per_minute:
    openai: 30          # Reduce request rate
    anthropic: 20
  
  retry_settings:
    max_retries: 5      # More retries
    retry_delay: 2.0    # Longer delays
```

### Q: Tool execution errors

**A:** Check tool configuration:
```yaml
tools:
  error_rate: 0.0       # Disable simulated errors
  mock_mode: true       # Ensure using mock data
  
  # Or debug specific tool
  knowledge_base:
    debug: true         # Enable debug logging
```

### Q: Memory issues with large evaluations

**A:** Reduce memory usage:
```yaml
evaluation:
  parallel: false       # Disable parallel execution
  batch_size: 1        # Process one at a time
  
performance:
  enable_cache: false   # Disable caching
```

## 🔒 Security & Privacy

### Q: Are my API keys secure?

**A:** bizCon:
- Never logs API keys
- Loads keys from environment variables or `.env`
- Doesn't store keys in configuration files
- Doesn't transmit keys except to provider APIs

### Q: Is evaluation data sent anywhere?

**A:** No, bizCon:
- Runs entirely locally
- Only contacts LLM provider APIs
- Doesn't collect telemetry
- All results stay on your machine

### Q: Can I use bizCon with private models?

**A:** Yes, implement a custom ModelClient:
```python
from bizcon.models import ModelClient

class PrivateModelClient(ModelClient):
    def __init__(self, endpoint_url, auth_token):
        self.endpoint = endpoint_url
        self.auth = auth_token
    
    def generate_response(self, messages, tools=None, **kwargs):
        # Your implementation
        pass
```

## 🎯 Best Practices

### Q: How many evaluation runs should I do?

**A:** Depends on your needs:
- **Quick test**: 1 run
- **Development**: 3 runs (balance of speed/reliability)
- **Production benchmark**: 5-10 runs (statistical significance)
- **Research**: 10+ runs with statistical analysis

### Q: Which scenarios are most important?

**A:** Depends on use case:
- **Customer Service**: service_complaints, appointment_scheduling
- **Sales**: product_inquiry, contract_negotiation
- **Technical**: technical_support, implementation_planning
- **Compliance**: compliance_inquiry
- **General**: Run all for comprehensive evaluation

### Q: How do I interpret the scores?

**A:** Score ranges:
- **90-100**: Excellent, production-ready
- **80-89**: Good, minor improvements needed
- **70-79**: Fair, noticeable gaps
- **60-69**: Poor, significant issues
- **<60**: Failing, not suitable for business use

## 🤝 Contributing

### Q: How can I contribute to bizCon?

**A:** We welcome contributions!
1. Check [GitHub Issues](https://github.com/yourusername/bizcon/issues)
2. Read [CONTRIBUTING.md](https://github.com/yourusername/bizcon/blob/main/CONTRIBUTING.md)
3. Submit pull requests for:
   - New scenarios
   - Additional model providers
   - Bug fixes
   - Documentation improvements

### Q: I found a bug, what should I do?

**A:** Please:
1. Check existing [issues](https://github.com/yourusername/bizcon/issues)
2. Create a new issue with:
   - bizCon version
   - Python version
   - Full error message
   - Steps to reproduce
3. Include minimal reproducible example if possible

### Q: Can I use bizCon commercially?

**A:** Yes! bizCon is MIT licensed. You can:
- Use in commercial projects
- Modify and distribute
- Include in proprietary software
- Just maintain the license attribution

## 📚 Additional Resources

### Q: Where can I learn more?

**A:** 
- [GitHub Repository](https://github.com/yourusername/bizcon)
- [API Documentation](API-Reference)
- [Example Scripts](https://github.com/yourusername/bizcon/tree/main/examples)
- [Test Cases](https://github.com/yourusername/bizcon/tree/main/tests)

### Q: Is there a Discord/Slack community?

**A:** Join our community:
- [GitHub Discussions](https://github.com/yourusername/bizcon/discussions)
- Report issues on [GitHub](https://github.com/yourusername/bizcon/issues)

---

<p align="center">
  <strong>Still have questions?</strong><br>
  Open an <a href="https://github.com/yourusername/bizcon/issues/new">issue</a> on GitHub
</p>