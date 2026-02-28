# User-Centric API Design: Hiding Complexity, Maximizing Functionality

**Date:** 2026-02-27
**Philosophy:** Users think in abstractions (phonological rules, morphosyntactic analyses) while the system manages the concrete complexity underneath. The API should match how users naturally think.

---

## Core Design Principle

**Users should never need to know about interfaces, ClassName, or casting.**

Instead:
1. ✅ Ask for "all phonological rules" → get ALL subtypes with type summary
2. ✅ Try to merge PhRegularRule into PhMetathesisRule → get WARNING, not error
3. ✅ Filter rules by "Name contains 'voicing'" → works across ALL rule types
4. ✅ See results → includes type information naturally

---

## Design 1: Smart GetAll() with Type Summary

### Current API (Forces User to Think About Types)
```python
# User has to think: "What do I want? All rules? What types exist?"
regular_rules = phonRuleOps.GetAll(class_type='PhRegularRule')
metathesis_rules = phonRuleOps.GetAll(class_type='PhMetathesisRule')
```

### Improved API (Matches How Users Think)
```python
# User asks naturally: "Give me all rules"
all_rules = phonRuleOps.GetAll()

# Returns a RuleCollection with built-in type awareness
print(all_rules)
# Output:
# ╔════════════════════════════════════════════════════════════════╗
# ║ Phonological Rules Summary (12 rules)                          ║
# ├────────────────────────────────────────────────────────────────┤
# │ PhRegularRule           : 7 rules (58%)                         │
# │ PhMetathesisRule        : 3 rules (25%)                         │
# │ PhReduplicationRule     : 2 rules (17%)                         │
# ╚════════════════════════════════════════════════════════════════╝

# Iteration works naturally - user doesn't think about types
for rule in all_rules:
    print(f"{rule.name} ({rule.class_type})")

# Can access any property without thinking about casting
for rule in all_rules:
    inputs = rule.input_contexts  # Works for ANY rule type
    outputs = rule.output_specs   # Works for ANY rule type
```

### Implementation

```python
class RuleCollection:
    """
    Smart collection that shows type diversity without overwhelming the user.

    Appears as a simple list, but internally manages multiple concrete types.
    """

    def __init__(self, rules):
        self.rules = list(rules)
        self._by_type = self._group_by_type()

    def _group_by_type(self):
        """Group rules by ClassName internally."""
        by_type = {}
        for rule in self.rules:
            class_type = rule.ClassName
            if class_type not in by_type:
                by_type[class_type] = []
            by_type[class_type].append(rule)
        return by_type

    def __str__(self):
        """Show type summary on display."""
        lines = [f"Phonological Rules Summary ({len(self.rules)} rules)"]
        lines.append("─" * 60)

        for class_type, rules in sorted(self._by_type.items()):
            pct = 100 * len(rules) / len(self.rules)
            lines.append(f"  {class_type:20s}: {len(rules):3d} rules ({pct:5.1f}%)")

        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        """Iterate naturally - user doesn't think about types."""
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def by_type(self, class_type):
        """Filter to specific type if user wants."""
        return RuleCollection(self._by_type.get(class_type, []))

    def regular_rules(self):
        """Convenience filters for common types."""
        return self.by_type('PhRegularRule')

    def metathesis_rules(self):
        return self.by_type('PhMetathesisRule')

    def replication_rules(self):
        return self.by_type('PhReduplicationRule')


class PhonologicalRuleOperations(BaseOperations):

    def GetAll(self):
        """
        Get all phonological rules.

        Returns RuleCollection that:
        - Shows type summary on display
        - Allows natural iteration (user doesn't think about types)
        - Provides type filtering if user wants it

        User can work at abstract level (all rules) or concrete level
        (specific types) without knowing about interfaces.
        """
        rules = self.project.lp.PhonologicalDataOA.PhonRulesOS
        return RuleCollection([PhonologicalRule(r) for r in rules])
```

### User Experience

```python
# Simple query matches natural thinking
rules = phonRuleOps.GetAll()

# Display shows type diversity without overwhelming
print(rules)
# Phonological Rules Summary (12 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   7 rules ( 58.3%)
#   PhMetathesisRule        :   3 rules ( 25.0%)
#   PhReduplicationRule     :   2 rules ( 16.7%)

# Iterate - no type awareness needed
for rule in rules:
    if rule.has_output_specs:  # Works for any type
        do_something(rule.output_specs)

# Filter if needed - but it's optional
regular_only = rules.regular_rules()
for rule in regular_only:
    # Still have access to all properties
    print(rule.output_specs)
```

---

## Design 2: Smart Merge with Warnings Not Errors

### Current API (Fails Silently or Throws Error)
```python
rule1 = phonRuleOps.Find("rule1")  # PhRegularRule
rule2 = phonRuleOps.Find("rule2")  # PhMetathesisRule

# ERROR! Crashes and burns
phonRuleOps.MergeObject(rule1, rule2)
# FP_ParameterError: Cannot merge different classes
```

### Improved API (Smart Warning, User in Control)
```python
rule1 = phonRuleOps.Find("rule1")  # PhRegularRule
rule2 = phonRuleOps.Find("rule2")  # PhMetathesisRule

# Gives user information, asks permission
result = phonRuleOps.MergeObject(rule1, rule2)

# Output shows what's happening:
# ⚠️  WARNING: Merging different rule types
# ├─ Survivor: "rule1" (PhRegularRule)
# └─ Victim:   "rule2" (PhMetathesisRule)
#
# Properties will be merged as follows:
# ├─ Common Properties (will merge):
# │  ├─ Name
# │  ├─ Description
# │  ├─ StrucDescOS (input contexts)
# │  └─ Direction
# │
# ├─ Type-Specific Properties (will NOT merge):
# │  ├─ PhRegularRule.RightHandSidesOS (present in survivor only)
# │  └─ PhMetathesisRule.LeftPartOfMetathesisOS (lost in victim)
# │
# └─ Result: Merged entry will be PhRegularRule with common properties
#
# Continue? (y/n): [User decides]
```

### Implementation

```python
class MergeWarning:
    """
    Provides detailed merge information without being an error.
    Lets user make informed decision.
    """

    def __init__(self, survivor, victim):
        self.survivor = survivor
        self.victim = victim
        self.survivor_type = survivor.ClassName
        self.victim_type = victim.ClassName

    def is_type_mismatch(self):
        """Check if merging different types."""
        return self.survivor_type != self.victim_type

    def get_common_properties(self):
        """Find properties available on both types."""
        survivor_props = set(dir(self.survivor._concrete))
        victim_props = set(dir(self.victim._concrete))
        return survivor_props & victim_props

    def get_survivor_only_properties(self):
        """Properties only on survivor type."""
        survivor_props = set(dir(self.survivor._concrete))
        victim_props = set(dir(self.victim._concrete))
        return survivor_props - victim_props

    def get_victim_only_properties(self):
        """Properties only on victim type (will be lost)."""
        survivor_props = set(dir(self.survivor._concrete))
        victim_props = set(dir(self.victim._concrete))
        return victim_props - survivor_props

    def print_report(self):
        """Show user what will happen."""
        print(f"\n⚠️  WARNING: Merging different rule types\n")
        print(f"├─ Survivor: \"{self.survivor.name}\" ({self.survivor_type})")
        print(f"└─ Victim:   \"{self.victim.name}\" ({self.victim_type})\n")

        print("Properties will be merged as follows:")

        common = self.get_common_properties()
        if common:
            print("├─ Common Properties (will merge):")
            for prop in sorted(common)[:5]:  # Show first 5
                print(f"│  ├─ {prop}")
            if len(common) > 5:
                print(f"│  └─ ... and {len(common) - 5} more")

        survivor_only = self.get_survivor_only_properties()
        if survivor_only:
            print("├─ Type-Specific to Survivor (preserved):")
            for prop in sorted(survivor_only)[:3]:
                print(f"│  ├─ {prop}")
            if len(survivor_only) > 3:
                print(f"│  └─ ... and {len(survivor_only) - 3} more")

        victim_only = self.get_victim_only_properties()
        if victim_only:
            print("└─ Type-Specific to Victim (will be lost):")
            for prop in sorted(victim_only)[:3]:
                print(f"   ├─ {prop}")
            if len(victim_only) > 3:
                print(f"   └─ ... and {len(victim_only) - 3} more")

        print()


class PhonologicalRuleOperations(BaseOperations):

    def MergeObject(self, survivor_or_hvo, victim_or_hvo, force=False):
        """
        Merge victim into survivor.

        If types don't match, shows detailed warning but ALLOWS merge
        (doesn't crash with error). User can inspect the report and decide.

        Args:
            survivor_or_hvo: Rule to keep
            victim_or_hvo: Rule to merge into survivor
            force: If True, merge without asking (for scripting)

        Returns:
            survivor object with merged data
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(survivor_or_hvo, "survivor_or_hvo")
        self._ValidateParam(victim_or_hvo, "victim_or_hvo")

        survivor = self.__ResolveObject(survivor_or_hvo)
        victim = self.__ResolveObject(victim_or_hvo)

        # Check for type mismatch - warn but don't error
        warning = MergeWarning(survivor, victim)

        if warning.is_type_mismatch():
            warning.print_report()

            if not force:
                response = input("Continue with merge? (y/n): ").lower().strip()
                if response != 'y':
                    logger.info("Merge cancelled by user")
                    return None
            else:
                logger.warning(f"Merging {warning.victim_type} into {warning.survivor_type} (forced)")

        # Proceed with merge - LibLCM handles the actual merge
        logger.info(f"Merging rule (HVO: {victim.Hvo}) into survivor (HVO: {survivor.Hvo})")
        survivor._obj.MergeObject(victim._obj, fLoseNoStringData=True)

        return survivor
```

### User Experience

```python
# Try to merge different types
result = phonRuleOps.MergeObject(regular_rule, metathesis_rule)

# Gets informative report, user can decide
# ⚠️  WARNING: Merging different rule types
#
# ├─ Survivor: "Voicing" (PhRegularRule)
# └─ Victim:   "Metathesis" (PhMetathesisRule)
#
# Properties will be merged as follows:
# ├─ Common Properties (will merge):
# │  ├─ Name
# │  ├─ Description
# │  ├─ StrucDescOS
# │  └─ Direction
# │
# └─ Type-Specific to Victim (will be lost):
#    ├─ LeftPartOfMetathesisOS
#    └─ RightPartOfMetathesisOS
#
# Continue with merge? (y/n): n
# → Merge cancelled by user

# Or force it for scripts:
result = phonRuleOps.MergeObject(rule1, rule2, force=True)
# → Merges without asking
```

---

## Design 3: Unified Filtering Across Types

### Current API (Separate Queries Per Type)
```python
# User has to query each type separately
regular = phonRuleOps.GetAll(class_type='PhRegularRule')
metathesis = phonRuleOps.GetAll(class_type='PhMetathesisRule')

# Then manually combine results
all_voicing = [r for r in regular if 'voic' in r.name.lower()] + \
             [r for r in metathesis if 'voic' in r.name.lower()]
```

### Improved API (Filter Across All Types Transparently)
```python
# Simple, unified query - type is transparent
voicing_rules = phonRuleOps.GetAll().filter(name_contains='voicing')

# Works for any common property across all rule types
# Results show the type diversity
print(voicing_rules)
# Phonological Rules Summary (3 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   2 rules ( 66.7%)
#   PhMetathesisRule        :   1 rule  ( 33.3%)

for rule in voicing_rules:
    print(f"{rule.name} ({rule.class_type})")
```

### Implementation

```python
class RuleCollection:
    """
    Smart collection with filtering across all types.
    """

    def filter(self, **criteria):
        """
        Filter by common properties (works across all rule types).

        Args:
            name_contains: Filter name by substring
            direction: Filter by direction (if available)
            stratum: Filter by stratum (if available)
        """
        results = self.rules

        if 'name_contains' in criteria:
            pattern = criteria['name_contains'].lower()
            results = [r for r in results
                      if pattern in r.name.lower()]

        if 'direction' in criteria:
            direction = criteria['direction']
            results = [r for r in results
                      if hasattr(r, 'Direction') and r.Direction == direction]

        if 'stratum' in criteria:
            stratum = criteria['stratum']
            results = [r for r in results
                      if hasattr(r, 'StratumRA') and r.StratumRA == stratum]

        return RuleCollection(results)

    def where(self, predicate):
        """
        Advanced filtering with custom predicate.
        """
        return RuleCollection([r for r in self.rules if predicate(r)])
```

### User Experience

```python
# Simple, unified queries
rules = phonRuleOps.GetAll()

# Filter by common property (works for all types)
voicing = rules.filter(name_contains='voicing')

# Complex filtering (user thinks in business logic, not types)
complex_rules = rules.where(lambda r:
    r.input_contexts > 2 and
    'consonant' in r.name.lower()
)

# Results naturally show type diversity
print(complex_rules)
# Phonological Rules Summary (5 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   3 rules ( 60.0%)
#   PhMetathesisRule        :   2 rules ( 40.0%)
```

---

## Design 4: Properties That Work Across Types

### Current API (Type-Specific Property Names)
```python
rule = phonRuleOps.Find("something")

# Different properties per type - user has to know
if rule.class_type == 'PhRegularRule':
    outputs = rule.RightHandSidesOS
elif rule.class_type == 'PhMetathesisRule':
    # Metathesis rules don't have RightHandSidesOS!
    outputs = None
```

### Improved API (Unified Property Access)
```python
rule = phonRuleOps.Find("something")

# Works for ANY rule type - returns what exists
outputs = rule.output_segments  # Smart property

# OR check what properties exist
if rule.has_output_specs:
    do_something(rule.output_specs)

if rule.has_metathesis_parts:
    do_something(rule.metathesis_parts)
```

### Implementation

```python
class PhonologicalRule:
    """
    Wrapper that provides unified interface while respecting type differences.
    """

    # Properties that work for ALL rule types
    @property
    def name(self):
        """Rule name (all types)."""
        return self._obj.Name.BestAnalysisAlternative.Text

    @property
    def input_contexts(self):
        """Input contexts (all types)."""
        return list(self._concrete.StrucDescOS)

    # Smart property - returns what exists
    @property
    def output_segments(self):
        """
        Output segments (type-aware).

        For PhRegularRule: RightHandSidesOS
        For PhMetathesisRule: MetathesisOutputs (if exists)
        For PhReduplicationRule: None (no outputs in same way)
        For others: None
        """
        if hasattr(self._concrete, 'RightHandSidesOS'):
            return list(self._concrete.RightHandSidesOS)
        return []

    # Type capability checks
    @property
    def has_output_specs(self):
        """Does this rule type have output specifications?"""
        return hasattr(self._concrete, 'RightHandSidesOS')

    @property
    def has_metathesis_parts(self):
        """Does this rule type have metathesis parts?"""
        return hasattr(self._concrete, 'LeftPartOfMetathesisOS')

    @property
    def has_reduplication_parts(self):
        """Does this rule type have reduplication parts?"""
        return hasattr(self._concrete, 'LeftPartOfReduplicationOS')

    # Type-specific access (if user knows the type)
    def get_property(self, name):
        """
        Get any property safely (returns None if doesn't exist).

        Useful for advanced users who know the type.
        """
        try:
            return getattr(self._concrete, name)
        except AttributeError:
            return None
```

### User Experience

```python
for rule in phonRuleOps.GetAll():
    # These work for any rule type
    print(f"{rule.name}: {len(rule.input_contexts)} inputs")

    if rule.has_output_specs:
        print(f"  Output specs: {len(rule.output_specs)}")

    if rule.has_metathesis_parts:
        print(f"  Metathesis rule")

    if rule.has_reduplication_parts:
        print(f"  Reduplication rule")

# No checking ClassName, no manual casting
# User thinks: "Does this rule have what I need?"
# Not: "What concrete type is this?"
```

---

## Complete User-Centric API

```python
# ═════════════════════════════════════════════════════════════════
# Get All - Natural Abstraction Level
# ═════════════════════════════════════════════════════════════════

rules = phonRuleOps.GetAll()

# Display shows type diversity without overwhelming
print(rules)
# Phonological Rules Summary (12 rules)
# ─────────────────────────────────────
#   PhRegularRule           :   7 rules ( 58.3%)
#   PhMetathesisRule        :   3 rules ( 25.0%)
#   PhReduplicationRule     :   2 rules ( 16.7%)


# ═════════════════════════════════════════════════════════════════
# Filter - Works Across All Types
# ═════════════════════════════════════════════════════════════════

voicing_rules = rules.filter(name_contains='voicing')

consonant_rules = rules.where(
    lambda r: len(r.input_contexts) >= 2
)


# ═════════════════════════════════════════════════════════════════
# Access Properties - Type-Aware But Transparent
# ═════════════════════════════════════════════════════════════════

for rule in voicing_rules:
    # These work for ANY type
    print(f"{rule.name} ({rule.class_type})")
    print(f"  Inputs: {len(rule.input_contexts)}")

    # Smart property returns what exists
    if rule.output_segments:
        print(f"  Outputs: {len(rule.output_segments)}")

    # Or check capabilities
    if rule.has_metathesis_parts:
        print(f"  This is a metathesis rule")


# ═════════════════════════════════════════════════════════════════
# Merge - Smart Warnings, User in Control
# ═════════════════════════════════════════════════════════════════

# Merging same type: no warning
result = phonRuleOps.MergeObject(rule1, rule2)
# ✅ Merged successfully

# Merging different types: gets warning
result = phonRuleOps.MergeObject(regular_rule, metathesis_rule)
# ⚠️  WARNING: Merging different rule types
# (Shows what will happen, asks user)
# Continue? (y/n):


# ═════════════════════════════════════════════════════════════════
# Optional: Type-Specific Operations (If User Wants)
# ═════════════════════════════════════════════════════════════════

regular_only = rules.regular_rules()
# Now user explicitly chose to work with one type
for rule in regular_only:
    # Safe to use PhRegularRule-specific properties
    for rhs in rule.RightHandSidesOS:
        print(rhs.Guid)
```

---

## Design Principles Embodied

✅ **Reduce Complexity**
- No interface/ClassName/casting visible to user
- Work at natural abstraction level (all rules, common properties)

✅ **Maximize Functionality**
- GetAll() returns meaningful type summary
- Filter works across all types
- Properties work intelligently

✅ **Dual Thinking**
- User thinks "phonological rules" (abstract) AND "these are different types" (concrete)
- API supports both simultaneously without forcing user to manage it

✅ **Smart Warnings**
- Merge unlike objects → warning + info, not error
- User stays in control, gets education

✅ **Natural Language**
- `.filter(name_contains='voicing')` not `.filter_by_property_value('Name', 'voicing')`
- `.has_output_specs` not `if rule.ClassName == 'PhRegularRule'`
- Matches how users naturally think

✅ **Transparent Type Management**
- System manages types internally
- User doesn't think about them
- But information is available when needed

