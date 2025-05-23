"""
Interactive charts using Plotly for advanced visualization dashboard.
"""
from typing import Dict, List, Any, Optional, Union
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class InteractiveCharts:
    """Generator for interactive Plotly charts."""
    
    def __init__(self, theme: str = "plotly_white"):
        """Initialize the interactive chart generator."""
        self.theme = theme
        self.color_palette = px.colors.qualitative.Set3
    
    def model_comparison_3d_scatter(
        self,
        results: Dict[str, Dict[str, float]],
        dimensions: List[str] = None
    ) -> go.Figure:
        """
        Create a 3D scatter plot comparing models across multiple dimensions.
        
        Args:
            results: Dictionary mapping model names to evaluation scores
            dimensions: List of 3 dimensions to plot (default: first 3)
            
        Returns:
            Plotly figure object
        """
        if not dimensions:
            dimensions = list(list(results.values())[0].keys())[:3]
        
        fig = go.Figure()
        
        for i, (model, scores) in enumerate(results.items()):
            fig.add_trace(go.Scatter3d(
                x=[scores.get(dimensions[0], 0)],
                y=[scores.get(dimensions[1], 0)],
                z=[scores.get(dimensions[2], 0)],
                mode='markers+text',
                name=model,
                text=[model],
                textposition="top center",
                marker=dict(
                    size=12,
                    color=self.color_palette[i % len(self.color_palette)],
                    symbol='circle',
                    line=dict(color='DarkSlateGrey', width=2)
                )
            ))
        
        fig.update_layout(
            title="3D Model Performance Comparison",
            scene=dict(
                xaxis_title=dimensions[0].replace('_', ' ').title(),
                yaxis_title=dimensions[1].replace('_', ' ').title(),
                zaxis_title=dimensions[2].replace('_', ' ').title(),
                xaxis=dict(range=[0, 10]),
                yaxis=dict(range=[0, 10]),
                zaxis=dict(range=[0, 10])
            ),
            template=self.theme,
            height=700
        )
        
        return fig
    
    def interactive_radar_chart(
        self,
        results: Dict[str, Dict[str, float]]
    ) -> go.Figure:
        """
        Create an interactive radar chart with hover details.
        
        Args:
            results: Dictionary mapping model names to evaluation scores
            
        Returns:
            Plotly figure object
        """
        categories = list(list(results.values())[0].keys())
        
        fig = go.Figure()
        
        for i, (model, scores) in enumerate(results.items()):
            values = [scores[cat] for cat in categories]
            values += values[:1]  # Close the polygon
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=model,
                line_color=self.color_palette[i % len(self.color_palette)],
                hovertemplate='%{theta}: %{r:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=True,
            title="Interactive Model Performance Radar",
            template=self.theme,
            height=600
        )
        
        return fig
    
    def animated_performance_timeline(
        self,
        turn_scores: Dict[str, List[Dict[str, Any]]],
        metric: str = "overall_score"
    ) -> go.Figure:
        """
        Create an animated timeline showing performance changes.
        
        Args:
            turn_scores: Dictionary mapping models to turn-by-turn scores
            metric: The metric to visualize
            
        Returns:
            Plotly figure object
        """
        # Prepare data for animation
        all_data = []
        for model, turns in turn_scores.items():
            for i, turn in enumerate(turns):
                all_data.append({
                    'Model': model,
                    'Turn': i + 1,
                    'Score': turn.get(metric, 0),
                    'Details': turn.get('details', '')
                })
        
        df = pd.DataFrame(all_data)
        
        # Create animated scatter plot
        fig = px.scatter(
            df,
            x="Turn",
            y="Score",
            color="Model",
            animation_frame="Turn",
            animation_group="Model",
            size="Score",
            hover_data=["Details"],
            range_y=[0, 10],
            title=f"Performance Timeline: {metric.replace('_', ' ').title()}",
            template=self.theme
        )
        
        fig.update_traces(marker=dict(size=12))
        fig.update_layout(height=600)
        
        return fig
    
    def interactive_heatmap_with_dendogram(
        self,
        results: Dict[str, Dict[str, float]]
    ) -> go.Figure:
        """
        Create an interactive heatmap with hierarchical clustering.
        
        Args:
            results: Dictionary mapping models to scenario scores
            
        Returns:
            Plotly figure object
        """
        import scipy.cluster.hierarchy as sch
        from scipy.spatial.distance import pdist, squareform
        
        # Convert to matrix
        models = list(results.keys())
        scenarios = list(list(results.values())[0].keys())
        
        matrix = np.array([[results[model][scenario] for scenario in scenarios] 
                          for model in models])
        
        # Perform hierarchical clustering
        distances = pdist(matrix, metric='euclidean')
        linkage = sch.linkage(distances, method='ward')
        dendogram = sch.dendrogram(linkage, no_plot=True)
        
        # Reorder based on clustering
        order = dendogram['leaves']
        matrix_ordered = matrix[order]
        models_ordered = [models[i] for i in order]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix_ordered,
            x=scenarios,
            y=models_ordered,
            colorscale='Viridis',
            hovertemplate='Model: %{y}<br>Scenario: %{x}<br>Score: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Clustered Performance Heatmap",
            xaxis_title="Scenarios",
            yaxis_title="Models",
            template=self.theme,
            height=600
        )
        
        return fig
    
    def sunburst_performance_breakdown(
        self,
        results: Dict[str, Dict[str, Any]]
    ) -> go.Figure:
        """
        Create a sunburst chart showing hierarchical performance breakdown.
        
        Args:
            results: Nested dictionary of performance metrics
            
        Returns:
            Plotly figure object
        """
        # Prepare data for sunburst
        labels = []
        parents = []
        values = []
        colors = []
        
        # Root
        labels.append("Overall")
        parents.append("")
        values.append(100)
        colors.append("#636EFA")
        
        # Add models
        for i, (model, metrics) in enumerate(results.items()):
            labels.append(model)
            parents.append("Overall")
            model_avg = np.mean(list(metrics.values()))
            values.append(model_avg * 10)  # Scale to percentage
            colors.append(self.color_palette[i % len(self.color_palette)])
            
            # Add metrics for each model
            for metric, score in metrics.items():
                labels.append(f"{model} - {metric}")
                parents.append(model)
                values.append(score)
                colors.append(self.color_palette[i % len(self.color_palette)])
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>Score: %{value:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Performance Breakdown Sunburst",
            template=self.theme,
            height=700
        )
        
        return fig
    
    def parallel_coordinates_comparison(
        self,
        results: Dict[str, Dict[str, float]]
    ) -> go.Figure:
        """
        Create a parallel coordinates plot for multi-dimensional comparison.
        
        Args:
            results: Dictionary mapping models to evaluation scores
            
        Returns:
            Plotly figure object
        """
        # Prepare data
        data = []
        for model, scores in results.items():
            row = {'Model': model}
            row.update(scores)
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Create dimensions for parallel coordinates
        dimensions = []
        for col in df.columns[1:]:  # Skip 'Model' column
            dimensions.append(
                dict(
                    range=[0, 10],
                    label=col.replace('_', ' ').title(),
                    values=df[col]
                )
            )
        
        # Create color scale based on overall performance
        overall_scores = df.iloc[:, 1:].mean(axis=1)
        
        fig = go.Figure(data=
            go.Parcoords(
                line=dict(
                    color=overall_scores,
                    colorscale='Viridis',
                    showscale=True,
                    cmin=0,
                    cmax=10,
                    colorbar=dict(title="Avg Score")
                ),
                dimensions=dimensions,
                labelfont=dict(size=12),
                tickfont=dict(size=10)
            )
        )
        
        fig.update_layout(
            title="Parallel Coordinates: Multi-dimensional Model Comparison",
            template=self.theme,
            height=600
        )
        
        return fig
    
    def interactive_box_plots(
        self,
        scenario_results: Dict[str, List[Dict[str, float]]]
    ) -> go.Figure:
        """
        Create interactive box plots showing score distributions.
        
        Args:
            scenario_results: Dictionary mapping scenarios to score lists
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        for i, (scenario, scores) in enumerate(scenario_results.items()):
            # Extract scores for different models
            model_scores = {}
            for score_dict in scores:
                for model, score in score_dict.items():
                    if model not in model_scores:
                        model_scores[model] = []
                    model_scores[model].append(score)
            
            # Add box plot for each model in this scenario
            for j, (model, model_score_list) in enumerate(model_scores.items()):
                fig.add_trace(go.Box(
                    y=model_score_list,
                    name=f"{scenario} - {model}",
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8,
                    marker_color=self.color_palette[(i + j) % len(self.color_palette)]
                ))
        
        fig.update_layout(
            title="Score Distribution by Scenario and Model",
            yaxis_title="Score",
            showlegend=True,
            template=self.theme,
            height=600
        )
        
        return fig
    
    def create_comparison_dashboard(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, go.Figure]:
        """
        Create a complete set of interactive charts for the dashboard.
        
        Args:
            results: Complete benchmark results
            
        Returns:
            Dictionary of chart names to Plotly figures
        """
        charts = {}
        
        # Extract different data views
        evaluator_scores = {}
        scenario_scores = {}
        
        for model, model_data in results.items():
            if 'evaluator_scores' in model_data.get('overall', {}):
                evaluator_scores[model] = model_data['overall']['evaluator_scores']
            
            if 'scenario_scores' in model_data.get('overall', {}):
                scenario_scores[model] = model_data['overall']['scenario_scores']
        
        # Generate all chart types
        if evaluator_scores:
            charts['radar'] = self.interactive_radar_chart(evaluator_scores)
            charts['3d_scatter'] = self.model_comparison_3d_scatter(evaluator_scores)
            charts['parallel'] = self.parallel_coordinates_comparison(evaluator_scores)
            charts['sunburst'] = self.sunburst_performance_breakdown(evaluator_scores)
        
        if scenario_scores:
            charts['heatmap'] = self.interactive_heatmap_with_dendogram(scenario_scores)
        
        return charts