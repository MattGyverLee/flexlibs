"""
Grammar Operations Module

This module provides operations for working with Parts of Speech, Grammatical
Categories, and other grammar-related data in FLEx.

Submodules:
    - pos_crud: Parts of Speech CRUD operations
    - pos_advanced: Advanced POS operations
    - gramcat_ops: Grammatical Categories operations

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from .pos_crud import (
    POSGetAll,
    POSCreate,
    POSDelete,
    POSExists,
    POSFind,
    POSGetName,
    POSSetName,
    POSGetAbbreviation,
    POSSetAbbreviation,
    POSGetSubcategories,
)

from .pos_advanced import (
    POSAddSubcategory,
    POSRemoveSubcategory,
    POSGetCatalogSourceId,
    POSGetInflectionClasses,
    POSGetAffixSlots,
    POSGetEntryCount,
)

from .gramcat_ops import (
    GramCatGetAll,
    GramCatCreate,
    GramCatDelete,
    GramCatGetName,
    GramCatSetName,
    GramCatGetSubcategories,
    GramCatGetParent,
)

__all__ = [
    # POS CRUD operations
    'POSGetAll',
    'POSCreate',
    'POSDelete',
    'POSExists',
    'POSFind',
    'POSGetName',
    'POSSetName',
    'POSGetAbbreviation',
    'POSSetAbbreviation',
    'POSGetSubcategories',

    # POS Advanced operations
    'POSAddSubcategory',
    'POSRemoveSubcategory',
    'POSGetCatalogSourceId',
    'POSGetInflectionClasses',
    'POSGetAffixSlots',
    'POSGetEntryCount',

    # Grammatical Categories operations
    'GramCatGetAll',
    'GramCatCreate',
    'GramCatDelete',
    'GramCatGetName',
    'GramCatSetName',
    'GramCatGetSubcategories',
    'GramCatGetParent',
]
