# filepath: /Users/ahstanin/GitHub/Olib-AI/bizcon/visualization/dashboard.py
"""
Interactive web dashboard for visualizing benchmark results.
"""
from typing import Dict, List, Any, Optional, Union
import json
import os
import io
import base64
import datetime
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flask import Flask, render_template, send_from_directory, jsonify

from visualization.charts import (
    model_comparison_radar,
    scenario_comparison_heatmap,
    tool_usage_bar_chart,
    performance_trend_line,
    breakdown_stacked_bar,
    success_rate_chart
)


class BenchmarkDashboard:
    """Interactive dashboard for visualizing benchmark results."""
    
    def __init__(self, 
                results_dir: str,
                host: str = '127.0.0.1',
                port: int = 5000):
        """
        Initialize the dashboard.
        
        Args:
            results_dir: Directory containing benchmark results JSON files
            host: Host to run the dashboard server on
            port: Port to run the dashboard server on
        """
        self.results_dir = Path(results_dir)
        self.host = host
        self.port = port
        self.app = self._create_app()
        self._cached_results = None
        self._temp_dir = tempfile.TemporaryDirectory()
        self.static_dir = Path(self._temp_dir.name)
    
    def _create_app(self) -> Flask:
        """Create the Flask application for the dashboard."""
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            """Render the main dashboard page."""
            return render_template('dashboard.html', 
                                  title='bizCon Benchmark Dashboard',
                                  timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        @app.route('/api/results')
        def results():
            """API endpoint for getting all benchmark results."""
            return jsonify(self._load_results())
        
        @app.route('/api/models')
        def models():
            """API endpoint for getting the list of evaluated models."""
            results = self._load_results()
            return jsonify(list(results.keys()))
        
        @app.route('/api/scenarios')
        def scenarios():
            """API endpoint for getting the list of scenarios."""
            results = self._load_results()
            scenarios = set()
            for model_results in results.values():
                for run in model_results.get('runs', []):
                    scenarios.add(run.get('scenario', {}).get('name', ''))
            return jsonify(list(scenarios))
        
        @app.route('/api/charts/<chart_type>')
        def charts(chart_type):
            """API endpoint for generating chart images."""
            results = self._load_results()
            
            # Generate the chart based on type
            if chart_type == 'radar':
                # Prepare data for radar chart
                evaluator_scores = {}
                for model, model_data in results.items():
                    evaluator_scores[model] = {}
                    for evaluator, score in model_data.get('overall', {}).get('evaluator_scores', {}).items():
                        evaluator_scores[model][evaluator] = score
                
                fig = model_comparison_radar(evaluator_scores)
            
            elif chart_type == 'heatmap':
                # Prepare data for heatmap
                scenario_scores = {}
                for model, model_data in results.items():
                    scenario_scores[model] = {}
                    for run in model_data.get('runs', []):
                        scenario_name = run.get('scenario', {}).get('name', '')
                        scenario_scores[model][scenario_name] = run.get('overall_score', 0)
                
                fig = scenario_comparison_heatmap(scenario_scores)
            
            elif chart_type == 'tool_usage':
                # Prepare data for tool usage chart
                tool_metrics = {}
                for model, model_data in results.items():
                    tool_metrics[model] = {}
                    for metric, score in model_data.get('overall', {}).get('tool_usage', {}).items():
                        tool_metrics[model][metric] = score
                
                fig = tool_usage_bar_chart(tool_metrics)
            
            elif chart_type == 'trends':
                # Prepare data for performance trend line
                turn_scores = {}
                for model, model_data in results.items():
                    scores = []
                    for run in model_data.get('runs', []):
                        for turn in run.get('turns', []):
                            scores.append(turn.get('score', 0))
                    if scores:
                        turn_scores[model] = scores
                
                fig = performance_trend_line(turn_scores)
            
            elif chart_type == 'breakdown':
                # Prepare data for breakdown chart
                breakdown = {}
                for model, model_data in results.items():
                    breakdown[model] = {}
                    for category, score in model_data.get('overall', {}).get('category_scores', {}).items():
                        breakdown[model][category] = score
                
                fig = breakdown_stacked_bar(breakdown)
            
            elif chart_type == 'success_rate':
                # Prepare data for success rate chart
                success_rates = {}
                for model, model_data in results.items():
                    success_rates[model] = {}
                    for category, rate in model_data.get('overall', {}).get('success_rates', {}).items():
                        success_rates[model][category] = rate
                
                fig = success_rate_chart(success_rates)
            
            else:
                return jsonify({'error': f'Unknown chart type: {chart_type}'}), 400
            
            # Convert plot to base64 image
            img_data = io.BytesIO()
            fig.savefig(img_data, format='png', bbox_inches='tight')
            img_data.seek(0)
            plt.close(fig)
            
            img_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
            return jsonify({'image': f'data:image/png;base64,{img_base64}'})
        
        @app.route('/static/<path:path>')
        def send_static(path):
            """Serve static files."""
            return send_from_directory(self.static_dir, path)
        
        # Generate template directory with HTML files
        self._create_template_files()
        
        return app
    
    def _load_results(self) -> Dict[str, Any]:
        """Load benchmark results from JSON files."""
        if self._cached_results:
            return self._cached_results
        
        results = {}
        for json_file in self.results_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                model_name = data.get('model_name', json_file.stem)
                results[model_name] = data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        self._cached_results = results
        return results
    
    def _create_template_files(self):
        """Create HTML template files for the dashboard."""
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), exist_ok=True)
        
        # Create dashboard HTML template
        dashboard_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .chart-container {
                    margin-bottom: 2rem;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 1rem;
                    background-color: white;
                }
                body {
                    background-color: #f8f9fa;
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                }
                .chart-img {
                    width: 100%;
                    height: auto;
                }
                h1, h2, h3 {
                    color: #343a40;
                }
                .timestamp {
                    color: #6c757d;
                    font-size: 0.9rem;
                    margin-bottom: 1.5rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row mb-4">
                    <div class="col-12">
                        <h1 class="text-center">bizCon Benchmark Dashboard</h1>
                        <p class="timestamp text-center">Generated on {{ timestamp }}</p>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <div class="chart-container">
                            <h3>Model Performance by Evaluator Category</h3>
                            <img id="radar-chart" class="chart-img" src="" alt="Radar Chart">
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h3>Performance by Scenario</h3>
                            <img id="heatmap-chart" class="chart-img" src="" alt="Heatmap Chart">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h3>Tool Usage Performance</h3>
                            <img id="tool-usage-chart" class="chart-img" src="" alt="Tool Usage Chart">
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h3>Score Breakdown</h3>
                            <img id="breakdown-chart" class="chart-img" src="" alt="Breakdown Chart">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h3>Success Rates</h3>
                            <img id="success-rate-chart" class="chart-img" src="" alt="Success Rate Chart">
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <div class="chart-container">
                            <h3>Performance Across Conversation Turns</h3>
                            <img id="trends-chart" class="chart-img" src="" alt="Trends Chart">
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Load chart images
                window.onload = function() {
                    const chartTypes = ['radar', 'heatmap', 'tool_usage', 'breakdown', 'success_rate', 'trends'];
                    
                    chartTypes.forEach(type => {
                        fetch(`/api/charts/${type}`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.image) {
                                    let chartId = '';
                                    if (type === 'tool_usage') {
                                        chartId = 'tool-usage-chart';
                                    } else {
                                        chartId = `${type}-chart`;
                                    }
                                    document.getElementById(chartId).src = data.image;
                                }
                            })
                            .catch(error => console.error(`Error loading ${type} chart:`, error));
                    });
                };
            </script>
        </body>
        </html>
        """
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'dashboard.html'), 'w') as f:
            f.write(dashboard_html)
    
    def start(self):
        """Start the dashboard server."""
        print(f"Starting bizCon dashboard on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)
    
    def __del__(self):
        """Clean up temporary files."""
        if hasattr(self, '_temp_dir') and self._temp_dir:
            self._temp_dir.cleanup()


def launch_dashboard(results_dir: str, host: str = '127.0.0.1', port: int = 5000):
    """
    Launch the benchmark dashboard.
    
    Args:
        results_dir: Directory containing benchmark results JSON files
        host: Host to run the dashboard server on
        port: Port to run the dashboard server on
    """
    dashboard = BenchmarkDashboard(results_dir, host, port)
    dashboard.start()