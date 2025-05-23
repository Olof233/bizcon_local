# Evaluation System

bizCon uses a comprehensive evaluation system with five key dimensions to assess LLM performance in business contexts. Each dimension is scored independently and weighted to produce an overall score.

## 📊 Evaluation Dimensions

### Overview

| Dimension | Weight | Focus Area | Key Metrics |
|-----------|-------:|------------|-------------|
| [Response Quality](#response-quality) | 25% | Accuracy & Completeness | Factual correctness, information coverage |
| [Business Value](#business-value) | 25% | Strategic Insights | ROI focus, actionable recommendations |
| [Communication Style](#communication-style) | 20% | Professionalism | Tone, clarity, structure |
| [Tool Usage](#tool-usage) | 20% | System Integration | Tool selection, data interpretation |
| [Performance](#performance) | 10% | Efficiency | Response time, token usage |

## 🎯 Detailed Dimension Descriptions

### Response Quality

**Purpose**: Evaluates the factual accuracy and completeness of responses.

**Scoring Criteria**:
- **Factual Accuracy** (40%): Information correctness
- **Completeness** (30%): Addressing all aspects of the query
- **Relevance** (30%): Staying on topic without unnecessary information

**Evaluation Method**:
```python
class ResponseQualityEvaluator(BaseEvaluator):
    def evaluate(self, response, scenario):
        score = 0.0
        
        # Check against ground truth
        if self._check_facts(response, scenario.ground_truth):
            score += 0.4
            
        # Assess completeness
        if self._all_points_addressed(response, scenario.required_points):
            score += 0.3
            
        # Measure relevance
        if self._is_relevant(response, scenario.context):
            score += 0.3
            
        return score
```

**Example Scoring**:
- **Excellent (0.9-1.0)**: All facts correct, comprehensive coverage, highly relevant
- **Good (0.7-0.89)**: Mostly accurate, covers main points, generally relevant
- **Fair (0.5-0.69)**: Some inaccuracies, missing key points, partially relevant
- **Poor (0-0.49)**: Significant errors, incomplete, off-topic

### Business Value

**Purpose**: Assesses strategic thinking and business impact of recommendations.

**Scoring Criteria**:
- **Strategic Insight** (35%): Understanding of business implications
- **Actionable Recommendations** (35%): Practical next steps
- **ROI Consideration** (30%): Cost-benefit awareness

**Evaluation Method**:
```python
class BusinessValueEvaluator(BaseEvaluator):
    def evaluate(self, response, scenario):
        score = 0.0
        
        # Strategic thinking
        if self._demonstrates_business_acumen(response):
            score += 0.35
            
        # Actionable advice
        if self._provides_clear_next_steps(response):
            score += 0.35
            
        # ROI awareness
        if self._considers_cost_benefit(response):
            score += 0.3
            
        return score
```

**Example Scoring**:
- **Excellent**: Identifies strategic opportunities, clear roadmap, quantified benefits
- **Good**: Solid business understanding, practical suggestions, cost awareness
- **Fair**: Basic business sense, generic recommendations, limited ROI discussion
- **Poor**: No strategic thinking, vague suggestions, ignores business impact

### Communication Style

**Purpose**: Evaluates professional communication effectiveness.

**Scoring Criteria**:
- **Professional Tone** (40%): Appropriate formality and respect
- **Clarity** (35%): Easy to understand, well-structured
- **Engagement** (25%): Personalized, empathetic when needed

**Evaluation Method**:
```python
class CommunicationStyleEvaluator(BaseEvaluator):
    def evaluate(self, response, scenario):
        score = 0.0
        
        # Professional tone
        if self._is_professional(response, scenario.formality_level):
            score += 0.4
            
        # Clear communication
        if self._is_clear_and_structured(response):
            score += 0.35
            
        # Engagement quality
        if self._shows_appropriate_engagement(response, scenario.context):
            score += 0.25
            
        return score
```

**Example Scoring**:
- **Excellent**: Perfect professional tone, crystal clear, highly engaging
- **Good**: Professional, well-structured, appropriately personalized
- **Fair**: Mostly professional, somewhat clear, basic engagement
- **Poor**: Inappropriate tone, confusing, impersonal or overly casual

### Tool Usage

**Purpose**: Measures effectiveness of business tool integration.

**Scoring Criteria**:
- **Tool Selection** (40%): Choosing the right tools for the task
- **Execution Accuracy** (35%): Correct parameter usage
- **Data Interpretation** (25%): Making sense of tool outputs

**Evaluation Method**:
```python
class ToolUsageEvaluator(BaseEvaluator):
    def evaluate(self, response, scenario):
        score = 0.0
        
        # Correct tool selection
        if self._selected_appropriate_tools(response.tool_calls, scenario.required_tools):
            score += 0.4
            
        # Proper execution
        if self._executed_correctly(response.tool_calls):
            score += 0.35
            
        # Result interpretation
        if self._interpreted_results_well(response, response.tool_results):
            score += 0.25
            
        return score
```

**Example Scoring**:
- **Excellent**: Perfect tool choices, flawless execution, insightful interpretation
- **Good**: Mostly correct tools, minor parameter issues, good interpretation
- **Fair**: Some wrong tools, execution errors, basic interpretation
- **Poor**: Wrong tools, failed execution, misinterprets results

### Performance

**Purpose**: Tracks efficiency metrics for cost and speed optimization.

**Scoring Criteria**:
- **Response Time** (50%): Speed of response generation
- **Token Efficiency** (30%): Conciseness without losing quality
- **Cost Effectiveness** (20%): Value per dollar spent

**Evaluation Method**:
```python
class PerformanceEvaluator(BaseEvaluator):
    def evaluate(self, response, scenario):
        score = 0.0
        
        # Response time (baseline: 5 seconds)
        time_score = max(0, 1 - (response.latency / 5.0))
        score += time_score * 0.5
        
        # Token efficiency (baseline: 500 tokens)
        token_score = max(0, 1 - (response.tokens / 500))
        score += token_score * 0.3
        
        # Cost effectiveness
        cost_score = self._calculate_value_per_dollar(response)
        score += cost_score * 0.2
        
        return score
```

**Example Scoring**:
- **Excellent**: < 2s response, < 200 tokens, high value/cost ratio
- **Good**: 2-4s response, 200-400 tokens, good value/cost
- **Fair**: 4-6s response, 400-600 tokens, acceptable value/cost
- **Poor**: > 6s response, > 600 tokens, poor value/cost

## 📈 Scoring Methodology

### Score Calculation

1. **Individual Dimension Scores**: Each evaluator returns a score from 0 to 1
2. **Weighted Average**: Scores are combined using configured weights
3. **Overall Score**: Final score out of 100

```python
def calculate_overall_score(evaluator_scores, weights):
    total = 0
    for evaluator, score in evaluator_scores.items():
        total += score * weights[evaluator]
    return total * 100  # Convert to percentage
```

### Success Rate Calculation

Success rates are dynamically calculated based on performance:

```python
def calculate_success_rate(score, base_rate=0.75):
    # Adjust base rate based on performance
    score_ratio = score / 100
    adjustment = (score_ratio - 0.75) * 0.3
    return min(1.0, max(0.0, base_rate + adjustment))
```

## 🎨 Evaluation Reports

### Score Visualization

Reports include multiple visualizations:
- **Overall Scores**: Bar chart comparing total scores
- **Dimension Breakdown**: Radar chart showing strengths/weaknesses
- **Scenario Performance**: Heatmap of model × scenario scores
- **Trend Analysis**: Performance over multiple runs

### Detailed Feedback

Each evaluation provides:
```json
{
    "dimension": "response_quality",
    "score": 0.85,
    "feedback": "Strong factual accuracy with comprehensive coverage. Minor relevance issues in technical details.",
    "strengths": ["Accurate information", "Complete responses"],
    "improvements": ["Reduce technical tangents"]
}
```

## 🔧 Custom Evaluators

### Creating New Evaluators

To add custom evaluation dimensions:

```python
from evaluators.base import BaseEvaluator, register_evaluator

@register_evaluator
class CustomEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__()
        self.name = "custom_dimension"
        self.weight = 0.15  # 15% of total score
        
    def evaluate(self, response, scenario):
        # Custom evaluation logic
        score = self._custom_scoring_logic(response)
        return score
        
    def get_feedback(self, score):
        if score > 0.8:
            return "Excellent custom performance"
        elif score > 0.6:
            return "Good custom performance"
        else:
            return "Needs improvement in custom dimension"
```

### Configuring Evaluator Weights

Adjust weights in `config/evaluation.yaml`:

```yaml
evaluator_weights:
  response_quality: 0.30      # Increase focus on accuracy
  business_value: 0.30        # Emphasize business impact
  communication_style: 0.15   # Reduce style weight
  tool_usage: 0.15           # Reduce tool weight
  performance: 0.10          # Keep performance weight
  custom_dimension: 0.15     # Add custom evaluator
```

## 📊 Evaluation Best Practices

1. **Balanced Weights**: Ensure weights reflect your priorities
2. **Scenario Relevance**: Some dimensions matter more for certain scenarios
3. **Multiple Runs**: Average across runs for statistical significance
4. **Baseline Comparison**: Compare against human performance benchmarks
5. **Continuous Calibration**: Adjust scoring based on real-world feedback

---

<p align="center">
  <strong>Configure your evaluation settings</strong><br>
  <a href="Configuration">View Configuration Guide →</a>
</p>