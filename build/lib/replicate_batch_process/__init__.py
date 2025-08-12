"""
Replicate Batch Process - Intelligent batch processing for Replicate models

Main exports:
- replicate_model_calling: Single image generation
- intelligent_batch_process: Simple batch processing  
- IntelligentBatchProcessor: Advanced batch processing with mixed models
- BatchRequest: Request object for advanced batch processing
"""

from .main import replicate_model_calling
from .intelligent_batch_processor import (
    intelligent_batch_process,
    IntelligentBatchProcessor,
    BatchRequest
)

__version__ = "1.0.7"
__author__ = "preangelleo"

__all__ = [
    "replicate_model_calling",
    "intelligent_batch_process", 
    "IntelligentBatchProcessor",
    "BatchRequest"
]