# API Philosophy Shift: From Technical to Human-Centric

**Date:** 2026-02-27
**Direction:** Move from exposing technical complexity to hiding it while maximizing functionality.

---

## The Shift

### OLD Philosophy: "Expose the Technology"
```
User must understand:
├─ Base interfaces
├─ ClassName attributes
├─ Concrete type mapping
├─ Casting operations
└─ Type-specific properties

Result: Users get frustrated with AttributeError
```

### NEW Philosophy: "Hide Complexity, Maximize Functionality"
```
User thinks in abstractions:
├─ "Get all rules"
├─ "Filter by name"
├─ "Access common properties"
├─ "Merge and get a warning"
└─ "See type diversity in results"

Result: API works the way users naturally think
```

---

## Side-by-Side Comparison

### Scenario 1: Get All Rules

**OLD API (Forces Type Awareness)**
```python
# User has to know types exist and manage them separately
regular = phonRuleOps.GetAll(class_type='PhRegularRule')
metathesis = phonRuleOps.GetAll(class_type='PhMetathesisRule')
redup = phonRuleOps.GetAll(class_type='PhReduplicationRule')

all_rules = regular + metathesis + redup

# User has to piece together what they got
print(f"Regular: {len(regular)}, Metathesis: {len(metathesis)}, Redup: {len(redup)}")
```

**NEW API (Natural Abstraction Level)**
```python
# User asks naturally: "Give me all rules"
all_rules = phonRuleOps.GetAll()

# System shows what they got with a helpful summary
print(all_rules)
# Phonological Rules Summary (12 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   7 rules ( 58.3%)
#   PhMetathesisRule        :   3 rules ( 25.0%)
#   PhReduplicationRule     :   2 rules ( 16.7%)
```

---

### Scenario 2: Access Properties

**OLD API (Requires Type Checking)**
```python
rule = phonRuleOps.Find("something")

# User must check ClassName and cast
if rule.ClassName == 'PhRegularRule':
    from SIL.LCModel import IPhRegularRule
    concrete = IPhRegularRule(rule)
    outputs = concrete.RightHandSidesOS
elif rule.ClassName == 'PhMetathesisRule':
    # Doesn't have RightHandSidesOS!
    outputs = None
```

**NEW API (Type-Transparent)**
```python
rule = phonRuleOps.Find("something")

# Works for ANY type - returns what exists
outputs = rule.output_segments

# Or check capability first
if rule.has_output_specs:
    do_something(rule.output_segments)

# No ClassName checking, no casting!
```

---

### Scenario 3: Filter Across Types

**OLD API (Separate Queries Per Type)**
```python
# User has to know each type and query separately
regular = phonRuleOps.GetAll(class_type='PhRegularRule')
metathesis = phonRuleOps.GetAll(class_type='PhMetathesisRule')
redup = phonRuleOps.GetAll(class_type='PhReduplicationRule')

# Manually filter each type
voicing_regular = [r for r in regular if 'voic' in r.name.lower()]
voicing_metathesis = [r for r in metathesis if 'voic' in r.name.lower()]
voicing_redup = [r for r in redup if 'voic' in r.name.lower()]

# Combine results
voicing_all = voicing_regular + voicing_metathesis + voicing_redup
```

**NEW API (Unified Filtering)**
```python
# Simple, unified query - type is transparent
voicing_rules = phonRuleOps.GetAll().filter(name_contains='voicing')

# Results naturally show type diversity
print(voicing_rules)
# Phonological Rules Summary (3 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   2 rules ( 66.7%)
#   PhMetathesisRule        :   1 rule  ( 33.3%)
```

---

### Scenario 4: Merge Different Types

**OLD API (Hard Error)**
```python
rule1 = phonRuleOps.Find("rule1")  # PhRegularRule
rule2 = phonRuleOps.Find("rule2")  # PhMetathesisRule

# Crashes with error - user doesn't understand why
try:
    phonRuleOps.MergeObject(rule1, rule2)
except FP_ParameterError as e:
    print(f"ERROR: {e}")
    # User is stuck - what does this error mean?
```

**NEW API (Informative Warning, User in Control)**
```python
rule1 = phonRuleOps.Find("rule1")  # PhRegularRule
rule2 = phonRuleOps.Find("rule2")  # PhMetathesisRule

# Gives user information, asks permission
result = phonRuleOps.MergeObject(rule1, rule2)

# ⚠️  WARNING: Merging different rule types
#
# ├─ Survivor: "rule1" (PhRegularRule)
# └─ Victim:   "rule2" (PhMetathesisRule)
#
# Properties will be merged as follows:
# ├─ Common Properties (will merge):
# │  ├─ Name
# │  ├─ Description
# │  ├─ StrucDescOS
# │  └─ Direction
# │
# ├─ Type-Specific to Survivor (preserved):
# │  └─ PhRegularRule.RightHandSidesOS
# │
# └─ Type-Specific to Victim (will be lost):
#    ├─ LeftPartOfMetathesisOS
#    └─ RightPartOfMetathesisOS
#
# Continue with merge? (y/n): n
# → Merge cancelled by user

# Or force it for scripts:
result = phonRuleOps.MergeObject(rule1, rule2, force=True)
```

---

### Scenario 5: Iterate and Work With Rules

**OLD API (Type-Aware Iteration)**
```python
rules = phonRuleOps.GetAll()

for rule in rules:
    # User has to think about types
    class_type = rule.ClassName

    if class_type == 'PhRegularRule':
        from SIL.LCModel import IPhRegularRule
        concrete = IPhRegularRule(rule)
        print(f"{rule.Name}: {concrete.RightHandSidesOS.Count} outputs")

    elif class_type == 'PhMetathesisRule':
        # Different properties entirely
        print(f"{rule.Name}: metathesis rule")

    # Exhausting and error-prone
```

**NEW API (Natural Iteration)**
```python
rules = phonRuleOps.GetAll()

for rule in rules:
    # User doesn't think about types
    print(f"{rule.name} ({rule.class_type})")

    # These work for any type
    print(f"  Inputs: {len(rule.input_contexts)}")

    # Smart check
    if rule.has_output_specs:
        print(f"  Outputs: {len(rule.output_specs)}")

    if rule.has_metathesis_parts:
        print(f"  Type: metathesis")

    # Simple and elegant
```

---

## Key Differences

### OLD API (Technical Mindset)
| Aspect | Approach |
|--------|----------|
| **Abstraction** | Expose all technical details |
| **Type Handling** | User must manage different types |
| **Errors** | Hard stops (exceptions) |
| **Properties** | Access by exact name (fails if doesn't exist) |
| **Filtering** | Separate query per type |
| **Design Pattern** | "Here's the technology, figure it out" |

### NEW API (User Mindset)
| Aspect | Approach |
|--------|----------|
| **Abstraction** | Hide complexity, expose natural concepts |
| **Type Handling** | System manages types transparently |
| **Warnings** | Informative warnings, user in control |
| **Properties** | Smart access (returns what exists) |
| **Filtering** | Unified queries across types |
| **Design Pattern** | "Here's what you need, we manage the complexity" |

---

## The "Dual Thinking" Principle

Users naturally think at two levels simultaneously:

```
Level 1: ABSTRACT (Conceptual)
"I need phonological rules"
"I need to filter rules with 'voicing' in the name"
"I want to merge these rules"

Level 2: CONCRETE (Practical)
"These are different types of rules"
"Some rules have outputs, some don't"
"If I merge unlike types, what gets lost?"
```

**OLD API forces:**
- User consciously manages Level 2 (Technical)
- Distracts from Level 1 (Business Logic)
- Error-prone: easy to forget casting, checking types

**NEW API supports:**
- User works naturally at Level 1 (Business Logic)
- System handles Level 2 (Technical) transparently
- Type information available when needed without forcing it

---

## Implementation Strategy

### Phase 1: Wrapper Classes (Immediate)
```python
class PhonologicalRule:
    # Wraps IPhSegmentRule, provides unified interface
    # Auto-routes property access to concrete type
```

### Phase 2: Smart Collections (Immediate)
```python
class RuleCollection:
    # Shows type diversity on display
    # Provides unified filtering
    # Supports iteration without type awareness
```

### Phase 3: Merge Warnings (Short Term)
```python
class MergeWarning:
    # Detailed reporting on type mismatches
    # Informative, not punitive
```

### Phase 4: Documentation (Short Term)
```python
# Guide: "Working with Objects that Have Multiple Types"
# Type hierarchy diagrams
# Common patterns and workflows
```

---

## Benefits Realized

| Benefit | Impact |
|---------|--------|
| **Reduced Cognitive Load** | Users think about business logic, not interfaces |
| **Fewer Errors** | No AttributeError from forgotten casting |
| **Better Discoverability** | IDE autocomplete shows what's available |
| **Clearer Intent** | Code reads like what user actually wants to do |
| **Educational** | Users learn type structure through warnings, not crashes |
| **Scalable** | Pattern works for any multi-type scenario |

---

## Examples of Scalability

This pattern applies beyond phonological rules:

```python
# MSAs (morphosyntactic analyses) - same pattern
analyses = lexEntryOps.GetAll()
# Shows: MoStemMsa (5), MoDerivAffMsa (3), MoInflAffMsa (2)

# Contexts - same pattern
contexts = environOps.GetAll()
# Shows type diversity naturally

# Any object with multiple concrete implementations
# Uses same design pattern automatically
```

---

## Comparison to Industry Standards

### How Other Libraries Handle This

**Doctrine ORM (PHP)** - Forces type awareness
```php
$results = $repo->findAll();  // Returns base type
foreach ($results as $obj) {
    if ($obj instanceof SpecificType) {
        // User must check type
    }
}
```

**SQLAlchemy (Python)** - Polymorphic querying
```python
results = session.query(BaseClass).all()
# Returns all subtypes mixed together
# User must check type or cast
```

**Entity Framework (C#)** - Navigation properties
```csharp
var results = context.BaseEntities.ToList();
// Type is preserved in C#, but user must know about subtypes
```

**FlexLibs2 (NEW)** - Transparent type management
```python
results = ops.GetAll()  # Returns smart collection
# Type diversity shown, filtering unified
# Properties work transparently across types
```

---

## Summary: Philosophy in Action

**Old Philosophy:**
> "The system exposes complexity. Users must understand interfaces, ClassName, casting, and type-specific properties."

**New Philosophy:**
> "The system hides complexity. Users think about what they want to do. The system understands the types underneath and provides what's needed."

This is the difference between:
- Making users experts in the **technology**
- Making users productive at their **business logic**

