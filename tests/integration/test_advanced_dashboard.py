"""
Integration tests for advanced dashboard functionality.
"""
import pytest
import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAdvancedDashboardIntegration:
    """Integration tests for the advanced dashboard with mock dependencies."""
    
    def setup_method(self):
        """Set up test environment with mock data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.results_dir = Path(self.temp_dir.name)
        
        # Create comprehensive mock results
        self.create_mock_results()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def create_mock_results(self):
        """Create realistic mock benchmark results."""
        models = ["gpt-4", "claude-3-sonnet", "mistral-large"]
        scenarios = ["product_inquiry", "technical_support", "contract_negotiation"]
        
        for model in models:
            results = {
                "model_name": model,
                "provider": model.split('-')[0],
                "timestamp": "2025-05-22T12:00:00Z",
                "overall": {
                    "overall_score": 7.5 + (models.index(model) * 0.3),
                    "total_runs": len(scenarios),
                    "evaluator_scores": {
                        "response_quality": 8.0 + (models.index(model) * 0.2),
                        "business_value": 7.5 + (models.index(model) * 0.3),
                        "communication_style": 8.5 - (models.index(model) * 0.1),
                        "tool_usage": 7.0 + (models.index(model) * 0.4),
                        "performance": 8.0 - (models.index(model) * 0.2)
                    },
                    "success_rates": {
                        "response_quality": 0.85 + (models.index(model) * 0.02),
                        "business_value": 0.75 + (models.index(model) * 0.03),
                        "communication_style": 0.90 - (models.index(model) * 0.01),
                        "tool_usage": 0.70 + (models.index(model) * 0.04),
                        "performance": 0.80 - (models.index(model) * 0.02)
                    },
                    "scenario_scores": {
                        scenario: 7.0 + (models.index(model) * 0.2) + (scenarios.index(scenario) * 0.1)
                        for scenario in scenarios
                    }
                },
                "runs": [
                    {
                        "scenario": {
                            "id": f"{scenario}_001",
                            "name": scenario.replace('_', ' ').title(),
                            "complexity": ["low", "medium", "high"][scenarios.index(scenario)],
                            "industry": "technology"
                        },
                        "overall_score": 7.0 + (models.index(model) * 0.2) + (scenarios.index(scenario) * 0.1),
                        "timestamp": f"2025-05-22T{12 + scenarios.index(scenario)}:00:00Z",
                        "evaluator_scores": {
                            "response_quality": 7.5 + (models.index(model) * 0.2),
                            "business_value": 7.0 + (models.index(model) * 0.3),
                            "communication_style": 8.0 - (models.index(model) * 0.1),
                            "tool_usage": 6.5 + (models.index(model) * 0.4),
                            "performance": 7.5 - (models.index(model) * 0.2)
                        },
                        "turns": [
                            {
                                "turn_index": i,
                                "overall_score": 7.0 + (i * 0.2),
                                "evaluator_scores": {
                                    "response_quality": 7.5 + (i * 0.1),
                                    "business_value": 7.0 + (i * 0.15)
                                }
                            }
                            for i in range(3)
                        ]
                    }
                    for scenario in scenarios
                ]
            }
            
            # Save results
            with open(self.results_dir / f"{model}_results.json", 'w') as f:
                json.dump(results, f, indent=2)
    
    @patch('visualization.advanced_dashboard.Flask')
    @patch('visualization.advanced_dashboard.InteractiveCharts')
    def test_dashboard_api_endpoints(self, mock_charts, mock_flask):
        """Test that all API endpoints are properly configured."""
        # Skip if dependencies not available
        try:
            from visualization import _ADVANCED_FEATURES_AVAILABLE
            if not _ADVANCED_FEATURES_AVAILABLE:
                pytest.skip("Advanced features not available")
        except ImportError:
            pytest.skip("Cannot import visualization module")
        
        # Mock Flask app
        mock_app = MagicMock()
        routes = {}
        
        def mock_route(path, **kwargs):
            def decorator(func):
                routes[path] = func
                return func
            return decorator
        
        mock_app.route = mock_route
        mock_flask.return_value = mock_app
        
        # Import and create dashboard
        from visualization.advanced_dashboard import AdvancedBenchmarkDashboard
        dashboard = AdvancedBenchmarkDashboard(
            results_dir=str(self.results_dir),
            auto_refresh=False
        )
        
        # Check that all expected routes are registered
        expected_routes = [
            '/',
            '/api/results',
            '/api/charts/<chart_type>',
            '/api/comparison',
            '/api/statistics',
            '/api/export/<format>',
            '/api/refresh'
        ]
        
        for route in expected_routes:
            # Check if route pattern matches
            route_found = any(route.replace('<', '').replace('>', '') in r for r in routes.keys())
            assert route_found, f"Route {route} not found in {routes.keys()}"
    
    def test_analysis_utils_with_mock_data(self):
        """Test analysis utilities with mock benchmark data."""
        try:
            from visualization import _ADVANCED_FEATURES_AVAILABLE
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Test with mock analyzer
                from visualization import BenchmarkAnalyzer
                
                # Should raise ImportError with helpful message
                with pytest.raises(ImportError) as exc_info:
                    analyzer = BenchmarkAnalyzer({})
                assert "pip install bizcon[advanced]" in str(exc_info.value)
                return
        except ImportError:
            pytest.skip("Cannot import visualization module")
        
        # If dependencies are available, test actual functionality
        from visualization.analysis_utils import BenchmarkAnalyzer, FilterManager
        
        # Load mock results
        results = {}
        for json_file in self.results_dir.glob('*.json'):
            with open(json_file, 'r') as f:
                data = json.load(f)
                model_name = data.get('model_name')
                results[model_name] = data
        
        # Test BenchmarkAnalyzer
        analyzer = BenchmarkAnalyzer(results)
        
        # Test statistical summary
        summary = analyzer.statistical_summary()
        assert 'overall' in summary
        assert summary['overall']['total_models'] == 3
        assert 'per_model' in summary
        assert 'per_scenario' in summary
        
        # Test model ranking
        rankings = analyzer.model_ranking()
        assert len(rankings) == 3
        assert all('model' in r and 'composite_score' in r for r in rankings)
        
        # Test FilterManager
        filter_manager = FilterManager(results)
        
        # Test model filtering
        filtered = filter_manager.filter_by_models(['gpt-4', 'claude-3-sonnet'])
        assert len(filtered) == 2
        assert 'mistral-large' not in filtered
        
        # Test scenario filtering
        filtered = filter_manager.filter_by_scenarios(['product_inquiry'])
        assert all(
            any('product' in run['scenario']['name'].lower() 
                for run in model_data.get('runs', []))
            for model_data in filtered.values()
        )
    
    def test_interactive_charts_mock(self):
        """Test interactive charts with mock plotly."""
        try:
            from visualization import _ADVANCED_FEATURES_AVAILABLE
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Test placeholder functionality
                from visualization import InteractiveCharts
                
                with pytest.raises(ImportError) as exc_info:
                    charts = InteractiveCharts()
                assert "pip install bizcon[advanced]" in str(exc_info.value)
                return
        except ImportError:
            pytest.skip("Cannot import visualization module")
        
        # If dependencies available, mock plotly and test
        with patch('visualization.interactive_charts.go') as mock_go:
            with patch('visualization.interactive_charts.px') as mock_px:
                from visualization.interactive_charts import InteractiveCharts
                
                # Mock figure
                mock_fig = MagicMock()
                mock_go.Figure.return_value = mock_fig
                
                # Create charts instance
                charts = InteractiveCharts()
                
                # Test data
                test_scores = {
                    "model1": {"metric1": 8.0, "metric2": 7.5},
                    "model2": {"metric1": 7.5, "metric2": 8.0}
                }
                
                # Test radar chart
                fig = charts.interactive_radar_chart(test_scores)
                mock_go.Figure.assert_called()
                
                # Test 3D scatter
                fig = charts.model_comparison_3d_scatter(test_scores)
                assert mock_go.Figure.call_count >= 2
    
    def test_demo_script_functionality(self):
        """Test that the demo script works correctly."""
        demo_script = Path(__file__).parent.parent.parent / 'examples' / 'advanced_dashboard_demo.py'
        
        if not demo_script.exists():
            pytest.skip("Demo script not found")
        
        # Test importing the demo script
        import importlib.util
        spec = importlib.util.spec_from_file_location("advanced_dashboard_demo", demo_script)
        demo_module = importlib.util.module_from_spec(spec)
        
        # Mock sys.exit to prevent script from exiting
        with patch('sys.exit'):
            try:
                spec.loader.exec_module(demo_module)
            except SystemExit:
                pass  # Expected if dependencies missing
            except ImportError as e:
                # Should show helpful error message
                assert "pip install bizcon[advanced]" in str(e) or "Advanced dashboard features require" in str(e)
    
    def test_dashboard_data_loading(self):
        """Test that dashboard correctly loads and processes data."""
        try:
            from visualization import _ADVANCED_FEATURES_AVAILABLE
            if not _ADVANCED_FEATURES_AVAILABLE:
                pytest.skip("Advanced features not available")
        except ImportError:
            pytest.skip("Cannot import visualization module")
        
        from visualization.advanced_dashboard import AdvancedBenchmarkDashboard
        
        # Create dashboard instance with mocked Flask
        with patch('visualization.advanced_dashboard.Flask'):
            dashboard = AdvancedBenchmarkDashboard(
                results_dir=str(self.results_dir),
                auto_refresh=False
            )
            
            # Test loading results
            results = dashboard._load_results()
            assert len(results) == 3
            assert all(model in results for model in ["gpt-4", "claude-3-sonnet", "mistral-large"])
            
            # Test filtering
            filtered = dashboard._filter_results(
                results,
                models=["gpt-4"],
                scenarios=["product_inquiry"]
            )
            assert len(filtered) == 1
            assert "gpt-4" in filtered
            
            # Test data extraction
            evaluator_scores = dashboard._extract_evaluator_scores(results)
            assert len(evaluator_scores) == 3
            assert all("response_quality" in scores for scores in evaluator_scores.values())
            
            # Test statistics calculation
            stats = dashboard._calculate_statistics(results)
            assert stats['total_models'] == 3
            assert stats['total_scenarios'] == 3
            assert stats['total_runs'] == 9  # 3 models × 3 scenarios


class TestAdvancedVisualizationEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_results_directory(self):
        """Test handling of empty results directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                from visualization import _ADVANCED_FEATURES_AVAILABLE
                if not _ADVANCED_FEATURES_AVAILABLE:
                    pytest.skip("Advanced features not available")
                
                from visualization.advanced_dashboard import AdvancedBenchmarkDashboard
                
                with patch('visualization.advanced_dashboard.Flask'):
                    dashboard = AdvancedBenchmarkDashboard(
                        results_dir=temp_dir,
                        auto_refresh=False
                    )
                    
                    results = dashboard._load_results()
                    assert len(results) == 0
                    
                    stats = dashboard._calculate_statistics(results)
                    assert stats['total_models'] == 0
                    
            except ImportError:
                pass  # Expected if dependencies missing
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create malformed JSON
            bad_json = Path(temp_dir) / "bad.json"
            bad_json.write_text("{ this is not valid json")
            
            try:
                from visualization import _ADVANCED_FEATURES_AVAILABLE
                if not _ADVANCED_FEATURES_AVAILABLE:
                    pytest.skip("Advanced features not available")
                
                from visualization.advanced_dashboard import AdvancedBenchmarkDashboard
                
                with patch('visualization.advanced_dashboard.Flask'):
                    dashboard = AdvancedBenchmarkDashboard(
                        results_dir=temp_dir,
                        auto_refresh=False
                    )
                    
                    # Should handle error gracefully
                    results = dashboard._load_results()
                    assert len(results) == 0  # Bad file skipped
                    
            except ImportError:
                pass  # Expected if dependencies missing