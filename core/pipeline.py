"""
Evaluation pipeline for running benchmarks on LLMs.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import os
import datetime
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Use relative import for core module
from .runner import ScenarioRunner

# Use absolute imports for other modules since they're at the same level as core
from ..models.base import ModelClient
from ..scenarios.base import BusinessScenario
from ..evaluators.base import BaseEvaluator
from ..tools.base import BusinessTool
from ..visualization.report import generate_report


class EvaluationPipeline:
    """Pipeline for evaluating LLMs on business conversation tasks."""
    
    def __init__(self, 
                 models: List[ModelClient],
                 scenarios: List[BusinessScenario],
                 evaluators: Optional[List[BaseEvaluator]] = None,
                 tools: Optional[Dict[str, BusinessTool]] = None,
                 num_runs: int = 1,
                 parallel: bool = False,
                 verbose: bool = False):
        """
        Initialize the evaluation pipeline.
        
        Args:
            models: List of model clients to evaluate
            scenarios: List of business scenarios to run
            evaluators: Optional list of evaluators (uses default set if None)
            tools: Optional dictionary of tools (uses default set if None)
            num_runs: Number of times to run each scenario (for consistency)
            parallel: Whether to run evaluations in parallel
            verbose: Whether to print detailed progress
        """
        self.models = models
        self.scenarios = scenarios
        self.evaluators = evaluators or self._get_default_evaluators()
        self.tools = tools or self._get_default_tools()
        self.num_runs = num_runs
        self.parallel = parallel
        self.verbose = verbose
        self.results = {}
        
    def _get_default_evaluators(self) -> List[BaseEvaluator]:
        """Get the default set of evaluators."""
        from ..evaluators.response_quality import ResponseQualityEvaluator
        from ..evaluators.communication_style import CommunicationStyleEvaluator
        from ..evaluators.tool_usage import ToolUsageEvaluator
        from ..evaluators.business_value import BusinessValueEvaluator
        from ..evaluators.performance import PerformanceEvaluator
        
        return [
            ResponseQualityEvaluator(weight=0.25),
            CommunicationStyleEvaluator(weight=0.20),
            ToolUsageEvaluator(weight=0.20),
            BusinessValueEvaluator(weight=0.25),
            PerformanceEvaluator(weight=0.10)
        ]
    
    def _get_default_tools(self) -> Dict[str, BusinessTool]:
        """Get the default set of business tools."""
        from ..tools.knowledge_base import KnowledgeBaseTool
        from ..tools.scheduler import SchedulerTool
        from ..tools.product_catalog import ProductCatalogTool
        from ..tools.customer_history import CustomerHistoryTool
        from ..tools.pricing_calculator import PricingCalculatorTool
        from ..tools.order_management import OrderManagementTool
        from ..tools.support_ticket import SupportTicketTool
        from ..tools.document_retrieval import DocumentRetrievalTool
        
        tools = {
            "knowledge_base": KnowledgeBaseTool(),
            "scheduler": SchedulerTool(),
            "product_catalog": ProductCatalogTool(),
            "customer_history": CustomerHistoryTool(),
            "pricing_calculator": PricingCalculatorTool(),
            "order_management": OrderManagementTool(),
            "support_ticket": SupportTicketTool(),
            "document_retrieval": DocumentRetrievalTool()
        }
        
        return tools
    
    def run(self) -> Dict[str, Any]:
        """
        Run the evaluation pipeline.
        
        Returns:
            Dictionary with evaluation results
        """
        start_time = time.time()
        self.results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "models": [model.get_usage_stats() for model in self.models],
            "scenarios": [scenario.get_metadata() for scenario in self.scenarios],
            "evaluators": [evaluator.get_metadata() for evaluator in self.evaluators],
            "tools": [tool.get_usage_stats() for tool in self.tools.values()],
            "num_runs": self.num_runs,
            "results": {}
        }
        
        # Reset model and tool statistics
        for model in self.models:
            model.reset_stats()
        
        for tool in self.tools.values():
            tool.reset_stats()
        
        # Create a list of all model-scenario pairs to evaluate
        evaluation_tasks = []
        for scenario in self.scenarios:
            for model in self.models:
                for run_num in range(self.num_runs):
                    evaluation_tasks.append((model, scenario, run_num))
        
        # Run evaluations (in parallel or sequentially)
        if self.parallel and len(evaluation_tasks) > 1:
            with ThreadPoolExecutor() as executor:
                results = list(tqdm(
                    executor.map(self._run_evaluation_task, evaluation_tasks),
                    total=len(evaluation_tasks),
                    desc="Running evaluations",
                    disable=not self.verbose
                ))
        else:
            results = []
            for task in tqdm(evaluation_tasks, disable=not self.verbose):
                results.append(self._run_evaluation_task(task))
        
        # Organize results by model and scenario
        for result in results:
            model_id = result["model_id"]
            scenario_id = result["scenario_id"]
            run_num = result["run_num"]
            
            if model_id not in self.results["results"]:
                self.results["results"][model_id] = {}
                
            if scenario_id not in self.results["results"][model_id]:
                self.results["results"][model_id][scenario_id] = []
                
            self.results["results"][model_id][scenario_id].append(result)
        
        # Add summary statistics
        self.results["summary"] = self._calculate_summary()
        self.results["duration"] = time.time() - start_time
        self.results["models"] = [model.get_usage_stats() for model in self.models]
        self.results["tools"] = [tool.get_usage_stats() for tool in self.tools.values()]
        
        return self.results
    
    def _run_evaluation_task(self, task: Tuple[ModelClient, BusinessScenario, int]) -> Dict[str, Any]:
        """
        Run a single evaluation task.
        
        Args:
            task: Tuple of (model, scenario, run_number)
            
        Returns:
            Dictionary with evaluation results
        """
        model, scenario, run_num = task
        
        if self.verbose:
            print(f"Running {model.model_name} on {scenario.name} (run {run_num+1}/{self.num_runs})")
        
        # Create a runner for this scenario
        runner = ScenarioRunner(
            model=model,
            scenario=scenario,
            evaluators=self.evaluators,
            tools=self.tools
        )
        
        # Run the scenario
        result = runner.run()
        result["model_id"] = model.model_name
        result["scenario_id"] = scenario.scenario_id
        result["run_num"] = run_num
        
        return result
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """
        Calculate summary statistics across all evaluations.
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "overall_scores": {},
            "category_scores": {},
            "scenario_scores": {}
        }
        
        # Calculate overall scores for each model
        for model_id, model_results in self.results["results"].items():
            all_scores = []
            category_scores = {}
            
            for scenario_id, scenario_runs in model_results.items():
                for run in scenario_runs:
                    all_scores.append(run["overall_score"])
                    
                    # Aggregate category scores
                    for category, score in run["category_scores"].items():
                        if category not in category_scores:
                            category_scores[category] = []
                        category_scores[category].append(score)
            
            # Store average overall score
            summary["overall_scores"][model_id] = sum(all_scores) / len(all_scores) if all_scores else 0
            
            # Store average category scores
            summary["category_scores"][model_id] = {
                category: sum(scores) / len(scores) if scores else 0
                for category, scores in category_scores.items()
            }
            
            # Calculate per-scenario scores
            scenario_scores = {}
            for scenario_id, scenario_runs in model_results.items():
                scenario_scores[scenario_id] = sum(run["overall_score"] for run in scenario_runs) / len(scenario_runs)
            
            summary["scenario_scores"][model_id] = scenario_scores
        
        return summary
    
    def generate_report(self, output_dir: str) -> None:
        """
        Generate a report with visualizations and analysis.
        
        Args:
            output_dir: Directory to save the report
        """
        if not self.results:
            raise ValueError("No results available. Run the pipeline first.")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save raw results
        with open(os.path.join(output_dir, "results.json"), "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate CSV data
        self._generate_csv_data(output_dir)
        
        # Generate report with visualizations
        generate_report(self.results, output_dir)
    
    def _generate_csv_data(self, output_dir: str) -> None:
        """
        Generate CSV files with evaluation data.
        
        Args:
            output_dir: Directory to save CSV files
        """
        # Overall scores
        overall_df = pd.DataFrame([
            {
                "model": model_id,
                "overall_score": score
            }
            for model_id, score in self.results["summary"]["overall_scores"].items()
        ])
        
        if not overall_df.empty:
            overall_df.to_csv(os.path.join(output_dir, "overall_scores.csv"), index=False)
        
        # Category scores
        category_rows = []
        for model_id, categories in self.results["summary"]["category_scores"].items():
            for category, score in categories.items():
                category_rows.append({
                    "model": model_id,
                    "category": category,
                    "score": score
                })
        
        category_df = pd.DataFrame(category_rows)
        if not category_df.empty:
            category_df.to_csv(os.path.join(output_dir, "category_scores.csv"), index=False)
        
        # Scenario scores
        scenario_rows = []
        for model_id, scenarios in self.results["summary"]["scenario_scores"].items():
            for scenario_id, score in scenarios.items():
                # Get scenario name from metadata
                scenario_name = next((s["name"] for s in self.results["scenarios"] 
                                     if s["scenario_id"] == scenario_id), scenario_id)
                
                scenario_rows.append({
                    "model": model_id,
                    "scenario_id": scenario_id,
                    "scenario_name": scenario_name,
                    "score": score
                })
        
        scenario_df = pd.DataFrame(scenario_rows)
        if not scenario_df.empty:
            scenario_df.to_csv(os.path.join(output_dir, "scenario_scores.csv"), index=False)