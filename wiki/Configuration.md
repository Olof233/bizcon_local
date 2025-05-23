# Configuration Guide

bizCon uses YAML configuration files to customize evaluation settings, model parameters, and framework behavior. This guide covers all configuration options and best practices.

## 📁 Configuration Files

### File Locations

```
config/
├── models.yaml        # Model definitions and parameters
├── evaluation.yaml    # Evaluation settings and weights
└── custom/           # Your custom configurations
```

## 🤖 Model Configuration (`models.yaml`)

### Basic Structure

```yaml
models:
  - provider: openai
    name: gpt-4
    temperature: 0.7
    max_tokens: 2048
    top_p: 1.0
    frequency_penalty: 0
    presence_penalty: 0
    seed: 42  # For reproducibility
    
  - provider: anthropic
    name: claude-3-opus
    temperature: 0.7
    max_tokens: 2048
    
  - provider: mistral
    name: mistral-large
    temperature: 0.7
    max_tokens: 2048
```

### Provider-Specific Options

#### OpenAI Models
```yaml
models:
  - provider: openai
    name: gpt-4
    model_id: gpt-4-0125-preview  # Specific model version
    temperature: 0.7
    max_tokens: 2048
    top_p: 1.0
    frequency_penalty: 0
    presence_penalty: 0
    seed: 42
    response_format: 
      type: json_object  # Force JSON responses
    tools: auto  # Tool usage mode: auto, none, required
```

#### Anthropic Models
```yaml
models:
  - provider: anthropic
    name: claude-3-opus
    model_id: claude-3-opus-20240229
    temperature: 0.7
    max_tokens: 2048
    top_p: 1.0
    top_k: 40
    system_prompt: "You are a helpful business assistant."
```

#### Mistral Models
```yaml
models:
  - provider: mistral
    name: mistral-large
    model_id: mistral-large-latest
    temperature: 0.7
    max_tokens: 2048
    top_p: 1.0
    safe_mode: false  # Content filtering
```

### Model Aliases

Define friendly names for model versions:

```yaml
model_aliases:
  gpt4: gpt-4-0125-preview
  claude: claude-3-opus-20240229
  mistral: mistral-large-latest

models:
  - provider: openai
    name: gpt4  # Uses alias
    temperature: 0.7
```

## 📊 Evaluation Configuration (`evaluation.yaml`)

### Core Settings

```yaml
evaluation:
  # Execution settings
  parallel: true              # Enable parallel model evaluation
  max_workers: 4             # Maximum parallel workers
  num_runs: 3                # Runs per model-scenario pair
  timeout: 300               # Timeout per evaluation (seconds)
  
  # Output settings
  output_dir: results/       # Where to save results
  formats:                   # Output formats to generate
    - html
    - csv
    - markdown
    - json
  
  # Randomization
  seed: 42                   # Global random seed
  shuffle_scenarios: false   # Randomize scenario order
```

### Evaluator Weights

Configure the importance of each evaluation dimension:

```yaml
evaluator_weights:
  response_quality: 0.25      # 25% - Accuracy and completeness
  business_value: 0.25        # 25% - Strategic insights
  communication_style: 0.20   # 20% - Professional communication
  tool_usage: 0.20           # 20% - Tool integration effectiveness
  performance: 0.10          # 10% - Speed and efficiency
```

### Tool Configuration

```yaml
tools:
  # Tool behavior settings
  mock_mode: true           # Use mock data (no real APIs)
  error_rate: 0.1          # 10% chance of tool errors
  latency_range: [100, 500] # Simulated latency in ms
  
  # Error simulation
  error_types:
    - timeout              # Connection timeout
    - not_found           # Resource not found
    - permission_denied   # Access denied
    - rate_limit         # API rate limit
  
  # Tool-specific settings
  knowledge_base:
    max_results: 5
    relevance_threshold: 0.7
    
  product_catalog:
    max_products: 10
    include_discontinued: false
    
  pricing_calculator:
    allow_custom_discounts: true
    max_discount_percent: 50
```

### Scenario Settings

```yaml
scenarios:
  # Scenario selection
  include_all: false        # Run all available scenarios
  include_categories:       # Include specific categories
    - sales
    - support
    - technical
    
  exclude_scenarios:        # Skip specific scenarios
    - experimental_001
    
  # Scenario behavior
  max_turns: 10            # Maximum conversation turns
  turn_timeout: 60         # Timeout per turn (seconds)
  
  # Difficulty settings
  complexity_levels:        # Include only certain complexities
    - medium
    - high
    - very_high
```

## 🎯 Advanced Configuration

### Performance Optimization

```yaml
performance:
  # Caching
  enable_cache: true
  cache_dir: .cache/
  cache_ttl: 3600          # Cache TTL in seconds
  
  # Rate limiting
  requests_per_minute:
    openai: 60
    anthropic: 50
    mistral: 100
    
  # Retry settings
  max_retries: 3
  retry_delay: 1.0         # Exponential backoff base
  
  # Batching
  batch_size: 5            # Scenarios per batch
  batch_delay: 0.5         # Delay between batches
```

### Logging Configuration

```yaml
logging:
  level: INFO              # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # Log destinations
  console:
    enabled: true
    level: INFO
    
  file:
    enabled: true
    path: logs/bizcon.log
    level: DEBUG
    max_size: 10485760     # 10MB
    backup_count: 5
    
  # Component-specific logging
  components:
    models: DEBUG
    evaluators: INFO
    tools: WARNING
```

### Visualization Settings

```yaml
visualization:
  # Chart settings
  charts:
    theme: plotly_white    # Chart theme
    height: 600           # Default chart height
    width: 1000           # Default chart width
    show_grid: true
    
  # Dashboard settings
  dashboard:
    port: 8050            # Dashboard server port
    debug: false          # Flask debug mode
    host: "127.0.0.1"    # Dashboard host
    
  # Report settings
  report:
    include_raw_data: false  # Include raw JSON in reports
    embed_charts: true       # Embed charts in HTML
    chart_format: png        # png, svg, webp
```

## 🔧 Environment Variables

Override configuration with environment variables:

```bash
# API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export MISTRAL_API_KEY="..."

# Override config values
export BIZCON_PARALLEL=true
export BIZCON_NUM_RUNS=5
export BIZCON_OUTPUT_DIR="./my_results"

# Model-specific overrides
export BIZCON_GPT4_TEMPERATURE=0.5
export BIZCON_CLAUDE_MAX_TOKENS=4096
```

## 📝 Custom Configuration Files

### Creating Custom Configs

```yaml
# config/custom/production.yaml
extends: evaluation.yaml    # Inherit from base config

evaluation:
  num_runs: 10            # More runs for production
  parallel: true
  max_workers: 8          # More workers
  
evaluator_weights:
  response_quality: 0.35   # Emphasize quality in production
  business_value: 0.35
  communication_style: 0.15
  tool_usage: 0.10
  performance: 0.05       # Less weight on performance
```

### Using Custom Configs

```bash
# CLI usage
bizcon run --config config/custom/production.yaml

# Python usage
from bizcon import EvaluationPipeline

pipeline = EvaluationPipeline("config/custom/production.yaml")
pipeline.run()
```

## 🎨 Configuration Templates

### Quick Test Configuration
```yaml
# config/quick_test.yaml
evaluation:
  num_runs: 1
  parallel: false
  
scenarios:
  include_scenarios:
    - product_inquiry_001
    
models:
  - provider: openai
    name: gpt-3.5-turbo
    temperature: 0.7
```

### Comprehensive Benchmark
```yaml
# config/benchmark.yaml
evaluation:
  num_runs: 5
  parallel: true
  max_workers: 8
  
scenarios:
  include_all: true
  
models:
  - provider: openai
    name: gpt-4
  - provider: anthropic
    name: claude-3-opus
  - provider: mistral
    name: mistral-large
```

### Cost-Optimized Configuration
```yaml
# config/cost_optimized.yaml
models:
  - provider: openai
    name: gpt-3.5-turbo
    max_tokens: 1000      # Limit tokens
    
  - provider: mistral
    name: mistral-small   # Cheaper model
    
evaluation:
  num_runs: 2             # Fewer runs
  
performance:
  cache_ttl: 7200         # Longer cache
```

## 🚀 Best Practices

1. **Version Control**: Keep configurations in git
2. **Environment Separation**: Use different configs for dev/staging/prod
3. **Sensitive Data**: Use environment variables for API keys
4. **Validation**: Test configurations with `--dry-run` flag
5. **Documentation**: Comment complex configuration choices

---

<p align="center">
  <strong>Explore advanced features and visualizations</strong><br>
  <a href="Advanced-Features">View Advanced Features →</a>
</p>