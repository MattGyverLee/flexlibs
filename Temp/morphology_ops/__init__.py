"""
Morphology Operations Module

This module provides comprehensive operations for morphological data in FLEx,
including allomorphs, morphological rules, inflection classes, and feature
structures.

Submodules:
- allomorph_ops: Operations for managing allomorphs (variant forms of morphemes)
- morph_rules: Operations for morphological and phonological rules
- inflection_features: Operations for inflection classes and feature structures

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from .allomorph_ops import (
    AllomorphGetAll,
    AllomorphCreate,
    AllomorphDelete,
    AllomorphGetForm,
    AllomorphSetForm,
    AllomorphGetMorphType,
    AllomorphSetMorphType,
    AllomorphGetPhoneEnv,
    AllomorphAddPhoneEnv,
    AllomorphRemovePhoneEnv,
)

from .morph_rules import (
    MorphRuleGetAll,
    MorphRuleCreate,
    MorphRuleDelete,
    MorphRuleGetName,
    MorphRuleSetName,
    MorphRuleGetDescription,
    MorphRuleSetDescription,
    MorphRuleGetStratum,
    MorphRuleSetStratum,
    MorphRuleIsActive,
    MorphRuleSetActive,
)

from .inflection_features import (
    InflectionClassGetAll,
    InflectionClassCreate,
    InflectionClassDelete,
    InflectionClassGetName,
    InflectionClassSetName,
    FeatureStructureGetAll,
    FeatureStructureCreate,
    FeatureStructureDelete,
    FeatureGetAll,
    FeatureCreate,
    FeatureDelete,
    FeatureGetValues,
)

__all__ = [
    # Allomorph operations (10 methods)
    'AllomorphGetAll',
    'AllomorphCreate',
    'AllomorphDelete',
    'AllomorphGetForm',
    'AllomorphSetForm',
    'AllomorphGetMorphType',
    'AllomorphSetMorphType',
    'AllomorphGetPhoneEnv',
    'AllomorphAddPhoneEnv',
    'AllomorphRemovePhoneEnv',

    # Morphological rule operations (11 methods)
    'MorphRuleGetAll',
    'MorphRuleCreate',
    'MorphRuleDelete',
    'MorphRuleGetName',
    'MorphRuleSetName',
    'MorphRuleGetDescription',
    'MorphRuleSetDescription',
    'MorphRuleGetStratum',
    'MorphRuleSetStratum',
    'MorphRuleIsActive',
    'MorphRuleSetActive',

    # Inflection class and feature operations (12 methods)
    'InflectionClassGetAll',
    'InflectionClassCreate',
    'InflectionClassDelete',
    'InflectionClassGetName',
    'InflectionClassSetName',
    'FeatureStructureGetAll',
    'FeatureStructureCreate',
    'FeatureStructureDelete',
    'FeatureGetAll',
    'FeatureCreate',
    'FeatureDelete',
    'FeatureGetValues',
]
