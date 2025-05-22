# filepath: /Users/ahstanin/GitHub/Olib-AI/bizcon/visualization/charts.py
"""
Visualization functions for benchmark results.
"""
from typing import Dict, List, Any, Optional, Union
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
import seaborn as sns


def set_plotting_style():
    """Set consistent styling for all plots."""
    # Set the style
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        try:
            plt.style.use('seaborn-whitegrid')
        except:
            plt.style.use('default')
    
    # Set fonts
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif'],
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 18
    })
    
    # Set color palette
    sns.set_palette('viridis')


def model_comparison_radar(
    results: Dict[str, Dict[str, float]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a radar chart comparing model performance across evaluator dimensions.
    
    Args:
        results: Dictionary mapping model names to dictionaries of evaluator scores
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    # Extract evaluator categories and model names
    evaluator_categories = list(list(results.values())[0].keys())
    model_names = list(results.keys())
    
    # Set up the radar chart
    angles = np.linspace(0, 2*np.pi, len(evaluator_categories), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    
    # Add evaluator labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in evaluator_categories])
    
    # Set y-ticks (score range)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_ylim(0, 10)
    
    # Plot each model
    for i, model_name in enumerate(model_names):
        values = [results[model_name][cat] for cat in evaluator_categories]
        values += values[:1]  # Close the loop
        
        ax.plot(angles, values, linewidth=2, linestyle='solid', 
                label=model_name, alpha=0.8)
        ax.fill(angles, values, alpha=0.1)
    
    # Add legend and title
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Model Performance Comparison by Evaluator Category', size=18, pad=20)
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig


def scenario_comparison_heatmap(
    results: Dict[str, Dict[str, float]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a heatmap comparing model performance across scenarios.
    
    Args:
        results: Dictionary mapping model names to dictionaries of scenario scores
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    # Convert results to a matrix
    model_names = list(results.keys())
    scenario_names = list(list(results.values())[0].keys())
    
    score_matrix = np.zeros((len(model_names), len(scenario_names)))
    for i, model in enumerate(model_names):
        for j, scenario in enumerate(scenario_names):
            score_matrix[i, j] = results[model][scenario]
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(max(10, len(scenario_names)), max(8, len(model_names) * 0.6)))
    
    # Plot heatmap
    heatmap = sns.heatmap(
        score_matrix, 
        annot=True, 
        fmt=".1f", 
        cmap="viridis", 
        cbar_kws={"label": "Score (0-10)"},
        linewidths=.5,
        ax=ax,
        vmin=0,
        vmax=10
    )
    
    # Set labels
    ax.set_yticklabels(model_names, rotation=0)
    ax.set_xticklabels([name.replace('_', ' ').title() for name in scenario_names], rotation=45, ha='right')
    
    ax.set_title('Model Performance by Scenario Type', pad=20)
    ax.set_xlabel('Scenario', labelpad=10)
    ax.set_ylabel('Model', labelpad=10)
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig


def tool_usage_bar_chart(
    results: Dict[str, Dict[str, Any]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a bar chart showing tool usage metrics by model.
    
    Args:
        results: Dictionary mapping model names to dictionaries of tool usage metrics
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    model_names = list(results.keys())
    metrics = ['tool_selection', 'parameter_quality', 'call_efficiency', 'result_interpretation']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(model_names))
    width = 0.2
    multiplier = 0
    
    # Plot bars for each metric
    for metric in metrics:
        metric_scores = [results[model].get(metric, 0) for model in model_names]
        offset = width * multiplier
        rects = ax.bar(x + offset, metric_scores, width, label=metric.replace('_', ' ').title())
        multiplier += 1
    
    # Add labels, title and legend
    ax.set_ylabel('Score')
    ax.set_title('Tool Usage Performance by Model')
    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
    ax.set_xticklabels(model_names)
    ax.set_ylim(0, 10)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(metrics))
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig


def performance_trend_line(
    turn_scores: Dict[str, List[float]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a line chart showing score trends across conversation turns.
    
    Args:
        turn_scores: Dictionary mapping model names to lists of scores by turn
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each model's scores
    for model_name, scores in turn_scores.items():
        turns = list(range(1, len(scores) + 1))
        ax.plot(turns, scores, marker='o', linewidth=2, markersize=8, label=model_name)
    
    # Add labels and title
    ax.set_xlabel('Conversation Turn')
    ax.set_ylabel('Score (0-10)')
    ax.set_title('Model Performance Across Conversation Turns')
    
    # Set axis limits and ticks
    ax.set_ylim(0, 10)
    max_turns = max(len(scores) for scores in turn_scores.values())
    ax.set_xlim(0.5, max_turns + 0.5)
    ax.set_xticks(range(1, max_turns + 1))
    
    # Add grid and legend
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='best')
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig


def breakdown_stacked_bar(
    results: Dict[str, Dict[str, float]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a stacked bar chart showing score breakdowns by evaluator category.
    
    Args:
        results: Dictionary mapping model names to dictionaries of evaluator scores
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    model_names = list(results.keys())
    categories = list(list(results.values())[0].keys())
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot stacked bars
    bottom = np.zeros(len(model_names))
    
    for category in categories:
        values = [results[model][category] for model in model_names]
        ax.bar(model_names, values, bottom=bottom, label=category.replace('_', ' ').title())
        bottom += values
    
    # Add labels, title and legend
    ax.set_ylabel('Cumulative Score')
    ax.set_title('Score Breakdown by Evaluator Category')
    ax.set_ylim(0, len(categories) * 10)  # Assuming each category has max score of 10
    
    # Add total scores on top of bars
    for i, model in enumerate(model_names):
        total = sum(results[model].values())
        ax.text(i, total + 1, f'Total: {total:.1f}', ha='center')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(categories))
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig


def success_rate_chart(
    success_rates: Dict[str, Dict[str, float]], 
    save_path: Optional[str] = None
) -> Figure:
    """
    Create a grouped bar chart showing success rates by category.
    
    Args:
        success_rates: Dictionary mapping model names to dictionaries of success rates
        save_path: Optional path to save the chart image
        
    Returns:
        Matplotlib figure
    """
    set_plotting_style()
    
    model_names = list(success_rates.keys())
    categories = list(list(success_rates.values())[0].keys())
    
    # Create figure
    fig, ax = plt.subplots(figsize=(max(12, len(categories) * 1.5), 8))
    
    x = np.arange(len(categories))
    width = 0.8 / len(model_names)
    
    # Plot bars for each model
    for i, model_name in enumerate(model_names):
        rates = [success_rates[model_name][cat] * 100 for cat in categories]  # Convert to percentage
        offset = width * i - width * (len(model_names) - 1) / 2
        ax.bar(x + offset, rates, width, label=model_name)
    
    # Add labels, title and legend
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Task Success Rate by Category')
    ax.set_xticks(x)
    ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
    ax.set_ylim(0, 100)
    
    # Add percentage labels on bars
    for i, model in enumerate(model_names):
        for j, cat in enumerate(categories):
            rate = success_rates[model][cat] * 100
            offset = width * i - width * (len(model_names) - 1) / 2
            ax.text(j + offset, rate + 2, f'{rate:.0f}%', ha='center', va='bottom', fontsize=9)
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=min(len(model_names), 3))
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig