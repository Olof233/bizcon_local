"""
Utility functions for advanced analysis and comparison of benchmark results.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import statistics


class BenchmarkAnalyzer:
    """Advanced analysis tools for benchmark results."""
    
    def __init__(self, results: Dict[str, Any]):
        """Initialize with benchmark results."""
        self.results = results
        self.df = self._convert_to_dataframe()
    
    def _convert_to_dataframe(self) -> pd.DataFrame:
        """Convert benchmark results to pandas DataFrame for analysis."""
        rows = []
        
        for model_name, model_data in self.results.items():
            for run in model_data.get('runs', []):
                row = {
                    'model': model_name,
                    'scenario': run.get('scenario', {}).get('name', ''),
                    'overall_score': run.get('overall_score', 0),
                    'timestamp': run.get('timestamp', ''),
                }
                
                # Add evaluator scores
                evaluator_scores = run.get('evaluator_scores', {})
                for evaluator, score in evaluator_scores.items():
                    row[f'eval_{evaluator}'] = score
                
                # Add scenario metadata
                scenario_info = run.get('scenario', {})
                row['industry'] = scenario_info.get('industry', '')
                row['complexity'] = scenario_info.get('complexity', '')
                
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def statistical_summary(self) -> Dict[str, Any]:
        """Generate comprehensive statistical summary."""
        summary = {}
        
        # Overall statistics
        summary['overall'] = {
            'total_models': len(self.results),
            'total_runs': len(self.df),
            'avg_score': self.df['overall_score'].mean(),
            'std_score': self.df['overall_score'].std(),
            'min_score': self.df['overall_score'].min(),
            'max_score': self.df['overall_score'].max(),
            'median_score': self.df['overall_score'].median()
        }
        
        # Per-model statistics
        summary['per_model'] = {}
        for model in self.df['model'].unique():
            model_data = self.df[self.df['model'] == model]
            summary['per_model'][model] = {
                'runs': len(model_data),
                'avg_score': model_data['overall_score'].mean(),
                'std_score': model_data['overall_score'].std(),
                'consistency': 1 / (1 + model_data['overall_score'].std()),  # Higher = more consistent
                'best_scenario': model_data.loc[model_data['overall_score'].idxmax(), 'scenario'],
                'worst_scenario': model_data.loc[model_data['overall_score'].idxmin(), 'scenario'],
                'scenario_count': model_data['scenario'].nunique()
            }
        
        # Per-scenario statistics
        summary['per_scenario'] = {}
        for scenario in self.df['scenario'].unique():
            scenario_data = self.df[self.df['scenario'] == scenario]
            summary['per_scenario'][scenario] = {
                'models_tested': len(scenario_data),
                'avg_score': scenario_data['overall_score'].mean(),
                'difficulty': 10 - scenario_data['overall_score'].mean(),  # Lower avg = harder
                'best_model': scenario_data.loc[scenario_data['overall_score'].idxmax(), 'model'],
                'score_range': scenario_data['overall_score'].max() - scenario_data['overall_score'].min()
            }
        
        return summary
    
    def model_ranking(self, 
                     metric: str = 'overall_score',
                     weight_consistency: float = 0.3) -> List[Dict[str, Any]]:
        """
        Rank models considering both performance and consistency.
        
        Args:
            metric: Metric to rank by
            weight_consistency: Weight for consistency factor (0-1)
            
        Returns:
            List of model rankings with details
        """
        rankings = []
        
        for model in self.df['model'].unique():
            model_data = self.df[self.df['model'] == model]
            
            avg_score = model_data[metric].mean()
            consistency = 1 / (1 + model_data[metric].std())
            
            # Composite score: average performance + consistency bonus
            composite_score = avg_score * (1 - weight_consistency) + consistency * weight_consistency * 10
            
            rankings.append({
                'model': model,
                'avg_score': avg_score,
                'consistency': consistency,
                'composite_score': composite_score,
                'runs': len(model_data),
                'scenarios_tested': model_data['scenario'].nunique()
            })
        
        return sorted(rankings, key=lambda x: x['composite_score'], reverse=True)
    
    def scenario_difficulty_analysis(self) -> Dict[str, Dict[str, float]]:
        """Analyze scenario difficulty based on average scores."""
        difficulty_analysis = {}
        
        for scenario in self.df['scenario'].unique():
            scenario_data = self.df[self.df['scenario'] == scenario]
            
            avg_score = scenario_data['overall_score'].mean()
            score_variance = scenario_data['overall_score'].var()
            
            # Difficulty metrics
            difficulty_analysis[scenario] = {
                'average_score': avg_score,
                'difficulty_rating': 10 - avg_score,  # Inverse of average score
                'discriminative_power': score_variance,  # Higher variance = better discrimination
                'models_tested': len(scenario_data),
                'completion_rate': len(scenario_data[scenario_data['overall_score'] > 5]) / len(scenario_data) * 100
            }
        
        return difficulty_analysis
    
    def correlation_analysis(self) -> pd.DataFrame:
        """Analyze correlations between different evaluation metrics."""
        # Get evaluator columns
        eval_columns = [col for col in self.df.columns if col.startswith('eval_')]
        eval_columns.append('overall_score')
        
        if len(eval_columns) < 2:
            return pd.DataFrame()
        
        correlation_matrix = self.df[eval_columns].corr()
        return correlation_matrix
    
    def performance_trends(self, 
                          time_window: str = 'day') -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze performance trends over time.
        
        Args:
            time_window: Aggregation window ('hour', 'day', 'week')
            
        Returns:
            Dictionary with trends for each model
        """
        if 'timestamp' not in self.df.columns or self.df['timestamp'].isna().all():
            return {}
        
        # Convert timestamp to datetime
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
        
        trends = {}
        for model in self.df['model'].unique():
            model_data = self.df[self.df['model'] == model].copy()
            model_data = model_data.dropna(subset=['datetime'])
            
            if len(model_data) == 0:
                continue
            
            # Group by time window
            if time_window == 'hour':
                model_data['period'] = model_data['datetime'].dt.floor('H')
            elif time_window == 'day':
                model_data['period'] = model_data['datetime'].dt.floor('D')
            elif time_window == 'week':
                model_data['period'] = model_data['datetime'].dt.floor('W')
            
            trend_data = model_data.groupby('period').agg({
                'overall_score': ['mean', 'std', 'count']
            }).round(3)
            
            trends[model] = [
                {
                    'period': period.isoformat(),
                    'avg_score': row[('overall_score', 'mean')],
                    'std_score': row[('overall_score', 'std')],
                    'run_count': row[('overall_score', 'count')]
                }
                for period, row in trend_data.iterrows()
            ]
        
        return trends
    
    def outlier_detection(self, 
                         metric: str = 'overall_score',
                         method: str = 'iqr') -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect outlier performances.
        
        Args:
            metric: Metric to analyze for outliers
            method: Detection method ('iqr', 'zscore')
            
        Returns:
            Dictionary with outliers for each model
        """
        outliers = {}
        
        for model in self.df['model'].unique():
            model_data = self.df[self.df['model'] == model]
            values = model_data[metric]
            
            if method == 'iqr':
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (values < lower_bound) | (values > upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs(statistics.zscore(values))
                outlier_mask = z_scores > 2  # 2 standard deviations
            
            outlier_data = model_data[outlier_mask]
            
            outliers[model] = [
                {
                    'scenario': row['scenario'],
                    'score': row[metric],
                    'timestamp': row.get('timestamp', ''),
                    'is_high': row[metric] > values.median()
                }
                for _, row in outlier_data.iterrows()
            ]
        
        return outliers
    
    def comparative_analysis(self, 
                           model1: str, 
                           model2: str) -> Dict[str, Any]:
        """
        Perform detailed comparative analysis between two models.
        
        Args:
            model1: First model name
            model2: Second model name
            
        Returns:
            Comprehensive comparison analysis
        """
        data1 = self.df[self.df['model'] == model1]
        data2 = self.df[self.df['model'] == model2]
        
        if len(data1) == 0 or len(data2) == 0:
            return {'error': 'One or both models not found'}
        
        analysis = {
            'models': [model1, model2],
            'overall_comparison': {},
            'scenario_comparison': {},
            'evaluator_comparison': {},
            'statistical_tests': {},
            'recommendations': []
        }
        
        # Overall comparison
        analysis['overall_comparison'] = {
            model1: {
                'avg_score': data1['overall_score'].mean(),
                'median_score': data1['overall_score'].median(),
                'std_score': data1['overall_score'].std(),
                'runs': len(data1)
            },
            model2: {
                'avg_score': data2['overall_score'].mean(),
                'median_score': data2['overall_score'].median(),
                'std_score': data2['overall_score'].std(),
                'runs': len(data2)
            }
        }
        
        # Scenario-by-scenario comparison
        common_scenarios = set(data1['scenario']) & set(data2['scenario'])
        for scenario in common_scenarios:
            s1_scores = data1[data1['scenario'] == scenario]['overall_score']
            s2_scores = data2[data2['scenario'] == scenario]['overall_score']
            
            analysis['scenario_comparison'][scenario] = {
                model1: s1_scores.mean() if len(s1_scores) > 0 else 0,
                model2: s2_scores.mean() if len(s2_scores) > 0 else 0,
                'advantage': model1 if s1_scores.mean() > s2_scores.mean() else model2
            }
        
        # Evaluator comparison
        eval_columns = [col for col in self.df.columns if col.startswith('eval_')]
        for eval_col in eval_columns:
            eval_name = eval_col.replace('eval_', '')
            e1_scores = data1[eval_col].mean()
            e2_scores = data2[eval_col].mean()
            
            analysis['evaluator_comparison'][eval_name] = {
                model1: e1_scores,
                model2: e2_scores,
                'difference': e1_scores - e2_scores,
                'advantage': model1 if e1_scores > e2_scores else model2
            }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on comparison."""
        recommendations = []
        
        model1, model2 = comparison['models']
        overall1 = comparison['overall_comparison'][model1]
        overall2 = comparison['overall_comparison'][model2]
        
        # Performance recommendations
        if overall1['avg_score'] > overall2['avg_score']:
            recommendations.append(f"Consider using {model1} for general tasks (higher average performance)")
        else:
            recommendations.append(f"Consider using {model2} for general tasks (higher average performance)")
        
        # Consistency recommendations
        if overall1['std_score'] < overall2['std_score']:
            recommendations.append(f"{model1} shows more consistent performance across scenarios")
        else:
            recommendations.append(f"{model2} shows more consistent performance across scenarios")
        
        # Scenario-specific recommendations
        eval_comp = comparison.get('evaluator_comparison', {})
        for evaluator, scores in eval_comp.items():
            if abs(scores['difference']) > 1.0:  # Significant difference
                winner = scores['advantage']
                recommendations.append(f"Use {winner} for tasks requiring strong {evaluator.replace('_', ' ')}")
        
        return recommendations
    
    def export_analysis(self, 
                       output_path: str,
                       include_raw_data: bool = True) -> None:
        """
        Export comprehensive analysis to files.
        
        Args:
            output_path: Directory to save analysis files
            include_raw_data: Whether to include raw data export
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Statistical summary
        summary = self.statistical_summary()
        with open(output_dir / f'statistical_summary_{timestamp}.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Model rankings
        rankings = self.model_ranking()
        with open(output_dir / f'model_rankings_{timestamp}.json', 'w') as f:
            json.dump(rankings, f, indent=2, default=str)
        
        # Scenario difficulty
        difficulty = self.scenario_difficulty_analysis()
        with open(output_dir / f'scenario_difficulty_{timestamp}.json', 'w') as f:
            json.dump(difficulty, f, indent=2, default=str)
        
        # Correlation analysis
        correlation = self.correlation_analysis()
        if not correlation.empty:
            correlation.to_csv(output_dir / f'correlation_matrix_{timestamp}.csv')
        
        # Raw data export
        if include_raw_data:
            self.df.to_csv(output_dir / f'benchmark_data_{timestamp}.csv', index=False)
        
        print(f"Analysis exported to {output_dir}")


class FilterManager:
    """Manager for advanced filtering of benchmark results."""
    
    def __init__(self, results: Dict[str, Any]):
        """Initialize with benchmark results."""
        self.results = results
    
    def filter_by_models(self, 
                        model_names: List[str]) -> Dict[str, Any]:
        """Filter results to include only specified models."""
        return {
            model: data for model, data in self.results.items() 
            if model in model_names
        }
    
    def filter_by_scenarios(self, 
                          scenario_patterns: List[str]) -> Dict[str, Any]:
        """Filter results to include only scenarios matching patterns."""
        filtered_results = {}
        
        for model, model_data in self.results.items():
            filtered_runs = []
            for run in model_data.get('runs', []):
                scenario_name = run.get('scenario', {}).get('name', '')
                if any(pattern in scenario_name for pattern in scenario_patterns):
                    filtered_runs.append(run)
            
            if filtered_runs:
                model_data_copy = model_data.copy()
                model_data_copy['runs'] = filtered_runs
                filtered_results[model] = model_data_copy
        
        return filtered_results
    
    def filter_by_score_range(self, 
                            min_score: float = 0,
                            max_score: float = 10,
                            metric: str = 'overall_score') -> Dict[str, Any]:
        """Filter results by score range."""
        filtered_results = {}
        
        for model, model_data in self.results.items():
            filtered_runs = []
            for run in model_data.get('runs', []):
                score = run.get(metric, 0)
                if min_score <= score <= max_score:
                    filtered_runs.append(run)
            
            if filtered_runs:
                model_data_copy = model_data.copy()
                model_data_copy['runs'] = filtered_runs
                filtered_results[model] = model_data_copy
        
        return filtered_results
    
    def filter_by_date_range(self, 
                           start_date: str,
                           end_date: str) -> Dict[str, Any]:
        """Filter results by date range."""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        filtered_results = {}
        
        for model, model_data in self.results.items():
            filtered_runs = []
            for run in model_data.get('runs', []):
                timestamp = run.get('timestamp', '')
                if timestamp:
                    try:
                        run_date = datetime.fromisoformat(timestamp)
                        if start <= run_date <= end:
                            filtered_runs.append(run)
                    except ValueError:
                        continue
            
            if filtered_runs:
                model_data_copy = model_data.copy()
                model_data_copy['runs'] = filtered_runs
                filtered_results[model] = model_data_copy
        
        return filtered_results
    
    def filter_by_complexity(self, 
                           complexities: List[str]) -> Dict[str, Any]:
        """Filter results by scenario complexity levels."""
        filtered_results = {}
        
        for model, model_data in self.results.items():
            filtered_runs = []
            for run in model_data.get('runs', []):
                complexity = run.get('scenario', {}).get('complexity', '')
                if complexity in complexities:
                    filtered_runs.append(run)
            
            if filtered_runs:
                model_data_copy = model_data.copy()
                model_data_copy['runs'] = filtered_runs
                filtered_results[model] = model_data_copy
        
        return filtered_results
    
    def apply_multiple_filters(self, 
                             filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply multiple filters in sequence."""
        results = self.results.copy()
        
        if 'models' in filters and filters['models']:
            filter_manager = FilterManager(results)
            results = filter_manager.filter_by_models(filters['models'])
        
        if 'scenarios' in filters and filters['scenarios']:
            filter_manager = FilterManager(results)
            results = filter_manager.filter_by_scenarios(filters['scenarios'])
        
        if 'score_range' in filters:
            range_filter = filters['score_range']
            filter_manager = FilterManager(results)
            results = filter_manager.filter_by_score_range(
                range_filter.get('min', 0),
                range_filter.get('max', 10),
                range_filter.get('metric', 'overall_score')
            )
        
        if 'date_range' in filters:
            date_filter = filters['date_range']
            filter_manager = FilterManager(results)
            results = filter_manager.filter_by_date_range(
                date_filter['start'],
                date_filter['end']
            )
        
        if 'complexities' in filters and filters['complexities']:
            filter_manager = FilterManager(results)
            results = filter_manager.filter_by_complexity(filters['complexities'])
        
        return results