# bizCon: Business Conversation Evaluation Framework for LLMs

bizCon is a comprehensive evaluation framework for benchmarking Large Language Models on business conversation capabilities. It assesses how well different models handle realistic business interactions involving tools, professional communication, and accurate information delivery.

## Features

- Compare multiple LLM providers (OpenAI, Anthropic, etc.)
- Test with realistic business scenarios across industries
- Simulate business tool interactions
- Evaluate response quality, communication style, and business value
- Generate comparative visualizations and reports

## Installation

```bash
pip install -e .
```

## Usage

```python
from bizcon.core.pipeline import EvaluationPipeline
from bizcon.models import OpenAIClient, AnthropicClient
from bizcon.scenarios import load_scenario

# Load models and scenarios
models = [OpenAIClient("gpt-4"), AnthropicClient("claude-3-sonnet")]
scenario = load_scenario("product_inquiry_001")

# Run evaluation
pipeline = EvaluationPipeline(models, [scenario])
results = pipeline.run()

# Generate report
pipeline.generate_report("output/comparison_report")
```

## Documentation

For detailed documentation, see the [docs](docs/) directory.
