# API Reference

Complete API documentation for the bizCon framework, covering all public classes, methods, and functions.

## 📦 Core Package (`bizcon`)

### Main Entry Points

```python
from bizcon import run_evaluation, EvaluationPipeline, __version__

# Run evaluation with configuration
results = run_evaluation(
    config_path="config/models.yaml",
    scenarios=["product_inquiry_001"],
    output_dir="results/",
    parallel=True
)

# Create pipeline instance
pipeline = EvaluationPipeline("config/models.yaml")
pipeline.run()
```

## 🔧 Core Module (`bizcon.core`)

### EvaluationPipeline

Main orchestrator for the evaluation process.

```python
class EvaluationPipeline:
    """Manages the complete evaluation workflow"""
    
    def __init__(self, config_path: str):
        """
        Initialize pipeline with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        
    def run(self, 
            scenarios: List[str] = None,
            output_dir: str = "results/",
            parallel: bool = None) -> Dict[str, Any]:
        """
        Execute evaluation pipeline
        
        Args:
            scenarios: List of scenario IDs to run (None = all)
            output_dir: Directory for output files
            parallel: Override parallel execution setting
            
        Returns:
            Dictionary containing evaluation results
        """
        
    def generate_report(self, 
                       results: Dict[str, Any],
                       output_dir: str) -> None:
        """Generate reports from evaluation results"""
```

### ScenarioRunner

Executes individual scenarios with models.

```python
class ScenarioRunner:
    """Runs scenarios with specific models"""
    
    def run_scenario(self,
                    model: ModelClient,
                    scenario: BusinessScenario,
                    evaluators: List[BaseEvaluator]) -> Dict[str, Any]:
        """
        Execute a single scenario
        
        Args:
            model: Model client instance
            scenario: Business scenario to run
            evaluators: List of evaluators to apply
            
        Returns:
            Evaluation results dictionary
        """
        
    def _execute_conversation(self,
                            model: ModelClient,
                            scenario: BusinessScenario) -> List[Dict]:
        """Execute multi-turn conversation"""
```

## 🤖 Models Module (`bizcon.models`)

### Base Classes

```python
class ModelClient(ABC):
    """Abstract base class for all model clients"""
    
    @abstractmethod
    def generate_response(self,
                         messages: List[Dict[str, str]],
                         tools: List[Dict] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate model response
        
        Args:
            messages: Conversation history
            tools: Available tools in OpenAI format
            **kwargs: Model-specific parameters
            
        Returns:
            Response dictionary with content and metadata
        """
        
    @abstractmethod  
    def get_token_count(self, text: str) -> int:
        """Count tokens in text"""
        
    def calculate_cost(self, 
                      input_tokens: int,
                      output_tokens: int) -> float:
        """Calculate API cost"""
```

### Provider Implementations

#### OpenAI Client

```python
class OpenAIClient(ModelClient):
    """OpenAI API client implementation"""
    
    def __init__(self,
                model_name: str = "gpt-4",
                api_key: str = None,
                **model_params):
        """
        Initialize OpenAI client
        
        Args:
            model_name: Model identifier
            api_key: API key (uses env var if None)
            **model_params: Temperature, max_tokens, etc.
        """
```

#### Anthropic Client

```python
class AnthropicClient(ModelClient):
    """Anthropic Claude API client"""
    
    def __init__(self,
                model_name: str = "claude-3-opus",
                api_key: str = None,
                **model_params):
        """Initialize Anthropic client"""
```

#### Mock Client

```python
class MockModelClient(ModelClient):
    """Mock model for testing"""
    
    def __init__(self,
                behavior: str = "accurate",
                latency_range: Tuple[float, float] = (0.1, 0.5)):
        """
        Initialize mock model
        
        Args:
            behavior: "accurate", "inaccurate", or "incomplete"
            latency_range: Simulated response time range
        """
```

## 🎯 Scenarios Module (`bizcon.scenarios`)

### Base Scenario Class

```python
class BusinessScenario(ABC):
    """Abstract base class for business scenarios"""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.category: str = ""
        self.complexity: str = ""  # low, medium, high, very_high
        self.conversation_flow: List[Dict] = []
        self.available_tools: List[str] = []
        self.evaluation_criteria: Dict = {}
        
    def get_turn(self, turn_index: int) -> Dict[str, str]:
        """Get conversation turn by index"""
        
    def get_expected_tools(self, turn_index: int) -> List[str]:
        """Get expected tool calls for turn"""
        
    @abstractmethod
    def validate_response(self, 
                         response: str,
                         turn_index: int) -> Dict[str, Any]:
        """Validate response against ground truth"""
```

### Scenario Registration

```python
# Decorator for auto-registration
@register_scenario
class CustomScenario(BusinessScenario):
    """Your custom scenario implementation"""
    
# Access registered scenarios
from bizcon.scenarios import SCENARIO_REGISTRY

available_scenarios = SCENARIO_REGISTRY.keys()
scenario_instance = SCENARIO_REGISTRY["scenario_id"]()
```

## 🛠️ Tools Module (`bizcon.tools`)

### Base Tool Class

```python
class BusinessTool(ABC):
    """Abstract base class for business tools"""
    
    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """
        Return tool definition in OpenAI function format
        
        Returns:
            Dictionary with name, description, parameters
        """
        
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute tool with given parameters
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution results
        """
        
    def validate_parameters(self, **kwargs) -> None:
        """Validate input parameters"""
```

### Tool Registration

```python
# Register custom tools
@register_tool
class CustomTool(BusinessTool):
    """Your custom tool implementation"""
    
# Access tools
from bizcon.tools import TOOL_REGISTRY

available_tools = TOOL_REGISTRY.keys()
tool_instance = TOOL_REGISTRY["tool_name"]()
```

## 📊 Evaluators Module (`bizcon.evaluators`)

### Base Evaluator Class

```python
class BaseEvaluator(ABC):
    """Abstract base class for evaluators"""
    
    def __init__(self):
        self.name: str = ""
        self.weight: float = 0.2
        
    @abstractmethod
    def evaluate(self,
                response: str,
                scenario: BusinessScenario,
                metadata: Dict = None) -> float:
        """
        Evaluate response quality
        
        Args:
            response: Model response text
            scenario: Current scenario context
            metadata: Additional evaluation data
            
        Returns:
            Score between 0 and 1
        """
        
    def get_feedback(self, score: float) -> str:
        """Generate human-readable feedback"""
```

### Evaluator Implementations

```python
# Available evaluators
from bizcon.evaluators import (
    ResponseQualityEvaluator,
    BusinessValueEvaluator,
    CommunicationStyleEvaluator,
    ToolUsageEvaluator,
    PerformanceEvaluator
)

# Create evaluator set
evaluators = [
    ResponseQualityEvaluator(),
    BusinessValueEvaluator(),
    CommunicationStyleEvaluator(),
    ToolUsageEvaluator(),
    PerformanceEvaluator()
]
```

## 🎨 Visualization Module (`bizcon.visualization`)

### Report Generator

```python
class ReportGenerator:
    """Generate evaluation reports"""
    
    def __init__(self, results_dir: str):
        """Initialize with results directory"""
        
    def generate_html(self,
                     output_path: str,
                     include_charts: bool = True) -> None:
        """Generate HTML report with embedded charts"""
        
    def generate_markdown(self,
                         output_path: str,
                         include_raw_data: bool = False) -> None:
        """Generate markdown report"""
        
    def generate_csv(self, output_dir: str) -> None:
        """Export results as CSV files"""
```

### Dashboard

```python
def launch_dashboard(results_dir: str,
                    port: int = 8050,
                    debug: bool = False) -> None:
    """
    Launch interactive dashboard
    
    Args:
        results_dir: Directory containing evaluation results
        port: Server port number
        debug: Enable Flask debug mode
    """
```

### Chart Builders

```python
class ChartBuilder:
    """Create custom visualizations"""
    
    def __init__(self, results_data: Dict[str, Any]):
        """Initialize with evaluation results"""
        
    def create_overall_scores_chart(self) -> go.Figure:
        """Create bar chart of overall scores"""
        
    def create_dimension_radar(self, 
                              model_name: str) -> go.Figure:
        """Create radar chart for model dimensions"""
        
    def create_scenario_heatmap(self) -> go.Figure:
        """Create heatmap of model × scenario scores"""
```

## 🧰 Utility Functions

### Configuration Loading

```python
from bizcon.core.utils import load_config, merge_configs

# Load YAML configuration
config = load_config("config/models.yaml")

# Merge multiple configs
merged = merge_configs(base_config, override_config)
```

### Result Processing

```python
from bizcon.core.utils import (
    calculate_statistics,
    aggregate_scores,
    format_results
)

# Calculate statistical summary
stats = calculate_statistics(scores_list)

# Aggregate scores by dimension
aggregated = aggregate_scores(results, by="evaluator")

# Format for display
formatted = format_results(results, format="table")
```

### Logging

```python
from bizcon.core.utils import get_logger

# Get configured logger
logger = get_logger(__name__)

logger.info("Starting evaluation")
logger.debug("Detailed information")
logger.error("Error occurred", exc_info=True)
```

## 🔌 Extension Points

### Custom Model Provider

```python
from bizcon.models import ModelClient, register_model

@register_model("custom_provider")
class CustomModelClient(ModelClient):
    """Custom model implementation"""
    
    def generate_response(self, messages, tools=None, **kwargs):
        # Your implementation
        pass
        
    def get_token_count(self, text):
        # Your implementation
        pass
```

### Custom Evaluator

```python
from bizcon.evaluators import BaseEvaluator, register_evaluator

@register_evaluator
class CustomEvaluator(BaseEvaluator):
    """Custom evaluation dimension"""
    
    def __init__(self):
        super().__init__()
        self.name = "custom_metric"
        self.weight = 0.15
        
    def evaluate(self, response, scenario, metadata=None):
        # Your scoring logic
        return score
```

### Plugin System

```python
from bizcon.plugins import Plugin, register_plugin

@register_plugin
class CustomPlugin(Plugin):
    """Add custom functionality"""
    
    def on_evaluation_start(self, pipeline):
        """Called before evaluation starts"""
        
    def on_evaluation_complete(self, results):
        """Called after evaluation completes"""
        
    def modify_report(self, report_data):
        """Modify report before generation"""
```

## 🔗 Integration Examples

### Programmatic Usage

```python
import bizcon

# Simple evaluation
results = bizcon.run_evaluation(
    config_path="config/models.yaml",
    scenarios=["product_inquiry_001", "technical_support_001"]
)

# Access specific scores
overall_scores = results["overall_scores"]
best_model = max(overall_scores.items(), key=lambda x: x[1])
print(f"Best model: {best_model[0]} with score {best_model[1]}")

# Generate custom report
from bizcon.visualization import ReportGenerator

report = ReportGenerator(results)
report.add_custom_section("Executive Summary", executive_summary_html)
report.generate_html("custom_report.html")
```

### REST API Integration

```python
from bizcon.api import create_app

# Create Flask app
app = create_app()

# Run API server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# API endpoints:
# POST /evaluate - Run evaluation
# GET /results/<run_id> - Get results
# GET /dashboard/<run_id> - Launch dashboard
```

---

<p align="center">
  <strong>Common questions and troubleshooting</strong><br>
  <a href="FAQ">View FAQ →</a>
</p>