"""
Phonology Operations Module

This module provides comprehensive operations for phonological data in FLEx,
including phonemes, natural classes, and phonological environments.

Phonology is the study of sound systems in language. This module supports:
- Managing phoneme inventories (the distinctive sounds in a language)
- Defining natural classes (groups of sounds that pattern together)
- Specifying phonological environments (contexts for sound changes)

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

# Import all phoneme CRUD operations (Cluster 2.4)
from .phoneme_crud import (
    PhonemeGetAll,
    PhonemeCreate,
    PhonemeDelete,
    PhonemeExists,
    PhonemeFind,
    PhonemeGetRepresentation,
    PhonemeSetRepresentation,
    PhonemeGetDescription,
    PhonemeSetDescription,
    PhonemeGetFeatures,
)

# Import all phoneme advanced operations (Cluster 2.5)
from .phoneme_advanced import (
    PhonemeGetCodes,
    PhonemeAddCode,
    PhonemeRemoveCode,
    PhonemeGetBasicIPASymbol,
    PhonemeIsVowel,
    PhonemeIsConsonant,
)

# Import all natural class operations (Cluster 2.6)
from .natural_class_ops import (
    NaturalClassGetAll,
    NaturalClassCreate,
    NaturalClassDelete,
    NaturalClassGetName,
    NaturalClassSetName,
    NaturalClassGetAbbreviation,
    NaturalClassGetPhonemes,
    NaturalClassAddPhoneme,
    NaturalClassRemovePhoneme,
)

# Import all phonological environment operations (Cluster 2.7)
from .environment_ops import (
    PhonEnvGetAll,
    PhonEnvCreate,
    PhonEnvDelete,
    PhonEnvGetName,
    PhonEnvSetName,
    PhonEnvGetStringRepresentation,
    PhonEnvSetStringRepresentation,
)

__all__ = [
    # Phoneme CRUD operations (10 methods)
    'PhonemeGetAll',
    'PhonemeCreate',
    'PhonemeDelete',
    'PhonemeExists',
    'PhonemeFind',
    'PhonemeGetRepresentation',
    'PhonemeSetRepresentation',
    'PhonemeGetDescription',
    'PhonemeSetDescription',
    'PhonemeGetFeatures',

    # Phoneme advanced operations (6 methods)
    'PhonemeGetCodes',
    'PhonemeAddCode',
    'PhonemeRemoveCode',
    'PhonemeGetBasicIPASymbol',
    'PhonemeIsVowel',
    'PhonemeIsConsonant',

    # Natural class operations (9 methods)
    'NaturalClassGetAll',
    'NaturalClassCreate',
    'NaturalClassDelete',
    'NaturalClassGetName',
    'NaturalClassSetName',
    'NaturalClassGetAbbreviation',
    'NaturalClassGetPhonemes',
    'NaturalClassAddPhoneme',
    'NaturalClassRemovePhoneme',

    # Phonological environment operations (7 methods)
    'PhonEnvGetAll',
    'PhonEnvCreate',
    'PhonEnvDelete',
    'PhonEnvGetName',
    'PhonEnvSetName',
    'PhonEnvGetStringRepresentation',
    'PhonEnvSetStringRepresentation',
]

# Total: 32 methods across 4 clusters
