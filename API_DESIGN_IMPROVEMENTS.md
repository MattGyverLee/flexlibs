# FlexLibs2 API Design: Hiding Interface/ClassName/Casting Complexity

**Date:** 2026-02-27
**Problem:** Users frequently get AttributeError when trying to access properties that require casting to concrete types. The relationship between base interfaces, ClassName, and concrete types is opaque.

**Goal:** Make the API easier to use by either clarifying or hiding the casting complexity.

---

## Current Problem

```python
# User writes this
rule = phonRuleOps.GetAll()[0]  # Returns IPhSegmentRule

# Tries to access type-specific property
rhs = rule.RightHandSidesOS  # ❌ AttributeError!
# "IPhSegmentRule has no attribute RightHandSidesOS"

# Debugging journey:
# 1. Check ClassName
print(rule.ClassName)  # "PhRegularRule"

# 2. Realize they need to cast
from SIL.LCModel import IPhRegularRule
concrete = IPhRegularRule(rule)

# 3. NOW it works
rhs = concrete.RightHandSidesOS  # ✅ Works

# But user has to remember this every time!
```

---

## Solution 1: Smart Return Types (RECOMMENDED)

**Concept:** Operations classes return wrapped objects that auto-cast based on ClassName.

### Implementation Example: PhonologicalRuleOperations

```python
class PhonologicalRule:
    """
    User-facing wrapper around IPhSegmentRule that handles casting internally.

    This solves the "which interface do I need?" problem by wrapping the
    actual LCM object and routing property access to the correct concrete type.
    """

    def __init__(self, lcm_obj):
        self._obj = lcm_obj  # Internal IPhSegmentRule
        self._concrete = cast_to_concrete(lcm_obj)  # Cached concrete type

    def __getattr__(self, name):
        """
        Try to get attribute from concrete type first (has more properties),
        then fall back to base interface.

        This ensures users get the right property without thinking about casting.
        """
        try:
            # Try concrete type first (specific to PhRegularRule, etc.)
            return getattr(self._concrete, name)
        except AttributeError:
            # Fall back to base interface
            return getattr(self._obj, name)

    # Expose commonly accessed properties explicitly
    @property
    def name(self):
        """Rule name."""
        return self._obj.Name.BestAnalysisAlternative.Text

    @property
    def input_contexts(self):
        """Input structural description contexts."""
        return list(self._concrete.StrucDescOS)

    @property
    def output_specs(self):
        """Output specifications (right-hand sides)."""
        return list(self._concrete.RightHandSidesOS)

    @property
    def class_type(self):
        """Concrete type (PhRegularRule, PhMetathesisRule, etc.)"""
        return self._obj.ClassName


class PhonologicalRuleOperations(BaseOperations):
    """Operations on phonological rules."""

    def GetAll(self, include_inactive=False):
        """
        Get all phonological rules.

        CHANGED: Returns wrapped PhonologicalRule objects instead of raw
        IPhSegmentRule. User can access any property without worrying about
        which concrete type it is.
        """
        rules = self.project.lp.PhonologicalDataOA.PhonRulesOS

        result = []
        for rule in rules:
            # WRAP the rule - now user gets transparent casting
            result.append(PhonologicalRule(rule))

        return result

    def Find(self, name):
        """Find rule by name. Returns wrapped PhonologicalRule."""
        for rule in self.GetAll():
            if rule.name == name:
                return rule
        return None
```

**User Experience (Much Better!):**
```python
# User writes this
rule = phonRuleOps.GetAll()[0]  # Returns wrapped PhonologicalRule

# Can now access ANY property transparently
rhs = rule.RightHandSidesOS  # ✅ Works! Auto-routed to IPhRegularRule
name = rule.Name  # ✅ Works! Available on base
class_type = rule.class_type  # ✅ Works! Shows "PhRegularRule"

# Or use convenience properties
inputs = rule.input_contexts
outputs = rule.output_specs

# No casting needed, no AttributeError!
```

---

### Wrapper Class Advantages

| Advantage | Impact |
|-----------|--------|
| **Transparent casting** | Users never think about interfaces |
| **Property discovery** | IDE autocomplete shows available properties |
| **Clear documentation** | Docstrings explain what's available |
| **Type safety** | Can validate operations before delegating |
| **Consistent API** | Same pattern across all object types |
| **Backward compatible** | Can expose underlying object if needed |

---

## Solution 2: Property Access Methods

**Concept:** Safe accessor methods that handle casting internally.

```python
class PhonologicalRuleOperations(BaseOperations):
    """Operations on phonological rules."""

    def GetInputContexts(self, rule_or_hvo):
        """
        Get input structural description contexts.

        Safe accessor that works regardless of which concrete rule type.
        Handles casting transparently.
        """
        rule = self.__ResolveObject(rule_or_hvo)
        concrete = cast_to_concrete(rule)

        if hasattr(concrete, 'StrucDescOS'):
            return list(concrete.StrucDescOS)
        return []

    def GetOutputSpecifications(self, rule_or_hvo):
        """
        Get output specifications (right-hand sides).

        Safe accessor that works regardless of rule type.
        """
        rule = self.__ResolveObject(rule_or_hvo)
        concrete = cast_to_concrete(rule)

        if hasattr(concrete, 'RightHandSidesOS'):
            return list(concrete.RightHandSidesOS)
        return []
```

**User Experience:**
```python
rule = phonRuleOps.GetAll()[0]

# Safe accessor methods handle casting
inputs = phonRuleOps.GetInputContexts(rule)
outputs = phonRuleOps.GetOutputSpecifications(rule)

# No AttributeError, clear intent
```

---

## Solution 3: Type-Safe Query Methods

**Concept:** Let users query by concrete type, get back properly-typed objects.

```python
class PhonologicalRuleOperations(BaseOperations):
    """Operations on phonological rules."""

    def GetAllRegularRules(self):
        """Get all PhRegularRule objects."""
        regular_rules = []
        for rule in self.GetAll():
            if rule.ClassName == 'PhRegularRule':
                # Already know it's PhRegularRule
                regular_rules.append(rule)
        return regular_rules

    def GetAllMetathesisRules(self):
        """Get all PhMetathesisRule objects."""
        metathesis_rules = []
        for rule in self.GetAll():
            if rule.ClassName == 'PhMetathesisRule':
                metathesis_rules.append(rule)
        return metathesis_rules

    def GetAllReduplicationRules(self):
        """Get all PhReduplicationRule objects."""
        redup_rules = []
        for rule in self.GetAll():
            if rule.ClassName == 'PhReduplicationRule':
                redup_rules.append(rule)
        return redup_rules
```

**User Experience:**
```python
# Get rules of specific type - now user KNOWS what they have
regular_rules = phonRuleOps.GetAllRegularRules()
for rule in regular_rules:
    # Safe to access PhRegularRule-specific properties
    rhs = rule.RightHandSidesOS  # ✅ Known to exist

# Or use generic method for mixed types
all_rules = phonRuleOps.GetAll()
for rule in all_rules:
    # Type-specific properties still accessible (via wrapper)
    rhs = rule.RightHandSidesOS  # ✅ Works for any rule type
```

---

## Solution 4: Fluent API with Type Guards

**Concept:** Builder pattern that guides users to the right type.

```python
class PhonologicalRuleQuery:
    """Fluent API for querying rules with type safety."""

    def __init__(self, ops):
        self.ops = ops
        self.rules = ops.GetAll()

    def of_type(self, class_name):
        """Filter to specific rule type."""
        self.rules = [r for r in self.rules
                     if r.ClassName == class_name]
        return self

    def regular_rules(self):
        """Get only PhRegularRule objects."""
        return self.of_type('PhRegularRule')

    def metathesis_rules(self):
        """Get only PhMetathesisRule objects."""
        return self.of_type('PhMetathesisRule')

    def named(self, pattern):
        """Filter by name pattern."""
        self.rules = [r for r in self.rules
                     if pattern.lower() in r.name.lower()]
        return self

    def get(self):
        """Execute query, return results."""
        return self.rules


class PhonologicalRuleOperations(BaseOperations):
    """Operations on phonological rules."""

    def query(self):
        """Start a type-safe query."""
        return PhonologicalRuleQuery(self)
```

**User Experience:**
```python
# Clear, discoverable API
rules = phonRuleOps.query().regular_rules().named("voic").get()

# User knows they have PhRegularRule objects
for rule in rules:
    rhs = rule.RightHandSidesOS  # ✅ Safe - filtered to this type
```

---

## Solution 5: Clear Type Documentation

**Concept:** Explicit documentation about which properties belong to which types.

```python
class PhonologicalRule:
    """
    Represents a phonological rule (with auto-casting).

    Properties Available by Type
    ============================

    All Rules (IPhSegmentRule):
        - Name: ITsMultiString - Rule name
        - Description: ITsMultiString - Rule description
        - StratumRA: IPhStratum - Reference to stratum
        - Direction: int - Rule direction
        - StrucDescOS: IEnumerable[IPhPhonContext] - Input contexts

    PhRegularRule Only:
        - RightHandSidesOS: IEnumerable[IPhSegRuleRHS] - Output specifications

    PhMetathesisRule Only:
        - LeftPartOfMetathesisOS: IEnumerable[IPhPhonContext]
        - RightPartOfMetathesisOS: IEnumerable[IPhPhonContext]

    PhReduplicationRule Only:
        - LeftPartOfReduplicationOS: IEnumerable[IPhPhonContext]
        - RightPartOfReduplicationOS: IEnumerable[IPhPhonContext]

    Example
    =======

        rule = phonRuleOps.Find("Voicing")

        # Safe to access any of these:
        name = rule.name              # Convenience property
        inputs = rule.input_contexts  # Wrapped property

        # Check type before accessing type-specific properties:
        if rule.class_type == 'PhRegularRule':
            for rhs in rule.output_specs:
                print(rhs.Guid)
    """
    pass
```

---

## Recommended Approach: Hybrid Solution

Combine multiple solutions for maximum clarity and ease of use:

### **1. Wrapper Objects (Solution 1)**
- Always return wrapped objects from GetAll(), Find(), etc.
- Transparent casting handles 90% of use cases

### **2. Convenience Properties (Solution 1)**
- `rule.input_contexts` instead of `rule.StrucDescOS`
- `rule.output_specs` instead of `rule.RightHandSidesOS`
- `rule.class_type` shows what concrete type it is

### **3. Type-Safe Queries (Solution 3)**
- `GetAllRegularRules()`, `GetAllMetathesisRules()` for type-specific operations
- Users can be confident about property availability

### **4. Clear Documentation (Solution 5)**
- Document which properties belong to which types
- Show examples of checking `class_type` before accessing type-specific properties

### **5. Safe Accessor Methods (Solution 2)**
- For complex operations: `GetInputContexts()`, `GetOutputSpecifications()`
- Delegates casting internally

---

## Implementation Roadmap

### Phase 1: Wrapper Classes (Highest Value)
Create wrapper classes for types with multiple concrete implementations:
- `PhonologicalRule` (wraps IPhSegmentRule)
- `MorphoSyntaxAnalysis` (wraps IMoMorphSynAnalysis)
- `Context` (wraps IPhPhonContext)

### Phase 2: Type-Specific Query Methods
Add filtered query methods:
- `GetAllRegularRules()`
- `GetAllMetathesisRules()`
- `GetAllDerivAffixMsas()`

### Phase 3: Documentation
- Update docstrings with type availability info
- Create guide: "Working with Types that Have Multiple Implementations"
- Add type hierarchy diagrams

### Phase 4: Convenience Properties
Add high-value shortcuts on wrapper classes:
- `rule.input_contexts` → `rule.StrucDescOS`
- `rule.output_specs` → `rule.RightHandSidesOS`

---

## Benefits by Solution

| Solution | Solves | Complexity | User Impact |
|----------|--------|-----------|------------|
| Wrapper Objects | AttributeError | Medium | High - transparent casting |
| Property Methods | Type uncertainty | Low | Medium - safe accessors |
| Type Queries | Type discovery | Low | High - clearer intent |
| Fluent API | Discovery | Medium | High - IDE friendly |
| Documentation | Confusion | Low | High - clear expectations |

---

## Example: Unified Improved API

```python
# Get rules - returns wrapped objects
rules = phonRuleOps.GetAll()

# Check the type
for rule in rules:
    print(f"Rule: {rule.name} ({rule.class_type})")

    # Can access type-specific properties transparently
    if rule.class_type == 'PhRegularRule':
        for rhs in rule.output_specs:  # Wrapper property
            print(f"  Output: {rhs.Guid}")

# Or query by type (clearer intent)
for rule in phonRuleOps.GetAllRegularRules():
    # Guaranteed to be PhRegularRule, so safe to access
    for rhs in rule.RightHandSidesOS:
        print(rhs.Guid)

# Or use type-safe query
rules = phonRuleOps.query().regular_rules().named("voicing").get()
for rule in rules:
    # IDE knows rule is type-filtered
    print(rule.output_specs)
```

---

## Key Design Principles

1. **Transparency**
   - API shouldn't require knowledge of pythonnet/interfaces
   - Casting should be automatic when possible

2. **Explicitness When Needed**
   - `class_type` property makes actual type visible
   - Type-filtered queries make intent clear

3. **Type Safety**
   - Type-filtered methods guarantee property availability
   - Wrapper validates before delegating

4. **Backward Compatibility**
   - Can expose underlying `_obj` for advanced users
   - Old code continues to work

5. **Discoverability**
   - IDE autocomplete shows available properties
   - Docstrings explain type availability
   - Type-safe methods guide users

---

## Next Steps

1. **Prototype** wrapper classes for PhonologicalRule
2. **Test** with user workflows from DEEP_CLONE_ANALYSIS.md
3. **Document** type hierarchy and property availability
4. **Implement** type-filtered query methods based on prototype feedback
5. **Extend** pattern to other multi-concrete-type classes

