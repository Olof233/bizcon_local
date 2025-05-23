"""
Advanced interactive dashboard with real-time updates, filtering, and comparison tools.
"""
from typing import Dict, List, Any, Optional, Union
import json
import os
import datetime
import tempfile
from pathlib import Path
import threading
import time

from flask import Flask, render_template, request, jsonify, send_from_directory
import plotly
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from .interactive_charts import InteractiveCharts
from .charts import set_plotting_style


class AdvancedBenchmarkDashboard:
    """Advanced interactive dashboard with enhanced features."""
    
    def __init__(self, 
                 results_dir: str,
                 host: str = '127.0.0.1',
                 port: int = 5001,
                 auto_refresh: bool = True,
                 refresh_interval: int = 30):
        """
        Initialize the advanced dashboard.
        
        Args:
            results_dir: Directory containing benchmark results
            host: Host to run the dashboard server on
            port: Port to run the dashboard server on
            auto_refresh: Enable automatic data refresh
            refresh_interval: Refresh interval in seconds
        """
        self.results_dir = Path(results_dir)
        self.host = host
        self.port = port
        self.auto_refresh = auto_refresh
        self.refresh_interval = refresh_interval
        
        self.chart_generator = InteractiveCharts()
        self.app = self._create_app()
        self._cached_results = None
        self._last_update = None
        
        # Start auto-refresh thread if enabled
        if self.auto_refresh:
            self._start_refresh_thread()
    
    def _create_app(self) -> Flask:
        """Create the Flask application with advanced features."""
        app = Flask(__name__)
        app.json_encoder = PlotlyJSONEncoder
        
        @app.route('/')
        def index():
            """Render the advanced dashboard homepage."""
            return render_template('advanced_dashboard.html',
                                 title='bizCon Advanced Dashboard',
                                 timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        @app.route('/api/results')
        def results():
            """API endpoint for getting benchmark results with optional filtering."""
            models = request.args.getlist('models')
            scenarios = request.args.getlist('scenarios')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            results = self._load_results()
            filtered_results = self._filter_results(results, models, scenarios, date_from, date_to)
            
            return jsonify({
                'data': filtered_results,
                'last_update': self._last_update,
                'total_models': len(results),
                'filtered_models': len(filtered_results)
            })
        
        @app.route('/api/charts/<chart_type>')
        def interactive_charts(chart_type):
            """API endpoint for interactive Plotly charts."""
            results = self._load_results()
            
            # Apply filters if provided
            models = request.args.getlist('models')
            scenarios = request.args.getlist('scenarios')
            if models or scenarios:
                results = self._filter_results(results, models, scenarios)
            
            try:
                if chart_type == 'radar':
                    evaluator_scores = self._extract_evaluator_scores(results)
                    fig = self.chart_generator.interactive_radar_chart(evaluator_scores)
                
                elif chart_type == '3d_scatter':
                    evaluator_scores = self._extract_evaluator_scores(results)
                    dimensions = request.args.getlist('dimensions')
                    fig = self.chart_generator.model_comparison_3d_scatter(evaluator_scores, dimensions)
                
                elif chart_type == 'heatmap':
                    scenario_scores = self._extract_scenario_scores(results)
                    fig = self.chart_generator.interactive_heatmap_with_dendogram(scenario_scores)
                
                elif chart_type == 'parallel':
                    evaluator_scores = self._extract_evaluator_scores(results)
                    fig = self.chart_generator.parallel_coordinates_comparison(evaluator_scores)
                
                elif chart_type == 'sunburst':
                    evaluator_scores = self._extract_evaluator_scores(results)
                    fig = self.chart_generator.sunburst_performance_breakdown(evaluator_scores)
                
                elif chart_type == 'timeline':
                    turn_scores = self._extract_turn_scores(results)
                    metric = request.args.get('metric', 'overall_score')
                    fig = self.chart_generator.animated_performance_timeline(turn_scores, metric)
                
                elif chart_type == 'boxplot':
                    scenario_results = self._extract_scenario_results(results)
                    fig = self.chart_generator.interactive_box_plots(scenario_results)
                
                else:
                    return jsonify({'error': f'Unknown chart type: {chart_type}'}), 400
                
                # Convert to JSON for frontend
                chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
                return jsonify({'chart': chart_json})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/comparison')
        def model_comparison():
            """API endpoint for detailed model comparison."""
            model1 = request.args.get('model1')
            model2 = request.args.get('model2')
            
            if not model1 or not model2:
                return jsonify({'error': 'Both model1 and model2 parameters required'}), 400
            
            results = self._load_results()
            comparison = self._compare_models(results, model1, model2)
            
            return jsonify(comparison)
        
        @app.route('/api/statistics')
        def statistics():
            """API endpoint for dashboard statistics."""
            results = self._load_results()
            stats = self._calculate_statistics(results)
            return jsonify(stats)
        
        @app.route('/api/export/<format>')
        def export_data(format):
            """API endpoint for exporting data in various formats."""
            results = self._load_results()
            
            if format == 'json':
                return jsonify(results)
            elif format == 'csv':
                csv_data = self._convert_to_csv(results)
                return csv_data
            elif format == 'excel':
                excel_file = self._convert_to_excel(results)
                return send_from_directory(
                    directory=str(self.results_dir),
                    path=excel_file,
                    as_attachment=True
                )
            else:
                return jsonify({'error': f'Unsupported format: {format}'}), 400
        
        @app.route('/api/refresh')
        def manual_refresh():
            """API endpoint for manual data refresh."""
            self._clear_cache()
            results = self._load_results()
            return jsonify({
                'status': 'refreshed',
                'timestamp': self._last_update,
                'models_count': len(results)
            })
        
        # Create template files
        self._create_template_files()
        
        return app
    
    def _load_results(self) -> Dict[str, Any]:
        """Load and cache benchmark results."""
        # Check if cache is still valid
        if self._cached_results and self._last_update:
            cache_age = (datetime.datetime.now() - self._last_update).seconds
            if cache_age < self.refresh_interval:
                return self._cached_results
        
        results = {}
        latest_time = None
        
        for json_file in self.results_dir.glob('*.json'):
            # Skip aggregate result files
            if json_file.stem in ['results', 'test_results']:
                continue
                
            try:
                file_mtime = datetime.datetime.fromtimestamp(json_file.stat().st_mtime)
                if not latest_time or file_mtime > latest_time:
                    latest_time = file_mtime
                
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    # Only load files that have the expected model structure
                    if 'runs' in data and 'overall' in data:
                        model_name = data.get('model_name', json_file.stem)
                        data['file_timestamp'] = file_mtime.isoformat()
                        results[model_name] = data
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        self._cached_results = results
        self._last_update = latest_time or datetime.datetime.now()
        
        return results
    
    def _filter_results(self, 
                       results: Dict[str, Any], 
                       models: List[str] = None,
                       scenarios: List[str] = None,
                       date_from: str = None,
                       date_to: str = None) -> Dict[str, Any]:
        """Filter results based on criteria."""
        filtered = {}
        
        for model_name, model_data in results.items():
            # Filter by models
            if models and model_name not in models:
                continue
                
            # Filter by date range
            if date_from or date_to:
                file_timestamp = model_data.get('file_timestamp')
                if file_timestamp:
                    file_date = datetime.datetime.fromisoformat(file_timestamp.replace('Z', '+00:00'))
                    if date_from and file_date < datetime.datetime.fromisoformat(date_from):
                        continue
                    if date_to and file_date > datetime.datetime.fromisoformat(date_to):
                        continue
            
            # Filter by scenarios
            if scenarios:
                filtered_runs = []
                for run in model_data.get('runs', []):
                    scenario_name = run.get('scenario', {}).get('name', '')
                    if any(scenario in scenario_name for scenario in scenarios):
                        filtered_runs.append(run)
                
                if filtered_runs:
                    model_data_copy = model_data.copy()
                    model_data_copy['runs'] = filtered_runs
                    filtered[model_name] = model_data_copy
            else:
                filtered[model_name] = model_data
        
        return filtered
    
    def _extract_evaluator_scores(self, results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract evaluator scores from results."""
        evaluator_scores = {}
        for model, model_data in results.items():
            if 'overall' in model_data and 'evaluator_scores' in model_data['overall']:
                evaluator_scores[model] = model_data['overall']['evaluator_scores']
        return evaluator_scores
    
    def _extract_scenario_scores(self, results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract scenario scores from results."""
        scenario_scores = {}
        for model, model_data in results.items():
            scenario_scores[model] = {}
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                scenario_scores[model][scenario_name] = run.get('overall_score', 0)
        return scenario_scores
    
    def _extract_turn_scores(self, results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract turn-by-turn scores."""
        turn_scores = {}
        for model, model_data in results.items():
            turns = []
            for run in model_data.get('runs', []):
                for turn in run.get('turns', []):
                    turns.append({
                        'overall_score': turn.get('overall_score', 0),
                        'details': turn.get('evaluator_scores', {})
                    })
            turn_scores[model] = turns
        return turn_scores
    
    def _extract_scenario_results(self, results: Dict[str, Any]) -> Dict[str, List[Dict[str, float]]]:
        """Extract scenario results for box plots."""
        scenario_results = {}
        for model, model_data in results.items():
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                if scenario_name not in scenario_results:
                    scenario_results[scenario_name] = []
                scenario_results[scenario_name].append({model: run.get('overall_score', 0)})
        return scenario_results
    
    def _compare_models(self, results: Dict[str, Any], model1: str, model2: str) -> Dict[str, Any]:
        """Generate detailed comparison between two models."""
        if model1 not in results or model2 not in results:
            return {'error': 'One or both models not found'}
        
        data1 = results[model1]
        data2 = results[model2]
        
        comparison = {
            'models': [model1, model2],
            'overall_scores': {
                model1: data1.get('overall', {}).get('overall_score', 0),
                model2: data2.get('overall', {}).get('overall_score', 0)
            },
            'evaluator_comparison': {},
            'scenario_comparison': {},
            'strengths_weaknesses': self._analyze_strengths_weaknesses(data1, data2, model1, model2)
        }
        
        # Compare evaluator scores
        eval1 = data1.get('overall', {}).get('evaluator_scores', {})
        eval2 = data2.get('overall', {}).get('evaluator_scores', {})
        
        for evaluator in set(list(eval1.keys()) + list(eval2.keys())):
            score1 = eval1.get(evaluator, 0)
            score2 = eval2.get(evaluator, 0)
            comparison['evaluator_comparison'][evaluator] = {
                model1: score1,
                model2: score2,
                'difference': score1 - score2,
                'winner': model1 if score1 > score2 else model2 if score2 > score1 else 'tie'
            }
        
        return comparison
    
    def _analyze_strengths_weaknesses(self, data1: Dict, data2: Dict, model1: str, model2: str) -> Dict[str, List[str]]:
        """Analyze relative strengths and weaknesses."""
        eval1 = data1.get('overall', {}).get('evaluator_scores', {})
        eval2 = data2.get('overall', {}).get('evaluator_scores', {})
        
        strengths = {model1: [], model2: []}
        weaknesses = {model1: [], model2: []}
        
        for evaluator in eval1.keys():
            if evaluator in eval2:
                diff = eval1[evaluator] - eval2[evaluator]
                if diff > 1.0:  # Significant advantage
                    strengths[model1].append(f"Superior {evaluator.replace('_', ' ')}")
                    weaknesses[model2].append(f"Weaker {evaluator.replace('_', ' ')}")
                elif diff < -1.0:
                    strengths[model2].append(f"Superior {evaluator.replace('_', ' ')}")
                    weaknesses[model1].append(f"Weaker {evaluator.replace('_', ' ')}")
        
        return {'strengths': strengths, 'weaknesses': weaknesses}
    
    def _calculate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate dashboard statistics."""
        total_models = len(results)
        total_scenarios = set()
        total_runs = 0
        
        for model_data in results.values():
            runs = model_data.get('runs', [])
            total_runs += len(runs)
            for run in runs:
                scenario_name = run.get('scenario', {}).get('name', '')
                total_scenarios.add(scenario_name)
        
        return {
            'total_models': total_models,
            'total_scenarios': len(total_scenarios),
            'total_runs': total_runs,
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'available_scenarios': list(total_scenarios),
            'available_models': list(results.keys())
        }
    
    def _convert_to_csv(self, results: Dict[str, Any]) -> str:
        """Convert results to CSV format."""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Model', 'Scenario', 'Overall_Score', 'Response_Quality', 
                        'Business_Value', 'Communication_Style', 'Tool_Usage', 'Performance'])
        
        # Write data
        for model, model_data in results.items():
            for run in model_data.get('runs', []):
                scenario = run.get('scenario', {}).get('name', '')
                scores = run.get('evaluator_scores', {})
                writer.writerow([
                    model, scenario, run.get('overall_score', 0),
                    scores.get('response_quality', 0),
                    scores.get('business_value', 0),
                    scores.get('communication_style', 0),
                    scores.get('tool_usage', 0),
                    scores.get('performance', 0)
                ])
        
        return output.getvalue()
    
    def _convert_to_excel(self, results: Dict[str, Any]) -> str:
        """Convert results to Excel format."""
        import pandas as pd
        
        # Prepare data
        data = []
        for model, model_data in results.items():
            for run in model_data.get('runs', []):
                row = {
                    'Model': model,
                    'Scenario': run.get('scenario', {}).get('name', ''),
                    'Overall_Score': run.get('overall_score', 0)
                }
                row.update(run.get('evaluator_scores', {}))
                data.append(row)
        
        df = pd.DataFrame(data)
        excel_file = self.results_dir / f"benchmark_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(excel_file, index=False)
        
        return excel_file.name
    
    def _clear_cache(self):
        """Clear cached results to force refresh."""
        self._cached_results = None
        self._last_update = None
    
    def _start_refresh_thread(self):
        """Start background thread for auto-refresh."""
        def refresh_worker():
            while self.auto_refresh:
                time.sleep(self.refresh_interval)
                self._clear_cache()
                self._load_results()
        
        refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        refresh_thread.start()
    
    def _create_template_files(self):
        """Create advanced HTML template files."""
        template_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'templates'
        template_dir.mkdir(exist_ok=True)
        
        # Advanced dashboard HTML template
        dashboard_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { background-color: #f8f9fa; }
                .chart-container { 
                    background: white; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                    padding: 1.5rem;
                }
                .filter-panel {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }
                .stat-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                }
                .loading { text-align: center; padding: 2rem; }
                .comparison-panel {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="#"><i class="fas fa-chart-line"></i> {{ title }}</a>
                    <div class="navbar-nav ms-auto">
                        <span class="navbar-text">Last Update: {{ timestamp }}</span>
                        <button class="btn btn-outline-light ms-2" onclick="refreshData()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>
            </nav>

            <div class="container-fluid mt-4">
                <!-- Statistics Row -->
                <div class="row" id="stats-row">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h5><i class="fas fa-robot"></i> Models</h5>
                            <h2 id="total-models">-</h2>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h5><i class="fas fa-tasks"></i> Scenarios</h5>
                            <h2 id="total-scenarios">-</h2>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h5><i class="fas fa-play"></i> Total Runs</h5>
                            <h2 id="total-runs">-</h2>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <h5><i class="fas fa-clock"></i> Status</h5>
                            <h6 id="update-status">Live</h6>
                        </div>
                    </div>
                </div>

                <!-- Filters -->
                <div class="row">
                    <div class="col-12">
                        <div class="filter-panel">
                            <h5><i class="fas fa-filter"></i> Filters & Controls</h5>
                            <div class="row">
                                <div class="col-md-3">
                                    <label>Models:</label>
                                    <select id="model-filter" class="form-select" multiple>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label>Scenarios:</label>
                                    <select id="scenario-filter" class="form-select" multiple>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label>Chart Type:</label>
                                    <select id="chart-type" class="form-select">
                                        <option value="radar">Radar Chart</option>
                                        <option value="3d_scatter">3D Scatter</option>
                                        <option value="heatmap">Heatmap</option>
                                        <option value="parallel">Parallel Coords</option>
                                        <option value="sunburst">Sunburst</option>
                                        <option value="timeline">Timeline</option>
                                        <option value="boxplot">Box Plot</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label>Export:</label>
                                    <div class="btn-group w-100">
                                        <button class="btn btn-outline-secondary btn-sm" onclick="exportData('json')">JSON</button>
                                        <button class="btn btn-outline-secondary btn-sm" onclick="exportData('csv')">CSV</button>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <label>&nbsp;</label>
                                    <button class="btn btn-primary w-100" onclick="applyFilters()">Apply Filters</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Model Comparison -->
                <div class="row">
                    <div class="col-12">
                        <div class="comparison-panel">
                            <h5><i class="fas fa-balance-scale"></i> Model Comparison</h5>
                            <div class="row">
                                <div class="col-md-4">
                                    <select id="compare-model1" class="form-select">
                                        <option value="">Select Model 1</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <select id="compare-model2" class="form-select">
                                        <option value="">Select Model 2</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <button class="btn btn-info w-100" onclick="compareModels()">Compare</button>
                                </div>
                            </div>
                            <div id="comparison-results" class="mt-3"></div>
                        </div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="row">
                    <div class="col-12">
                        <div class="chart-container">
                            <h5>Interactive Visualization</h5>
                            <div id="main-chart" class="loading">
                                <i class="fas fa-spinner fa-spin fa-2x"></i>
                                <p>Loading chart...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                let currentFilters = {};
                let statisticsData = {};

                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    loadStatistics();
                    loadChart('radar');
                    setupAutoRefresh();
                });

                function loadStatistics() {
                    fetch('/api/statistics')
                        .then(response => response.json())
                        .then(data => {
                            statisticsData = data;
                            updateStatistics(data);
                            populateFilters(data);
                        })
                        .catch(error => console.error('Error loading statistics:', error));
                }

                function updateStatistics(data) {
                    document.getElementById('total-models').textContent = data.total_models || 0;
                    document.getElementById('total-scenarios').textContent = data.total_scenarios || 0;
                    document.getElementById('total-runs').textContent = data.total_runs || 0;
                    document.getElementById('update-status').textContent = 'Live';
                }

                function populateFilters(data) {
                    const modelFilter = document.getElementById('model-filter');
                    const scenarioFilter = document.getElementById('scenario-filter');
                    const compareModel1 = document.getElementById('compare-model1');
                    const compareModel2 = document.getElementById('compare-model2');

                    // Clear existing options
                    [modelFilter, scenarioFilter, compareModel1, compareModel2].forEach(select => {
                        select.innerHTML = select.id.includes('compare') ? '<option value="">Select Model</option>' : '';
                    });

                    // Populate models
                    (data.available_models || []).forEach(model => {
                        [modelFilter, compareModel1, compareModel2].forEach(select => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            select.appendChild(option);
                        });
                    });

                    // Populate scenarios
                    (data.available_scenarios || []).forEach(scenario => {
                        const option = document.createElement('option');
                        option.value = scenario;
                        option.textContent = scenario;
                        scenarioFilter.appendChild(option);
                    });
                }

                function loadChart(chartType) {
                    const chartDiv = document.getElementById('main-chart');
                    chartDiv.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading chart...</p>';

                    let url = `/api/charts/${chartType}`;
                    
                    // Add filters to URL
                    const params = new URLSearchParams();
                    if (currentFilters.models && currentFilters.models.length > 0) {
                        currentFilters.models.forEach(model => params.append('models', model));
                    }
                    if (currentFilters.scenarios && currentFilters.scenarios.length > 0) {
                        currentFilters.scenarios.forEach(scenario => params.append('scenarios', scenario));
                    }
                    
                    if (params.toString()) {
                        url += '?' + params.toString();
                    }

                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                chartDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
                            } else {
                                const chartData = JSON.parse(data.chart);
                                Plotly.newPlot('main-chart', chartData.data, chartData.layout, {responsive: true});
                            }
                        })
                        .catch(error => {
                            console.error('Error loading chart:', error);
                            chartDiv.innerHTML = '<div class="alert alert-danger">Failed to load chart</div>';
                        });
                }

                function applyFilters() {
                    const modelFilter = document.getElementById('model-filter');
                    const scenarioFilter = document.getElementById('scenario-filter');
                    const chartType = document.getElementById('chart-type').value;

                    currentFilters = {
                        models: Array.from(modelFilter.selectedOptions).map(option => option.value),
                        scenarios: Array.from(scenarioFilter.selectedOptions).map(option => option.value)
                    };

                    loadChart(chartType);
                }

                function compareModels() {
                    const model1 = document.getElementById('compare-model1').value;
                    const model2 = document.getElementById('compare-model2').value;

                    if (!model1 || !model2) {
                        alert('Please select two models to compare');
                        return;
                    }

                    fetch(`/api/comparison?model1=${model1}&model2=${model2}`)
                        .then(response => response.json())
                        .then(data => {
                            displayComparison(data);
                        })
                        .catch(error => console.error('Error comparing models:', error));
                }

                function displayComparison(data) {
                    const resultsDiv = document.getElementById('comparison-results');
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                        return;
                    }

                    let html = `
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6>${data.models[0]} Strengths:</h6>
                                <ul>
                                    ${(data.strengths_weaknesses.strengths[data.models[0]] || []).map(s => `<li class="text-success">${s}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>${data.models[1]} Strengths:</h6>
                                <ul>
                                    ${(data.strengths_weaknesses.strengths[data.models[1]] || []).map(s => `<li class="text-success">${s}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;

                    resultsDiv.innerHTML = html;
                }

                function exportData(format) {
                    window.open(`/api/export/${format}`, '_blank');
                }

                function refreshData() {
                    document.getElementById('update-status').textContent = 'Refreshing...';
                    
                    fetch('/api/refresh')
                        .then(response => response.json())
                        .then(data => {
                            loadStatistics();
                            applyFilters();
                            document.getElementById('update-status').textContent = 'Live';
                        })
                        .catch(error => {
                            console.error('Error refreshing data:', error);
                            document.getElementById('update-status').textContent = 'Error';
                        });
                }

                function setupAutoRefresh() {
                    // Auto-refresh every 30 seconds
                    setInterval(() => {
                        refreshData();
                    }, 30000);
                }

                // Chart type change handler
                document.getElementById('chart-type').addEventListener('change', function() {
                    loadChart(this.value);
                });
            </script>
        </body>
        </html>
        """
        
        with open(template_dir / 'advanced_dashboard.html', 'w') as f:
            f.write(dashboard_html)
    
    def start(self):
        """Start the advanced dashboard server."""
        print(f"Starting bizCon Advanced Dashboard on http://{self.host}:{self.port}")
        print("Features enabled:")
        print("- Interactive Plotly charts")
        print("- Real-time filtering and comparison")
        print("- Auto-refresh" if self.auto_refresh else "- Manual refresh only")
        print("- Data export (JSON, CSV)")
        print("- Advanced model comparison")
        
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)


def launch_advanced_dashboard(results_dir: str, 
                            host: str = '127.0.0.1', 
                            port: int = 5001,
                            auto_refresh: bool = True,
                            refresh_interval: int = 30):
    """
    Launch the advanced benchmark dashboard.
    
    Args:
        results_dir: Directory containing benchmark results
        host: Host to run the dashboard server on
        port: Port to run the dashboard server on
        auto_refresh: Enable automatic data refresh
        refresh_interval: Refresh interval in seconds
    """
    dashboard = AdvancedBenchmarkDashboard(
        results_dir=results_dir,
        host=host,
        port=port,
        auto_refresh=auto_refresh,
        refresh_interval=refresh_interval
    )
    dashboard.start()