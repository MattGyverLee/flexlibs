# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.4.1] - 2026-03-16

### Fixed

#### Decorator Bugs
- **Duplicate `@OperationsMethod` decorators** - Fixed `'OperationsMethod' object is not callable'` errors
  - BaseOperations.py: Removed duplicates from 9 reordering/sync methods
  - POSOperations.py: Removed duplicates from 17 methods (including GetAll)
  - LexEntryOperations.py: Removed duplicates from 5 methods
  - All 64 operation files verified clean

### Added

#### Pre-commit Hooks
- Custom decorator validator prevents duplicate decorators
- Black code formatting enforcement
- Flake8 linting (unused imports, complexity)
- Detect-secrets for credential detection
- Setup documentation in docs/PRE_COMMIT_SETUP.md
- Decorator checking script in scripts/check_decorators.py

---

## [2.3.0] - 2026-02-28

### Added

#### Extended Wrapper Classes
- **Allomorph**: Wrapper for allomorph variants and forms
  - Form and gloss access with normalization
  - Environment context tracking
  - Variant relationship management

- **CompoundRule**: Wrapper for compound rule definitions
  - Rule component access
  - Directional compound rules
  - Integration with morpheme inventories

- **AdhocProhibition**: Wrapper for morphosyntactic prohibitions
  - Prohibited morpheme combinations
  - Context-aware blocking rules
  - Exception handling

- **Annotation**: Wrapper for project annotations and notes
  - Annotation type identification
  - Content and metadata access
  - Author and timestamp tracking

- **AffixTemplate**: Wrapper for morpheme slot templates
  - Slot configuration and ordering
  - Prefix and suffix slot management
  - Obligatory/optional slot constraints

#### Smart Collections (Extended)
- **AllomorphCollection**: Type-aware collection for allomorphs
- **CompoundRuleCollection**: Unified collection for compound rules
- **ProhibitionCollection**: Collection for morphosyntactic prohibitions
- **AnnotationCollection**: Collection for project annotations
- **AffixTemplateCollection**: Collection for affix templates

#### Type Hints and IDE Support
- Python type hints on all wrapper class properties (18+ properties)
- Improved IDE autocomplete and type checking
- Better static analysis support

#### Documentation
- **USAGE_ALLOMORPHS.md**: Allomorph operations guide
- **USAGE_COMPOUND_RULES.md**: Compound rule operations guide
- **USAGE_PROHIBITIONS.md**: Morphosyntactic prohibition guide
- **USAGE_ANNOTATIONS.md**: Annotation operations guide
- **USAGE_AFFIX_TEMPLATES.md**: Affix template operations guide

### Improved

- **Code Quality**: Type hints across all wrapper classes
- **Documentation**: Usage guides for all new domains
- **Test Coverage**: Extended test suite for new wrappers
- **API Consistency**: All collections follow unified interface

### Backward Compatibility

- **100% Maintained**: All v2.0 and v2.1 APIs unchanged
- **Additive Only**: New wrappers don't modify existing functionality
- **Mixed Usage**: Old and new approaches coexist seamlessly

### Deprecation Notices

None. All previous APIs remain fully functional.

---

## [2.2.0] - 2025-02-28

### Added

#### Wrapper Classes
- **PhonologicalRule**: Unified wrapper for PhRegularRule, PhMetathesisRule, and PhReduplicationRule
  - Transparent casting to concrete types
  - Capability-based API (`has_output_specs`, `has_metathesis_parts`, `has_reduplication_parts`)
  - Convenience properties for common operations
  - Full backward compatibility with base interface

- **MorphosyntaxAnalysis**: Unified wrapper for MoStemMsa, MoDerivAffMsa, MoInflAffMsa, and MoUnclassifiedAffMsa
  - Type identification properties (`is_stem_msa`, `is_deriv_aff`, `is_infl_aff`)
  - Automatic casting based on actual type
  - Convenience properties for POS access
  - Proper string representation showing actual type

- **PhonologicalContext**: Unified wrapper for PhSimpleContextSeg, PhSimpleContextNC, PhComplexContext, and PhBoundaryContext
  - Context type detection (`is_simple_context`, `is_complex_context`, `is_boundary_context`)
  - Segment-based vs natural class detection
  - Convenience properties for accessing context-specific data
  - Clear display of context type

#### Smart Collections
- **RuleCollection**: Collection class for phonological rules
  - Type-aware display showing breakdown of rule types
  - Convenience filter methods (`regular_rules`, `metathesis_rules`, `reduplication_rules`)
  - Custom filtering with `filter_where()` across all rule types
  - Support for method chaining

- **MSACollection**: Collection class for morphosyntactic analyses
  - Type-aware display showing MSA type breakdown
  - Convenience filters (`stem_msas`, `deriv_aff_msas`, `infl_aff_msas`, `unclassified_aff_msas`)
  - POS-based filtering (`filter_by_pos()`)
  - Advanced filtering with `filter_by_has_pos()`, `filter_where()`

- **ContextCollection**: Collection class for phonological contexts
  - Type-aware display with context type breakdown
  - Convenience filters for all context types
  - Custom filtering capabilities
  - Full iteration and indexing support

#### Base Infrastructure
- **LCMObjectWrapper**: Base class for all wrapper implementations
  - Automatic delegation to concrete interfaces
  - Consistent property access across types
  - Exception handling for missing properties
  - `__getattr__` delegation pattern for seamless access

- **SmartCollection**: Base class for all collection types
  - Type-aware string representation
  - By-type filtering with `by_type()`
  - Generic filtering framework
  - Standard collection operations (append, extend, clear)

### Improved

- **Type Transparency**: Users no longer need to manually check `ClassName` and cast to concrete types
- **IDE Support**: Wrapper classes provide better autocomplete and type hints
- **Error Messages**: Type mismatches produce clear, actionable error messages
- **Filtering**: Unified filtering across type hierarchies without manual type checking
- **Documentation**: Comprehensive examples in docstrings and test suite
- **Code Maintainability**: Internal casting hidden from public API, reducing complexity

### Fixed

- **AttributeError Prevention**: Capability checks prevent accessing unavailable properties
- **Type Safety**: Automatic casting ensures correct interface access
- **Method Chaining**: Collections support fluent filtering patterns

### Documentation

- **MIGRATION.md**: Complete migration guide showing old vs new API
  - Side-by-side examples for all three domains
  - Backward compatibility notes
  - Gradual vs immediate migration strategies
  - Feature comparison table

- **Wrapper Classes Documentation**: Comprehensive docstrings
  - Usage examples in all wrapper classes
  - Capability-based API documented
  - Type detection methods explained

- **Smart Collections Guide**: Collection usage patterns
  - Filtering examples
  - Type-aware display explanation
  - Convenience method documentation

### Backward Compatibility

- **Zero Breaking Changes**: All existing v2.1 code runs unchanged
- **Additive Design**: New wrappers are purely additive, don't modify existing API
- **Mixed Usage**: Old and new approaches can coexist in same codebase
- **Gradual Migration**: Users can migrate at their own pace
- **Base Interface Access**: Direct access to base ILcmObjects still available

### Tests

**Core Wrapper Tests** (41 tests)
- LCM Object wrapper initialization and delegation
- Concrete property access across types
- Exception handling and edge cases
- Attribute error prevention

**Collection Tests** (70 tests)
- SmartCollection initialization and operations
- Indexing, slicing, iteration
- Type-aware string representation
- By-type filtering and custom filtering

**Domain-Specific Tests** (68 tests)
- **Phonological Rules**: RuleCollection and PhonologicalRule wrapper
  - Regular rule properties
  - Metathesis rule properties
  - Reduplication rule properties
  - Convenience filters and chaining

- **MSAs**: MSACollection and MorphosyntaxAnalysis wrapper
  - Stem MSA properties and filters
  - Derivational affixal MSA properties
  - Inflectional affixal MSA properties
  - POS-based filtering and detection

- **Contexts**: ContextCollection and PhonologicalContext wrapper
  - Simple context (segment-based) properties
  - Simple context (natural class) properties
  - Complex context properties
  - Boundary context properties
  - Type convenience filters

**Total: 179 tests passing, 0 failures, 0 regressions**

### Performance

- No performance degradation compared to v2.1
- Wrapper overhead minimal (delegation pattern)
- Collection operations O(n) as expected
- Lazy evaluation in filter chains

### Known Limitations

- Wrappers currently available for three domains:
  - Grammar: Phonological Rules
  - Lexicon: Morphosyntactic Analyses
  - Grammar: Phonological Contexts
- Other domains will receive wrapper support in v2.3+
- Direct operations still available for all domains

### Deprecation Notices

None. All v2.1 API remains fully functional.

---

## [2.1.0] - Previous Release

See git history for previous changelog entries.

---

## How to Upgrade

### From Earlier Versions to v2.3.0

No action required. Simply upgrade the package:

```bash
pip install flexlibs2==2.3.0
```

Existing code will continue to work unchanged. All v2.0, v2.1, and v2.2 APIs remain fully functional.

### Using Wrapper Classes

To use the latest wrappers for additional domains:

```python
from flexlibs2.wrappers import Allomorph, CompoundRule, AffixTemplate
from flexlibs2.collections import AllomorphCollection, CompoundRuleCollection

# Work with allomorphs transparently
allomorphs = project.Allomorph.GetAll()
for allomorph in allomorphs:
    print(f"{allomorph.form}: {allomorph.gloss}")
```

Existing code continues to work without modification.

---

## Future Roadmap

### v2.4.0 (Planned)

- Performance optimizations for large collections
- Advanced query builder pattern
- Integration with FLEx import/export
- Extended wrapper support for remaining domains

### v3.0.0 (Future)

- Complete wrapper coverage for all domains
- Potential breaking changes for major improvements
- Enhanced type safety with static typing

---

## Contributing

See CONTRIBUTING.md for guidelines on contributing to FlexLibs2.

---

## Version Support

- **v2.3.x**: Current stable release, actively maintained
- **v2.2.x**: Previous stable, maintenance only
- **v2.1.x**: Legacy, security fixes only
- **v2.0.x**: End of life
- **v1.x**: End of life

