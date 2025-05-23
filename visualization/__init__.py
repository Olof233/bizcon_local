# filepath: /Users/ahstanin/GitHub/Olib-AI/bizcon/visualization/__init__.py
"""
bizCon visualization package with advanced dashboard capabilities.
"""
# Use relative imports instead of bizcon package imports
from .charts import (
    model_comparison_radar,
    scenario_comparison_heatmap,
    tool_usage_bar_chart,
    performance_trend_line,
    breakdown_stacked_bar,
    success_rate_chart
)

from .dashboard import (
    BenchmarkDashboard,
    launch_dashboard
)

# Optional advanced features (require additional dependencies)
try:
    from .advanced_dashboard import (
        AdvancedBenchmarkDashboard,
        launch_advanced_dashboard
    )
    from .interactive_charts import (
        InteractiveCharts
    )
    from .analysis_utils import (
        BenchmarkAnalyzer,
        FilterManager
    )
    _ADVANCED_FEATURES_AVAILABLE = True
except ImportError as import_error:
    # Create placeholder classes/functions for missing dependencies
    _missing_deps_msg = f"Advanced features require additional dependencies. Install with: pip install \"bizcon[advanced]\""
    
    class AdvancedBenchmarkDashboard:
        def __init__(self, *args, **kwargs):
            raise ImportError(_missing_deps_msg)
    
    def launch_advanced_dashboard(*args, **kwargs):
        raise ImportError(_missing_deps_msg)
    
    class InteractiveCharts:
        def __init__(self, *args, **kwargs):
            raise ImportError(_missing_deps_msg)
    
    class BenchmarkAnalyzer:
        def __init__(self, *args, **kwargs):
            raise ImportError(_missing_deps_msg)
    
    class FilterManager:
        def __init__(self, *args, **kwargs):
            raise ImportError(_missing_deps_msg)
    
    _ADVANCED_FEATURES_AVAILABLE = False

from .report import (
    BenchmarkReport
)

__all__ = [
    # Chart functions
    'model_comparison_radar',
    'scenario_comparison_heatmap',
    'tool_usage_bar_chart',
    'performance_trend_line', 
    'breakdown_stacked_bar',
    'success_rate_chart',
    
    # Dashboard classes and functions
    'BenchmarkDashboard',
    'launch_dashboard',
    'AdvancedBenchmarkDashboard',
    'launch_advanced_dashboard',
    
    # Interactive charts
    'InteractiveCharts',
    
    # Analysis utilities
    'BenchmarkAnalyzer',
    'FilterManager',
    
    # Report classes and functions
    'BenchmarkReport'
]