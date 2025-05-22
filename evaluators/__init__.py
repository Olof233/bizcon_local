"""
bizCon evaluators package.
"""
from typing import Dict, Type, List

# Use relative imports instead of bizcon package imports
from .base import BaseEvaluator
from .business_value import BusinessValueEvaluator
from .communication_style import CommunicationStyleEvaluator
from .performance import PerformanceEvaluator
from .response_quality import ResponseQualityEvaluator
from .tool_usage import ToolUsageEvaluator

# Register all evaluator classes
EVALUATOR_REGISTRY: Dict[str, Type[BaseEvaluator]] = {
    "business_value": BusinessValueEvaluator,
    "communication_style": CommunicationStyleEvaluator,
    "performance": PerformanceEvaluator,
    "response_quality": ResponseQualityEvaluator,
    "tool_usage": ToolUsageEvaluator,
}

def get_evaluator(evaluator_name: str, **kwargs) -> BaseEvaluator:
    """
    Get an evaluator instance by name.
    
    Args:
        evaluator_name: Name of the evaluator to get
        **kwargs: Arguments to pass to the evaluator constructor
        
    Returns:
        Instance of the requested evaluator
        
    Raises:
        ValueError: If the evaluator name is not registered
    """
    if evaluator_name not in EVALUATOR_REGISTRY:
        raise ValueError(f"Unknown evaluator: {evaluator_name}. Available evaluators: {list(EVALUATOR_REGISTRY.keys())}")
    
    return EVALUATOR_REGISTRY[evaluator_name](**kwargs)

def get_all_evaluators(weights: Dict[str, float] = None) -> List[BaseEvaluator]:
    """
    Get instances of all registered evaluators.
    
    Args:
        weights: Optional dictionary mapping evaluator names to weights
        
    Returns:
        List of evaluator instances
    """
    if weights is None:
        weights = {name: 1.0 for name in EVALUATOR_REGISTRY}
    
    evaluators = []
    for name, cls in EVALUATOR_REGISTRY.items():
        weight = weights.get(name, 1.0)
        evaluators.append(cls(weight=weight))
    
    return evaluators