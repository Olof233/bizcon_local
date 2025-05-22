"""
Core package for bizCon framework.
Contains pipeline, runner, and utility modules.
"""
from .pipeline import EvaluationPipeline
from .runner import ScenarioRunner
from .utils import load_yaml_file, save_yaml_file