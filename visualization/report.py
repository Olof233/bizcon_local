# filepath: /Users/ahstanin/GitHub/Olib-AI/bizcon/visualization/report.py
"""
Report generation functions for benchmark results.
"""
from typing import Dict, List, Any, Optional, Union
import json
import os
import io
import datetime
import base64
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import jinja2
import pdfkit
import markdown

from .charts import (
    model_comparison_radar,
    scenario_comparison_heatmap,
    tool_usage_bar_chart,
    performance_trend_line,
    breakdown_stacked_bar,
    success_rate_chart
)


class BenchmarkReport:
    """Generator for benchmark reports in HTML and PDF formats."""
    
    def __init__(self, results: Dict[str, Any], output_dir: str = None): #type: ignore
        """
        Initialize the report generator.
        
        Args:
            results: Dictionary of benchmark results
            output_dir: Directory to save generated reports
        """
        self.results = results
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / 'reports'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up Jinja2 environment
        self.template_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'templates'
        self.template_dir.mkdir(exist_ok=True)
        
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Create template files if they don't exist
        self._create_template_files()
    
    def _create_template_files(self):
        """Create HTML template files for reports."""
        # Create report HTML template
        report_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1, h2, h3, h4 {
                    color: #2c3e50;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                th, td {
                    text-align: left;
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .chart-container {
                    margin: 30px 0;
                    text-align: center;
                }
                .chart-image {
                    max-width: 100%;
                    height: auto;
                }
                .section {
                    margin-bottom: 40px;
                }
                .metadata {
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-bottom: 30px;
                }
                .summary-box {
                    background-color: #f8f9fa;
                    border-left: 4px solid #2c3e50;
                    padding: 15px;
                    margin-bottom: 20px;
                }
                .model-comparison {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .model-card {
                    flex: 1;
                    min-width: 300px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                }
                .score {
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .good-score {
                    color: #27ae60;
                }
                .medium-score {
                    color: #f39c12;
                }
                .poor-score {
                    color: #c0392b;
                }
                .footer {
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 0.8em;
                    color: #7f8c8d;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h1>{{ title }}</h1>
            
            <div class="metadata">
                <p>Generated on: {{ timestamp }}</p>
                <p>Models evaluated: {{ models|join(', ') }}</p>
                <p>Scenarios tested: {{ scenarios|join(', ') }}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="summary-box">
                    <p>{{ summary }}</p>
                    
                    {% if top_model %}
                    <p>Top performing model: <strong>{{ top_model }}</strong> with an overall score of <span class="score good-score">{{ top_model_score }}</span>/10</p>
                    {% endif %}
                    
                    {% if key_findings %}
                    <h3>Key Findings</h3>
                    <ul>
                        {% for finding in key_findings %}
                        <li>{{ finding }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
            </div>
            
            <div class="section">
                <h2>Overall Performance Comparison</h2>
                
                <div class="chart-container">
                    <h3>Model Performance by Evaluator Category</h3>
                    <img class="chart-image" src="{{ charts.radar }}" alt="Radar chart of model performance">
                </div>
                
                <div class="model-comparison">
                    {% for model in models %}
                    <div class="model-card">
                        <h3>{{ model }}</h3>
                        <p>Overall score: <span class="score {{ score_class(scores[model].overall) }}">{{ scores[model].overall }}</span>/10</p>
                        
                        <h4>Breakdown:</h4>
                        <ul>
                            {% for category, score in scores[model].categories.items() %}
                            <li>{{ category|replace('_', ' ')|title }}: <span class="score {{ score_class(score) }}">{{ score }}</span>/10</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="section">
                <h2>Performance by Scenario</h2>
                
                <div class="chart-container">
                    <img class="chart-image" src="{{ charts.heatmap }}" alt="Heatmap of scenario performance">
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            {% for model in models %}
                            <th>{{ model }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for scenario in scenarios %}
                        <tr>
                            <td>{{ scenario|replace('_', ' ')|title }}</td>
                            {% for model in models %}
                            <td class="{{ score_class(scenario_scores[model][scenario]) }}">{{ scenario_scores[model][scenario] }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>Tool Usage Analysis</h2>
                
                <div class="chart-container">
                    <img class="chart-image" src="{{ charts.tool_usage }}" alt="Tool usage performance">
                </div>
                
                <h3>Key Observations</h3>
                <ul>
                    {% for observation in tool_observations %}
                    <li>{{ observation }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <h2>Detailed Analysis</h2>
                
                <div class="chart-container">
                    <h3>Score Breakdown by Category</h3>
                    <img class="chart-image" src="{{ charts.breakdown }}" alt="Score breakdown">
                </div>
                
                <div class="chart-container">
                    <h3>Performance Trends Across Conversation</h3>
                    <img class="chart-image" src="{{ charts.trends }}" alt="Performance trends">
                </div>
                
                <div class="chart-container">
                    <h3>Success Rates by Category</h3>
                    <img class="chart-image" src="{{ charts.success_rate }}" alt="Success rates">
                </div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="footer">
                <p>Generated with bizCon Benchmark Framework</p>
                <p>© {{ current_year }} - All rights reserved</p>
            </div>
        </body>
        </html>
        """
        
        with open(self.template_dir / 'report.html', 'w', encoding='utf-8') as f:
            f.write(report_html)
    
    def _generate_charts(self) -> Dict[str, str]:
        """
        Generate charts and convert them to base64 for embedding in reports.
        
        Returns:
            Dictionary mapping chart names to base64-encoded images
        """
        charts = {}
        
        # Prepare data for radar chart
        evaluator_scores = {}
        for model, model_data in self.results.items():
            evaluator_scores[model] = {}
            for evaluator, score in model_data.get('overall', {}).get('evaluator_scores', {}).items():
                evaluator_scores[model][evaluator] = score
        
        # Generate radar chart
        fig = model_comparison_radar(evaluator_scores)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['radar'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Prepare data for heatmap
        scenario_scores = {}
        for model, model_data in self.results.items():
            scenario_scores[model] = {}
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                scenario_scores[model][scenario_name] = run.get('overall_score', 0)
        
        # Generate heatmap
        fig = scenario_comparison_heatmap(scenario_scores)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['heatmap'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Prepare data for tool usage chart
        tool_metrics = {}
        for model, model_data in self.results.items():
            tool_metrics[model] = {}
            for metric, score in model_data.get('overall', {}).get('tool_usage', {}).items():
                tool_metrics[model][metric] = score
        
        # Generate tool usage chart
        fig = tool_usage_bar_chart(tool_metrics)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['tool_usage'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Prepare data for breakdown chart
        breakdown = {}
        for model, model_data in self.results.items():
            breakdown[model] = {}
            for category, score in model_data.get('overall', {}).get('category_scores', {}).items():
                breakdown[model][category] = score
        
        # Generate breakdown chart
        fig = breakdown_stacked_bar(breakdown)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['breakdown'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Prepare data for success rate chart
        success_rates = {}
        for model, model_data in self.results.items():
            success_rates[model] = {}
            for category, rate in model_data.get('overall', {}).get('success_rates', {}).items():
                success_rates[model][category] = rate
        
        # Generate success rate chart
        fig = success_rate_chart(success_rates)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['success_rate'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Prepare data for performance trend line
        turn_scores = {}
        for model, model_data in self.results.items():
            scores = []
            for run in model_data.get('runs', []):
                for turn in run.get('turns', []):
                    scores.append(turn.get('score', 0))
            if scores:
                turn_scores[model] = scores
        
        # Generate performance trend line
        fig = performance_trend_line(turn_scores)
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
        img_data.seek(0)
        plt.close(fig)
        charts['trends'] = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Convert to data URLs
        for chart_name, img_base64 in charts.items():
            charts[chart_name] = f'data:image/png;base64,{img_base64}'
        
        return charts
    
    def _prepare_template_data(self) -> Dict[str, Any]:
        """
        Prepare data for the report template.
        
        Returns:
            Dictionary of template variables
        """
        # Get basic metadata
        models = list(self.results.keys())
        
        # Get list of scenarios
        scenarios = set()
        for model_data in self.results.values():
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                if scenario_name:
                    scenarios.add(scenario_name)
        scenarios = list(scenarios)
        
        # Get scores for each model
        scores = {}
        for model, model_data in self.results.items():
            overall_score = model_data.get('overall', {}).get('score', 0)
            category_scores = model_data.get('overall', {}).get('category_scores', {})
            scores[model] = {
                'overall': overall_score,
                'categories': category_scores
            }
        
        # Find top model
        top_model = None
        top_model_score = 0
        for model, model_scores in scores.items():
            if model_scores['overall'] > top_model_score:
                top_model = model
                top_model_score = model_scores['overall']
        
        # Get scenario scores
        scenario_scores = {}
        for model, model_data in self.results.items():
            scenario_scores[model] = {}
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                if scenario_name:
                    scenario_scores[model][scenario_name] = run.get('overall_score', 0)
        
        # Generate charts
        charts = self._generate_charts()
        
        # Generate summary and recommendations based on results
        summary = self._generate_summary(models, scores, scenario_scores)
        key_findings = self._generate_key_findings(models, scores, scenario_scores)
        recommendations = self._generate_recommendations(models, scores, scenario_scores)
        tool_observations = self._generate_tool_observations(models, self.results)
        
        # Return template data
        return {
            'title': 'bizCon Benchmark Report',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_year': datetime.datetime.now().year,
            'models': models,
            'scenarios': scenarios,
            'scores': scores,
            'top_model': top_model,
            'top_model_score': f"{top_model_score:.1f}",
            'scenario_scores': scenario_scores,
            'charts': charts,
            'summary': summary,
            'key_findings': key_findings,
            'recommendations': recommendations,
            'tool_observations': tool_observations,
            'score_class': lambda score: 'good-score' if score >= 7 else 'medium-score' if score >= 4 else 'poor-score'
        }
    
    def _generate_summary(self, 
                         models: List[str], 
                         scores: Dict[str, Dict[str, float]], 
                         scenario_scores: Dict[str, Dict[str, float]]) -> str:
        """Generate summary text based on benchmark results."""
        n_models = len(models)
        avg_overall = sum(s['overall'] for s in scores.values()) / n_models if n_models > 0 else 0
        
        summary = f"This report presents a comprehensive evaluation of {n_models} language models on business conversation tasks. "
        
        if n_models > 1:
            model_performances = [(model, scores[model]['overall']) for model in models]
            model_performances.sort(key=lambda x: x[1], reverse=True)
            best_model, best_score = model_performances[0]
            worst_model, worst_score = model_performances[-1]
            
            if best_score - worst_score > 3:
                summary += f"There is significant variation in model performance, with {best_model} ({best_score:.1f}/10) substantially outperforming {worst_model} ({worst_score:.1f}/10). "
            elif best_score - worst_score > 1:
                summary += f"There are notable differences between models, with {best_model} ({best_score:.1f}/10) outperforming {worst_model} ({worst_score:.1f}/10). "
            else:
                summary += f"All models performed similarly, with overall scores ranging from {worst_score:.1f} to {best_score:.1f}. "
        
        # Comment on overall performance
        if avg_overall >= 8:
            summary += "Overall, the models demonstrated excellent performance on business conversation tasks. "
        elif avg_overall >= 6:
            summary += "Overall, the models demonstrated good performance on business conversation tasks. "
        elif avg_overall >= 4:
            summary += "Overall, the models demonstrated adequate performance on business conversation tasks. "
        else:
            summary += "Overall, the models demonstrated poor performance on business conversation tasks. "
        
        return summary
    
    def _generate_key_findings(self, 
                              models: List[str], 
                              scores: Dict[str, Dict[str, float]], 
                              scenario_scores: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate key findings based on benchmark results."""
        findings = []
        
        # Finding 1: Best and worst scenarios
        all_scenario_scores = []
        for model, scenarios in scenario_scores.items():
            for scenario, score in scenarios.items():
                all_scenario_scores.append((model, scenario, score))
        
        if all_scenario_scores:
            # Best scenario types
            scenario_avg_scores = {}
            for _, scenario, score in all_scenario_scores:
                if scenario not in scenario_avg_scores:
                    scenario_avg_scores[scenario] = []
                scenario_avg_scores[scenario].append(score)
            
            for scenario, scores_list in scenario_avg_scores.items():
                scenario_avg_scores[scenario] = sum(scores_list) / len(scores_list)
            
            best_scenarios = sorted(scenario_avg_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            worst_scenarios = sorted(scenario_avg_scores.items(), key=lambda x: x[1])[:2]
            
            findings.append(f"Models performed best on {best_scenarios[0][0].replace('_', ' ').title()} scenarios " +
                           f"(avg. score: {best_scenarios[0][1]:.1f}/10)" +
                           (f" and {best_scenarios[1][0].replace('_', ' ').title()} scenarios " +
                           f"(avg. score: {best_scenarios[1][1]:.1f}/10)" if len(best_scenarios) > 1 else ""))
            
            findings.append(f"Models struggled most with {worst_scenarios[0][0].replace('_', ' ').title()} scenarios " +
                           f"(avg. score: {worst_scenarios[0][1]:.1f}/10)" +
                           (f" and {worst_scenarios[1][0].replace('_', ' ').title()} scenarios " +
                           f"(avg. score: {worst_scenarios[1][1]:.1f}/10)" if len(worst_scenarios) > 1 else ""))
        
        # Finding 2: Best and worst evaluator categories
        if models and all(scores[model].get('categories') for model in models):
            category_scores = {}
            for model in models: 
                for category, score in scores[model]['categories'].items(): #type: ignore
                    if category not in category_scores:
                        category_scores[category] = []
                    category_scores[category].append(score)
            
            for category, scores_list in category_scores.items():
                category_scores[category] = sum(scores_list) / len(scores_list)
            
            best_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            worst_categories = sorted(category_scores.items(), key=lambda x: x[1])[:2]
            
            findings.append(f"Models scored highest in {best_categories[0][0].replace('_', ' ').title()} " +
                           f"(avg. score: {best_categories[0][1]:.1f}/10)" +
                           (f" and {best_categories[1][0].replace('_', ' ').title()} " +
                           f"(avg. score: {best_categories[1][1]:.1f}/10)" if len(best_categories) > 1 else ""))
            
            findings.append(f"Models scored lowest in {worst_categories[0][0].replace('_', ' ').title()} " +
                           f"(avg. score: {worst_categories[0][1]:.1f}/10)" +
                           (f" and {worst_categories[1][0].replace('_', ' ').title()} " +
                           f"(avg. score: {worst_categories[1][1]:.1f}/10)" if len(worst_categories) > 1 else ""))
        
        return findings
    
    def _generate_recommendations(self, 
                                models: List[str], 
                                scores: Dict[str, Dict[str, float]], 
                                scenario_scores: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate recommendations based on benchmark results."""
        recommendations = []
        
        # Get average scores by category
        category_scores = {}
        for model in models:
            model_categories = scores[model].get('categories', {})
            for category, score in model_categories.items(): #type: ignore
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
        
        category_avgs = {}
        for category, cat_scores in category_scores.items():
            category_avgs[category] = sum(cat_scores) / len(cat_scores) if cat_scores else 0
        
        # Add category-specific recommendations
        for category, avg_score in category_avgs.items():
            if category == 'tool_usage' and avg_score < 7:
                recommendations.append(
                    "Improve tool usage capabilities of models by enhancing parameter validation, "
                    "optimizing tool selection logic, and improving the interpretation of tool outputs."
                )
            elif category == 'business_value' and avg_score < 7:
                recommendations.append(
                    "Enhance business value delivery by fine-tuning models on domain-specific content "
                    "and incorporating more business context into model responses."
                )
            elif category == 'response_quality' and avg_score < 7:
                recommendations.append(
                    "Improve response quality by focusing on factual accuracy and implementing better "
                    "fact-checking mechanisms during response generation."
                )
            elif category == 'communication_style' and avg_score < 7:
                recommendations.append(
                    "Enhance communication style by training models to maintain consistent tone, "
                    "appropriate formality, and clear structure in business conversations."
                )
        
        # Add general recommendations
        if len(models) > 1:
            top_model = max(models, key=lambda m: scores[m]['overall'])
            recommendations.append(
                f"Consider using {top_model} for critical business scenarios where overall "
                f"performance is essential, as it demonstrated the highest overall scores."
            )
        
        # Add scenario-specific recommendations
        all_scenario_scores = []
        for model, scenarios in scenario_scores.items():
            for scenario, score in scenarios.items():
                all_scenario_scores.append((model, scenario, score))
        
        if all_scenario_scores:
            scenario_avg_scores = {}
            for _, scenario, score in all_scenario_scores:
                if scenario not in scenario_avg_scores:
                    scenario_avg_scores[scenario] = []
                scenario_avg_scores[scenario].append(score)
            
            for scenario, score_list in scenario_avg_scores.items():
                avg_score = sum(score_list) / len(score_list)
                if avg_score < 5:
                    recommendations.append(
                        f"Develop specialized training data for {scenario.replace('_', ' ').title()} scenarios, "
                        f"which showed lower performance across all models (avg. score: {avg_score:.1f}/10)."
                    )
        
        # Add a recommendation about benchmarking
        recommendations.append(
            "Continue regular benchmarking with bizCon to track progress and identify areas for improvement "
            "as models and business requirements evolve."
        )
        
        return recommendations
    
    def _generate_tool_observations(self, 
                                  models: List[str], 
                                  results: Dict[str, Any]) -> List[str]:
        """Generate observations about tool usage based on benchmark results."""
        observations = []
        
        # Extract tool usage metrics
        tool_metrics = {}
        for model, model_data in results.items():
            tool_metrics[model] = model_data.get('overall', {}).get('tool_usage', {})
        
        if not tool_metrics or not any(tool_metrics.values()):
            return ["No tool usage data available for analysis."]
        
        # Calculate averages for each metric across models
        metric_avgs = {}
        for model, metrics in tool_metrics.items():
            for metric, value in metrics.items():
                if metric not in metric_avgs:
                    metric_avgs[metric] = []
                metric_avgs[metric].append(value)
        
        for metric, values in metric_avgs.items():
            metric_avgs[metric] = sum(values) / len(values) if values else 0
        
        # Generate observations based on the metrics
        if 'tool_selection' in metric_avgs:
            avg_selection = metric_avgs['tool_selection']
            if avg_selection >= 7:
                observations.append(f"Models demonstrated good tool selection capabilities (avg. score: {avg_selection:.1f}/10).")
            else:
                observations.append(f"Models struggled with selecting appropriate tools (avg. score: {avg_selection:.1f}/10).")
        
        if 'parameter_quality' in metric_avgs:
            avg_params = metric_avgs['parameter_quality']
            if avg_params >= 7:
                observations.append(f"Models provided high-quality parameters when calling tools (avg. score: {avg_params:.1f}/10).")
            else:
                observations.append(f"Models had difficulty constructing appropriate parameters for tools (avg. score: {avg_params:.1f}/10).")
        
        if 'call_efficiency' in metric_avgs:
            avg_efficiency = metric_avgs['call_efficiency']
            if avg_efficiency >= 7:
                observations.append(f"Models were efficient in their tool usage patterns (avg. score: {avg_efficiency:.1f}/10).")
            else:
                observations.append(f"Models made redundant or unnecessary tool calls (avg. score: {avg_efficiency:.1f}/10).")
        
        if 'result_interpretation' in metric_avgs:
            avg_interpretation = metric_avgs['result_interpretation']
            if avg_interpretation >= 7:
                observations.append(f"Models effectively incorporated tool results into responses (avg. score: {avg_interpretation:.1f}/10).")
            else:
                observations.append(f"Models struggled to properly interpret and incorporate tool results (avg. score: {avg_interpretation:.1f}/10).")
        
        # Compare models if there are multiple
        if len(models) > 1:
            best_model = None
            best_score = 0
            for model, metrics in tool_metrics.items():
                tool_avg = sum(metrics.values()) / len(metrics) if metrics else 0
                if tool_avg > best_score:
                    best_score = tool_avg
                    best_model = model
            
            if best_model:
                observations.append(f"{best_model} demonstrated the best overall tool usage capabilities (avg. score: {best_score:.1f}/10).")
        
        return observations
    
    def generate_html(self, filename: str = "benchmark_report.html") -> str:
        """
        Generate an HTML report from benchmark results.
        
        Args:
            filename: Name of the HTML file to generate
            
        Returns:
            Path to the generated HTML file
        """
        # Prepare template data
        template_data = self._prepare_template_data()
        
        # Render HTML template
        template = self.jinja_env.get_template('report.html')
        html_content = template.render(**template_data)
        
        # Save HTML to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def generate_pdf(self, filename: str = "benchmark_report.pdf") -> str:
        """
        Generate a PDF report from benchmark results.
        
        Args:
            filename: Name of the PDF file to generate
            
        Returns:
            Path to the generated PDF file
        """
        # First generate HTML
        html_path = self.generate_html("temp_report.html")
        
        # Convert HTML to PDF
        output_path = self.output_dir / filename
        try:
            pdfkit.from_file(html_path, str(output_path))
        except Exception as e:
            print(f"Error generating PDF: {e}")
            print("Falling back to HTML report only.")
            return html_path
        
        # Remove temporary HTML file
        os.remove(html_path)
        
        return str(output_path)
    
    def generate_markdown(self, filename: str = "benchmark_report.md") -> str:
        """
        Generate a Markdown report from benchmark results.
        
        Args:
            filename: Name of the Markdown file to generate
            
        Returns:
            Path to the generated Markdown file
        """
        # Prepare template data
        data = self._prepare_template_data()
        
        # Create markdown content
        md_content = f"# {data['title']}\n\n"
        md_content += f"Generated on: {data['timestamp']}  \n"
        md_content += f"Models evaluated: {', '.join(data['models'])}  \n"
        md_content += f"Scenarios tested: {', '.join(data['scenarios'])}  \n\n"
        
        md_content += "## Executive Summary\n\n"
        md_content += f"{data['summary']}\n\n"
        
        if data['top_model']:
            md_content += f"Top performing model: **{data['top_model']}** with an overall score of **{data['top_model_score']}/10**\n\n"
        
        if data['key_findings']:
            md_content += "### Key Findings\n\n"
            for finding in data['key_findings']:
                md_content += f"- {finding}\n"
            md_content += "\n"
        
        md_content += "## Overall Performance Comparison\n\n"
        
        md_content += "### Model Performance Breakdown\n\n"
        md_content += "| Model | Overall Score | " + " | ".join([cat.replace('_', ' ').title() for cat in data['scores'][data['models'][0]]['categories'].keys()]) + " |\n"
        md_content += "| --- | --- | " + " | ".join(["---" for _ in data['scores'][data['models'][0]]['categories']]) + " |\n"
        
        for model in data['models']:
            row = f"| {model} | {data['scores'][model]['overall']:.1f} | "
            row += " | ".join([f"{score:.1f}" for score in data['scores'][model]['categories'].values()])
            row += " |\n"
            md_content += row
        
        md_content += "\n## Performance by Scenario\n\n"
        md_content += "| Scenario | " + " | ".join(data['models']) + " |\n"
        md_content += "| --- | " + " | ".join(["---" for _ in data['models']]) + " |\n"
        
        for scenario in data['scenarios']:
            row = f"| {scenario.replace('_', ' ').title()} | "
            row += " | ".join([f"{data['scenario_scores'][model].get(scenario, 0):.1f}" for model in data['models']])
            row += " |\n"
            md_content += row
        
        md_content += "\n## Tool Usage Analysis\n\n"
        md_content += "### Key Observations\n\n"
        for observation in data['tool_observations']:
            md_content += f"- {observation}\n"
        md_content += "\n"
        
        md_content += "## Recommendations\n\n"
        for recommendation in data['recommendations']:
            md_content += f"- {recommendation}\n"
        md_content += "\n"
        
        md_content += "---\n\n"
        md_content += f"Generated with bizCon Benchmark Framework | © {data['current_year']} - All rights reserved"
        
        # Save markdown to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(output_path)


def generate_report(results_file: str, output_dir: str = None, format: str = 'html') -> str: #type: ignore
    """
    Generate a benchmark report in the specified format.
    
    Args:
        results_file: Path to JSON file with benchmark results
        output_dir: Directory to save the report
        format: Report format ('html', 'pdf', or 'markdown')
        
    Returns:
        Path to the generated report file
    """
    # Load results from file
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Create report generator
    report = BenchmarkReport(results, output_dir)
    
    # Generate report in the specified format
    if format.lower() == 'pdf':
        return report.generate_pdf()
    elif format.lower() == 'markdown':
        return report.generate_markdown()
    else:
        return report.generate_html()