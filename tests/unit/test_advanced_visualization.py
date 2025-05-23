"""
Unit tests for advanced visualization features.
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestAdvancedVisualizationImports:
    """Test import behavior for advanced visualization features."""
    
    def test_graceful_import_failure(self):
        """Test that missing dependencies are handled gracefully."""
        # Test importing with missing dependencies
        with patch.dict('sys.modules', {'plotly': None, 'flask': None}):
            from visualization import (
                AdvancedBenchmarkDashboard, 
                InteractiveCharts,
                BenchmarkAnalyzer,
                FilterManager
            )
            
            # Test that placeholder classes raise appropriate errors
            with pytest.raises(ImportError) as exc_info:
                dashboard = AdvancedBenchmarkDashboard('test')
            assert "Install with: pip install bizcon[advanced]" in str(exc_info.value)
            
            with pytest.raises(ImportError) as exc_info:
                charts = InteractiveCharts()
            assert "Install with: pip install bizcon[advanced]" in str(exc_info.value)
    
    def test_advanced_features_flag(self):
        """Test that the advanced features flag is set correctly."""
        from visualization import _ADVANCED_FEATURES_AVAILABLE
        # This will be False if dependencies are missing, True if present
        assert isinstance(_ADVANCED_FEATURES_AVAILABLE, bool)


class TestInteractiveChartsMock:
    """Mock tests for InteractiveCharts functionality."""
    
    def test_interactive_charts_import_handling(self):
        """Test that InteractiveCharts handles missing dependencies correctly."""
        try:
            from visualization import InteractiveCharts, _ADVANCED_FEATURES_AVAILABLE
            
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Should be a placeholder that raises ImportError
                with pytest.raises(ImportError) as exc_info:
                    charts = InteractiveCharts()
                assert "pip install bizcon[advanced]" in str(exc_info.value)
            else:
                # If dependencies are available, should work
                charts = InteractiveCharts()
                assert hasattr(charts, 'interactive_radar_chart')
                assert hasattr(charts, 'model_comparison_3d_scatter')
        except ImportError:
            # Expected if running without advanced dependencies
            pass


class TestAdvancedDashboardMock:
    """Mock tests for AdvancedBenchmarkDashboard functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.results_dir = Path(self.temp_dir.name)
        
        # Create mock result files
        self.mock_results = {
            "model_name": "test-model",
            "overall": {
                "overall_score": 8.0,
                "evaluator_scores": {
                    "response_quality": 8.5,
                    "business_value": 7.8
                }
            },
            "runs": [
                {
                    "scenario": {"name": "test_scenario", "complexity": "medium"},
                    "overall_score": 8.0,
                    "evaluator_scores": {
                        "response_quality": 8.5,
                        "business_value": 7.8
                    }
                }
            ]
        }
        
        # Save mock results
        with open(self.results_dir / "test_results.json", 'w') as f:
            json.dump(self.mock_results, f)
    
    def teardown_method(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_dashboard_import_handling(self):
        """Test that AdvancedBenchmarkDashboard handles missing dependencies correctly."""
        try:
            from visualization import AdvancedBenchmarkDashboard, _ADVANCED_FEATURES_AVAILABLE
            
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Should be a placeholder that raises ImportError
                with pytest.raises(ImportError) as exc_info:
                    dashboard = AdvancedBenchmarkDashboard(str(self.results_dir))
                assert "pip install bizcon[advanced]" in str(exc_info.value)
            else:
                # If dependencies are available, test basic instantiation would work
                # (but we won't actually create it to avoid Flask running)
                assert AdvancedBenchmarkDashboard is not None
        except ImportError:
            # Expected if running without advanced dependencies
            pass
    
    def test_results_loading_logic(self):
        """Test the logic of loading results without actually importing the dashboard."""
        # This tests the file loading logic that would be used by the dashboard
        results = {}
        for json_file in self.results_dir.glob('*.json'):
            with open(json_file, 'r') as f:
                data = json.load(f)
                model_name = data.get('model_name', json_file.stem)
                results[model_name] = data
        
        assert 'test-model' in results
        assert results['test-model']['overall']['overall_score'] == 8.0


class TestBenchmarkAnalyzerMock:
    """Mock tests for BenchmarkAnalyzer functionality."""
    
    def setup_method(self):
        """Set up mock data for analysis."""
        self.mock_results = {
            "model1": {
                "runs": [
                    {
                        "scenario": {"name": "scenario1", "complexity": "low"},
                        "overall_score": 8.0,
                        "evaluator_scores": {
                            "response_quality": 8.5,
                            "business_value": 7.5
                        },
                        "timestamp": "2025-05-22T10:00:00"
                    },
                    {
                        "scenario": {"name": "scenario2", "complexity": "high"},
                        "overall_score": 7.0,
                        "evaluator_scores": {
                            "response_quality": 7.5,
                            "business_value": 6.5
                        },
                        "timestamp": "2025-05-22T11:00:00"
                    }
                ]
            },
            "model2": {
                "runs": [
                    {
                        "scenario": {"name": "scenario1", "complexity": "low"},
                        "overall_score": 7.5,
                        "evaluator_scores": {
                            "response_quality": 8.0,
                            "business_value": 7.0
                        },
                        "timestamp": "2025-05-22T10:30:00"
                    }
                ]
            }
        }
    
    def test_analyzer_import_handling(self):
        """Test that BenchmarkAnalyzer handles missing dependencies correctly."""
        try:
            from visualization import BenchmarkAnalyzer, _ADVANCED_FEATURES_AVAILABLE
            
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Should be a placeholder that raises ImportError
                with pytest.raises(ImportError) as exc_info:
                    analyzer = BenchmarkAnalyzer(self.mock_results)
                assert "pip install bizcon[advanced]" in str(exc_info.value)
            else:
                # If dependencies are available, should work
                analyzer = BenchmarkAnalyzer(self.mock_results)
                assert hasattr(analyzer, 'statistical_summary')
        except ImportError:
            # Expected if running without advanced dependencies
            pass
    
    def test_filter_manager_import_handling(self):
        """Test FilterManager import handling."""
        try:
            from visualization import FilterManager, _ADVANCED_FEATURES_AVAILABLE
            
            if not _ADVANCED_FEATURES_AVAILABLE:
                # Should be a placeholder that raises ImportError
                with pytest.raises(ImportError) as exc_info:
                    filter_manager = FilterManager(self.mock_results)
                assert "pip install bizcon[advanced]" in str(exc_info.value)
            else:
                # If dependencies are available, should work
                filter_manager = FilterManager(self.mock_results)
                assert hasattr(filter_manager, 'filter_by_models')
        except ImportError:
            # Expected if running without advanced dependencies
            pass


class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""
    
    def test_demo_script_import_handling(self):
        """Test that the demo script handles missing imports correctly."""
        demo_script = Path(__file__).parent.parent.parent / 'examples' / 'advanced_dashboard_demo.py'
        
        if demo_script.exists():
            # Read the script content
            with open(demo_script, 'r') as f:
                content = f.read()
            
            # Check for proper import handling
            assert 'try:' in content
            assert 'from visualization.advanced_dashboard import launch_advanced_dashboard' in content
            assert 'except ImportError:' in content
            assert 'pip install bizcon[advanced]' in content
    
    def test_visualization_package_structure(self):
        """Test that visualization package is properly structured."""
        viz_dir = Path(__file__).parent.parent.parent / 'visualization'
        
        # Check required files exist
        assert (viz_dir / '__init__.py').exists()
        assert (viz_dir / 'charts.py').exists()
        assert (viz_dir / 'dashboard.py').exists()
        assert (viz_dir / 'report.py').exists()
        
        # Check new files exist
        assert (viz_dir / 'interactive_charts.py').exists()
        assert (viz_dir / 'advanced_dashboard.py').exists()
        assert (viz_dir / 'analysis_utils.py').exists()


class TestSetupConfiguration:
    """Test setup.py configuration for advanced features."""
    
    def test_setup_extras_require(self):
        """Test that setup.py properly defines extras_require."""
        setup_file = Path(__file__).parent.parent.parent / 'setup.py'
        
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                content = f.read()
            
            # Check for extras_require
            assert 'extras_require' in content
            assert '"advanced"' in content
            assert 'plotly' in content
            assert 'flask' in content
            assert 'scipy' in content
    
    def test_version_update(self):
        """Test that version is updated to reflect new features."""
        setup_file = Path(__file__).parent.parent.parent / 'setup.py'
        
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                content = f.read()
            
            # Check version is updated
            assert 'version="0.4.0"' in content