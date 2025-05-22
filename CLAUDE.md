# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BizCon is a framework for evaluating and benchmarking Large Language Models (LLMs) on business conversation capabilities. It allows comparing different LLM providers (OpenAI, Anthropic, Mistral) across various business scenarios with standardized metrics.

## Project Structure

- **Models**: Integrations with different LLM providers (OpenAI, Anthropic, Mistral)
- **Scenarios**: Business conversation scenarios (product inquiries, technical support, etc.)
- **Evaluators**: Metrics for quality, business value, communication style
- **Tools**: Simulated business tools (knowledge base, scheduler, product catalog)
- **Core**: Pipeline for orchestrating evaluations
- **Visualization**: Reports and dashboards for comparison results

## Development Setup

```bash
# Install in development mode
pip install -e .
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_evaluators.py

# Run with verbose output
pytest -v
```

## CLI Usage

The project provides a command-line interface:

```bash
# Run bizcon CLI
bizcon [arguments]
```

## Example Usage

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

## Note

This project appears to be in early development with many files created but currently empty.