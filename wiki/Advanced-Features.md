# Advanced Features

bizCon includes powerful visualization and analysis features for deep insights into LLM performance. This guide covers the interactive dashboard, advanced analytics, and report customization options.

## 🎨 Interactive Dashboard

### Overview

The interactive dashboard provides real-time exploration of evaluation results with filtering, comparison, and drill-down capabilities.

### Starting the Dashboard

```bash
# Launch dashboard after evaluation
bizcon dashboard --results results/run_20250523_150000/

# Launch with specific port
bizcon dashboard --results results/latest/ --port 8080

# Python API
from bizcon.visualization import launch_dashboard
launch_dashboard("results/run_20250523_150000/", port=8050)
```

### Dashboard Components

#### 1. Overview Tab
- **Model Performance Summary**: Overall scores and rankings
- **Quick Stats**: Total evaluations, average scores, best performers
- **Performance Timeline**: Scores across multiple runs

#### 2. Comparative Analysis Tab
- **Model Comparison Matrix**: Side-by-side model performance
- **Dimension Breakdown**: Radar charts for each model
- **Statistical Significance**: Confidence intervals and p-values

#### 3. Scenario Analysis Tab
- **Scenario Heatmap**: Model × Scenario performance grid
- **Difficulty Analysis**: Performance vs scenario complexity
- **Tool Usage Patterns**: Which tools were used when

#### 4. Deep Dive Tab
- **Individual Conversations**: Browse actual model responses
- **Error Analysis**: Common failure patterns
- **Token Economics**: Cost vs quality analysis

### Interactive Features

#### Filtering
```javascript
// Real-time filtering options
filters = {
    models: ["gpt-4", "claude-3-opus"],
    scenarios: ["product_inquiry_001", "technical_support_001"],
    score_range: [75, 100],
    date_range: ["2025-05-01", "2025-05-31"]
}
```

#### Dynamic Charts
- **Hover Details**: See exact scores and metadata
- **Zoom & Pan**: Focus on specific data ranges
- **Export**: Save charts as PNG/SVG
- **Responsive**: Adapts to screen size

## 📊 Advanced Analytics

### Statistical Analysis

#### Performance Metrics
```python
from bizcon.visualization import AnalysisUtils

# Load results
analysis = AnalysisUtils("results/run_20250523_150000/")

# Statistical summary
stats = analysis.get_statistical_summary()
print(stats)
# Output:
# {
#     'mean_scores': {'gpt-4': 85.2, 'claude-3-opus': 83.7},
#     'std_dev': {'gpt-4': 3.2, 'claude-3-opus': 4.1},
#     'confidence_95': {'gpt-4': [82.0, 88.4], 'claude-3-opus': [79.6, 87.8]}
# }
```

#### Correlation Analysis
```python
# Find correlations between dimensions
correlations = analysis.dimension_correlations()
# Shows which evaluation dimensions tend to correlate
```

#### Trend Analysis
```python
# Analyze performance trends across runs
trends = analysis.analyze_trends()
# Identifies improving/declining performance patterns
```

### Cost-Benefit Analysis

```python
# Calculate value metrics
cost_analysis = analysis.cost_benefit_analysis()

# Results include:
# - Cost per point of quality score
# - Token efficiency ratings  
# - ROI calculations
# - Optimal model for budget constraints
```

### Scenario Clustering

```python
# Group similar scenarios
clusters = analysis.cluster_scenarios()

# Helps identify:
# - Scenario categories where models excel
# - Common failure patterns
# - Training recommendations
```

## 🎯 Custom Visualizations

### Creating Custom Charts

```python
from bizcon.visualization import ChartBuilder

# Initialize with results
charts = ChartBuilder("results/run_20250523_150000/")

# Custom bar chart
fig = charts.create_custom_bar_chart(
    x_axis="models",
    y_axis="business_value_score",
    color_by="scenario_category",
    title="Business Value by Model and Category"
)
fig.show()

# Custom scatter plot
fig = charts.create_scatter_plot(
    x="response_time",
    y="quality_score",
    size="token_count",
    color="model",
    title="Quality vs Speed Trade-off"
)
```

### Advanced Chart Types

#### Sankey Diagrams
Show tool usage flow:
```python
fig = charts.create_sankey_diagram(
    source="scenarios",
    target="tools_used",
    values="usage_count"
)
```

#### 3D Surface Plots
Visualize multi-dimensional relationships:
```python
fig = charts.create_3d_surface(
    x="complexity",
    y="token_count",
    z="quality_score",
    color="model"
)
```

#### Animation
Show performance over time:
```python
fig = charts.create_animated_bar_chart(
    animation_frame="run_number",
    title="Model Performance Evolution"
)
```

## 📈 Report Customization

### HTML Report Templates

Customize the HTML report appearance:

```python
from bizcon.visualization import ReportGenerator

# Custom template
report = ReportGenerator(
    results_dir="results/run_20250523_150000/",
    template="custom_template.html",
    theme="dark"
)

# Add custom sections
report.add_section(
    title="Executive Summary",
    content=custom_executive_summary_html
)

# Generate report
report.generate("custom_report.html")
```

### Markdown Reports

Generate detailed markdown reports:

```python
# Markdown with custom sections
report.generate_markdown(
    include_sections=[
        "summary",
        "methodology", 
        "detailed_results",
        "recommendations"
    ],
    include_raw_data=True
)
```

### PDF Generation

Create professional PDF reports:

```python
# Requires wkhtmltopdf or weasyprint
report.generate_pdf(
    "evaluation_report.pdf",
    include_cover_page=True,
    company_logo="logo.png"
)
```

## 🔄 Real-time Monitoring

### Live Evaluation Tracking

Monitor evaluations in progress:

```python
from bizcon.visualization import LiveMonitor

# Start monitoring
monitor = LiveMonitor()
monitor.start(port=8090)

# In another terminal, run evaluation
# The monitor will show real-time progress
```

### Webhook Integration

Send results to external systems:

```yaml
# config/evaluation.yaml
webhooks:
  completion:
    url: "https://your-api.com/bizcon/results"
    method: POST
    headers:
      Authorization: "Bearer token"
  
  failure:
    url: "https://your-api.com/bizcon/alerts"
```

## 🎮 Advanced Dashboard Features

### Custom Dashboards

Create specialized dashboards:

```python
from bizcon.visualization import DashboardBuilder

# Build custom dashboard
builder = DashboardBuilder()

# Add custom tab
builder.add_tab(
    name="Cost Analysis",
    layout=[
        builder.cost_per_quality_chart(),
        builder.token_usage_timeline(),
        builder.roi_calculator()
    ]
)

# Launch
builder.launch(port=8060)
```

### Dashboard Plugins

Extend dashboard functionality:

```python
# Create plugin
class CustomMetricPlugin:
    def __init__(self):
        self.name = "custom_metrics"
        
    def calculate(self, results):
        # Custom metric calculation
        return custom_scores
        
    def render(self):
        # Return Plotly figure
        return custom_chart

# Register plugin
dashboard.register_plugin(CustomMetricPlugin())
```

## 📊 Export Options

### Data Export Formats

```python
# Export to various formats
from bizcon.visualization import DataExporter

exporter = DataExporter("results/run_20250523_150000/")

# Excel with multiple sheets
exporter.to_excel("results.xlsx", include_charts=True)

# SQL database
exporter.to_sql("sqlite:///results.db", table_name="evaluations")

# Parquet for big data processing
exporter.to_parquet("results.parquet")

# JSON with custom schema
exporter.to_json("results.json", schema="custom_schema.json")
```

### Integration with BI Tools

Connect to business intelligence platforms:

```python
# Tableau
exporter.to_tableau_extract("results.tde")

# Power BI
exporter.to_powerbi_dataset("results.pbix")

# Looker
exporter.to_lookml("results.lookml")
```

## 🚀 Performance Optimization

### Large Dataset Handling

```yaml
# config/visualization.yaml
performance:
  # Sampling for large datasets
  max_points_per_chart: 10000
  sampling_method: "stratified"
  
  # Caching
  enable_cache: true
  cache_backend: "redis"
  cache_ttl: 3600
  
  # Aggregation
  pre_aggregate: true
  aggregation_levels: ["model", "scenario", "category"]
```

### Distributed Processing

```python
# Use Dask for distributed analytics
from bizcon.visualization import DistributedAnalysis

analysis = DistributedAnalysis(
    results_dir="results/",
    cluster="dask-cluster:8786"
)

# Parallel processing of large result sets
summary = analysis.distributed_summary()
```

---

<p align="center">
  <strong>Learn about testing strategies</strong><br>
  <a href="Testing-Guide">View Testing Guide →</a>
</p>