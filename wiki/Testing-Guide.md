# Testing Guide

bizCon includes comprehensive testing capabilities to ensure framework reliability and enable development without requiring API keys. This guide covers testing strategies, mock implementations, and validation approaches.

## 🧪 Testing Overview

### Testing Levels

1. **Framework Validation** - Test without API keys using mock models
2. **Unit Testing** - Component-level tests for individual modules
3. **Integration Testing** - End-to-end pipeline validation
4. **Real Model Testing** - Optional tests with actual LLM providers

### Quick Testing Commands

```bash
# Framework validation (no API keys needed)
python test_framework.py

# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only

# Run with coverage
pytest --cov=bizcon tests/

# Test with real models (requires API keys)
python test_with_real_models.py
```

## 🎭 Mock Model Testing

### MockModelClient

The framework includes a sophisticated mock model for testing:

```python
from models.base import MockModelClient

# Create mock with specific behavior
mock = MockModelClient(
    behavior="accurate",  # accurate, inaccurate, incomplete
    latency_range=(0.1, 0.5),
    token_range=(100, 500)
)

# Use like any other model
response = mock.generate_response(
    messages=[{"role": "user", "content": "Hello"}],
    tools=available_tools
)
```

### Mock Behaviors

#### Accurate Mock
```python
# Simulates high-performing model
mock = MockModelClient(behavior="accurate")
# - Correct tool usage
# - Complete responses
# - Professional tone
# - High evaluation scores
```

#### Inaccurate Mock
```python
# Simulates poor-performing model
mock = MockModelClient(behavior="inaccurate")
# - Wrong tool calls
# - Incomplete information
# - Unprofessional tone
# - Low evaluation scores
```

#### Incomplete Mock
```python
# Simulates partially capable model
mock = MockModelClient(behavior="incomplete")
# - Some correct tool usage
# - Partial responses
# - Mixed quality
# - Medium evaluation scores
```

## 🔬 Unit Testing

### Testing Evaluators

```python
# tests/unit/test_evaluators.py
import pytest
from evaluators import ResponseQualityEvaluator

class TestResponseQualityEvaluator:
    def test_perfect_response(self):
        evaluator = ResponseQualityEvaluator()
        
        response = "Accurate, complete, and relevant response"
        scenario = MockScenario(
            ground_truth=["fact1", "fact2"],
            required_points=["point1", "point2"]
        )
        
        score = evaluator.evaluate(response, scenario)
        assert score >= 0.9
        
    def test_poor_response(self):
        evaluator = ResponseQualityEvaluator()
        
        response = "Wrong and incomplete"
        scenario = MockScenario(
            ground_truth=["fact1", "fact2"],
            required_points=["point1", "point2"]
        )
        
        score = evaluator.evaluate(response, scenario)
        assert score < 0.5
```

### Testing Tools

```python
# tests/unit/test_tools.py
import pytest
from tools import ProductCatalog

class TestProductCatalog:
    def test_search_products(self):
        catalog = ProductCatalog()
        
        results = catalog.execute(
            query="CRM",
            filters={"category": "Sales"}
        )
        
        assert len(results["products"]) > 0
        assert all(p["category"] == "Sales" for p in results["products"])
        
    def test_empty_search(self):
        catalog = ProductCatalog()
        
        results = catalog.execute(
            query="NonexistentProduct123"
        )
        
        assert len(results["products"]) == 0
```

### Testing Scenarios

```python
# tests/unit/test_scenarios.py
import pytest
from scenarios import ProductInquiryScenario

class TestProductInquiryScenario:
    def test_scenario_initialization(self):
        scenario = ProductInquiryScenario()
        
        assert scenario.id == "product_inquiry_001"
        assert len(scenario.conversation_flow) > 0
        assert len(scenario.available_tools) > 0
        
    def test_conversation_flow(self):
        scenario = ProductInquiryScenario()
        
        # Test first turn
        first_turn = scenario.get_turn(0)
        assert first_turn["role"] == "user"
        assert "product" in first_turn["content"].lower()
```

## 🔄 Integration Testing

### End-to-End Pipeline Tests

```python
# tests/integration/test_pipeline.py
import pytest
from core import EvaluationPipeline

class TestEvaluationPipeline:
    def test_full_evaluation_flow(self, tmp_path):
        # Use temporary directory for outputs
        config = create_test_config()
        
        pipeline = EvaluationPipeline(config)
        results = pipeline.run(
            scenarios=["product_inquiry_001"],
            output_dir=str(tmp_path)
        )
        
        # Verify results structure
        assert "overall_scores" in results
        assert "category_scores" in results
        assert "scenario_scores" in results
        
        # Verify files created
        assert (tmp_path / "report.html").exists()
        assert (tmp_path / "overall_scores.csv").exists()
```

### Mock Integration Tests

```python
# tests/integration/test_mock_integration.py
class TestMockIntegration:
    def test_mock_models_differentiation(self):
        """Verify different mock behaviors produce different scores"""
        
        accurate_mock = MockModelClient(behavior="accurate")
        poor_mock = MockModelClient(behavior="inaccurate")
        
        # Run same scenario with both
        scenario = ProductInquiryScenario()
        
        accurate_result = run_scenario(accurate_mock, scenario)
        poor_result = run_scenario(poor_mock, scenario)
        
        # Accurate should score higher
        assert accurate_result["score"] > poor_result["score"]
        assert accurate_result["score"] > 80
        assert poor_result["score"] < 50
```

## 🎯 Test Data Management

### Fixture Organization

```python
# tests/fixtures/scenarios.py
import pytest

@pytest.fixture
def sample_product_inquiry():
    return {
        "messages": [
            {"role": "user", "content": "I need a CRM for 50 users"},
            {"role": "assistant", "content": "I'll help you find the right CRM..."}
        ],
        "expected_tools": ["product_catalog", "pricing_calculator"],
        "ground_truth": {
            "products_mentioned": ["SalesPro CRM", "Enterprise CRM"],
            "price_range": "10000-15000"
        }
    }

@pytest.fixture
def sample_technical_support():
    return {
        "messages": [
            {"role": "user", "content": "API returning 401 errors"},
            {"role": "assistant", "content": "Let me help troubleshoot..."}
        ],
        "expected_tools": ["knowledge_base", "customer_history"],
        "ground_truth": {
            "diagnosis": "authentication_issue",
            "solution": "regenerate_api_key"
        }
    }
```

### Mock Data Sets

```python
# tests/fixtures/mock_data.py
MOCK_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "SalesPro CRM",
        "category": "Sales",
        "price": 3500,
        "features": ["Pipeline Management", "Reporting"]
    },
    # ... more products
]

MOCK_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "title": "API Authentication Guide",
        "content": "To authenticate with our API...",
        "category": "technical"
    },
    # ... more articles
]
```

## 🔍 Testing Strategies

### Scenario Coverage Testing

```python
def test_all_scenarios_covered():
    """Ensure all scenarios are tested"""
    
    from scenarios import SCENARIO_REGISTRY
    
    tested_scenarios = set()
    
    for test_file in Path("tests/").rglob("test_*.py"):
        content = test_file.read_text()
        for scenario_id in SCENARIO_REGISTRY:
            if scenario_id in content:
                tested_scenarios.add(scenario_id)
    
    untested = set(SCENARIO_REGISTRY.keys()) - tested_scenarios
    assert not untested, f"Untested scenarios: {untested}"
```

### Performance Testing

```python
def test_evaluation_performance():
    """Test evaluation speed and resource usage"""
    
    import time
    import psutil
    
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    # Run evaluation
    pipeline = EvaluationPipeline("config/test.yaml")
    pipeline.run(scenarios=["product_inquiry_001"])
    
    duration = time.time() - start_time
    memory_used = psutil.Process().memory_info().rss - start_memory
    
    # Performance assertions
    assert duration < 60  # Should complete in under 60 seconds
    assert memory_used < 500 * 1024 * 1024  # Less than 500MB
```

### Error Handling Testing

```python
def test_tool_error_handling():
    """Test graceful handling of tool failures"""
    
    # Configure tool to fail
    tool = ProductCatalog(error_rate=1.0)  # Always fail
    
    try:
        result = tool.execute(query="test")
    except ToolError as e:
        assert e.error_type in ["timeout", "not_found", "permission_denied"]
        assert e.retry_after is not None
```

## 🏃‍♂️ Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
        
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
        
    - name: Run framework validation
      run: python test_framework.py
      
    - name: Run unit tests
      run: pytest tests/unit/ -v
      
    - name: Run integration tests
      run: pytest tests/integration/ -v
      
    - name: Generate coverage report
      run: |
        pytest --cov=bizcon --cov-report=xml tests/
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: test-framework
        name: Framework Validation
        entry: python test_framework.py
        language: system
        pass_filenames: false
        
      - id: unit-tests
        name: Unit Tests
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
```

## 🎨 Test Visualization

### Test Report Generation

```python
# Generate HTML test report
pytest --html=test_report.html --self-contained-html

# Generate coverage visualization
pytest --cov=bizcon --cov-report=html tests/
# Open htmlcov/index.html
```

### Performance Profiling

```python
# Profile test execution
pytest --profile tests/

# Generate flame graph
py-spy record -o profile.svg -- pytest tests/
```

## 🚀 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Never call real APIs in tests
3. **Use Fixtures**: Share test data efficiently
4. **Test Edge Cases**: Include boundary conditions
5. **Performance Assertions**: Include timing constraints
6. **Documentation**: Document test purposes clearly

---

<p align="center">
  <strong>Explore the code API documentation</strong><br>
  <a href="API-Reference">View API Reference →</a>
</p>