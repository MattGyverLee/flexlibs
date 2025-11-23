"""
Text Operations Module - Clusters 1.1-1.2

This package provides Pythonic wrapper methods for FLEx Text operations.

Modules:
    text_core: Core CRUD operations for Text objects (Cluster 1.1)
    text_advanced: Advanced operations for Text objects (Cluster 1.2)
    paragraph_crud: CRUD operations for Paragraph objects (Cluster 1.3)

Author: FlexTools Development Team
Date: 2025-11-22
"""

from .text_core import TextCoreOperations
from .text_advanced import TextAdvancedOperations
from .paragraph_crud import ParagraphCRUDOperations

__all__ = [
    'TextCoreOperations',
    'TextAdvancedOperations',
    'ParagraphCRUDOperations',
]

__version__ = '0.1.0'
