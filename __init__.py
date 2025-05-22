"""
bizCon: Business Conversation Evaluation Framework for LLMs

A comprehensive evaluation framework for benchmarking Large Language Models
on business conversation capabilities. It assesses how well different models
handle realistic business interactions involving tools, professional communication,
and accurate information delivery.
"""

__version__ = "0.1.0"

# Core imports
from core.pipeline import EvaluationPipeline
from core.runner import ScenarioRunner

# Expose key functionality
from models import get_model_client, list_supported_models
from scenarios import load_scenarios, list_available_scenarios
from evaluators import get_all_evaluators
from tools import get_default_tools
from visualization.dashboard import launch_dashboard
from visualization.report import generate_report

# Make key classes available at package level
from models.base import ModelClient
from scenarios.base import BusinessScenario
from evaluators.base import BaseEvaluator
from tools.base import BusinessTool