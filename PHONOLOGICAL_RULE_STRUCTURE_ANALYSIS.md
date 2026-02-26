# Phonological Rule "a neutralization" - Comprehensive LCM Structure Analysis

## Overview

Analyzed the "a neutralization" phonological rule from the Test FieldWorks project to understand how rule formulas (input, output, contexts) are stored in the LCM.

## Rule Basic Information

- **Rule Name**: a neutralization
- **HVO**: 13203
- **ClassName**: PhRegularRule
- **Direction**: 0 (left-to-right)
- **Disabled**: False

## LCM Storage Structure

### 1. Root Rule Object (PhRegularRule)

The phonological rule itself is stored as a **PhRegularRule** object with:
- **Properties**: Name, Description (both MultiUnicodeAccessor/MultiStringAccessor objects, NOT direct strings)
- **OwnedObjects**: 2 items (see below)
- **StrucDescOS**: Structure description objects (input and context) - accessed via `rule.StrucDescOS`
- **RightHandSidesOS**: Right-hand side objects (not directly accessible, but children exist in OwnedObjects)

### 2. OwnedObjects Structure

The rule has exactly **2 OwnedObjects**:

```
PhRegularRule (HVO: 13203)
├── [0] PhSegRuleRHS (HVO: 6777)
│   ├── [0] PhSimpleContextSeg (HVO: 4429)  [OUTPUT SEGMENT]
│   ├── [1] PhSimpleContextBdry (HVO: 11292) [OUTPUT BOUNDARY]
│   └── [2] PhSimpleContextNC (HVO: 14809)   [OUTPUT NATURAL CLASS]
│
└── [1] PhSimpleContextSeg (HVO: 16756)  [INPUT SEGMENT / STRUCTURE DESCRIPTION]
```

### 3. Component Breakdown

#### Component 0: PhSegRuleRHS (RIGHT-HAND SIDE - OUTPUT)
- **HVO**: 6777
- **ClassName**: PhSegRuleRHS
- **Purpose**: Contains the output specification of the rule
- **Owner**: PhRegularRule (HVO: 13203)
- **OwningFlid**: 5129001 (RHS field identifier)
- **OwnedObjects**: 3 items (output elements)

##### Output Elements (children of PhSegRuleRHS):

**[0] PhSimpleContextSeg (HVO: 4429)**
- **Type**: Output segment element
- **OwningFlid**: 5131001 (segment field)
- **Properties**:
  - `FeatureStructureRA`: Currently None (unset in test data - would reference a phoneme/feature)
  - `IndexInOwner`: -1
- **Role**: When set, would reference a phoneme or feature structure that is the output

**[1] PhSimpleContextBdry (HVO: 11292)**
- **Type**: Output boundary element
- **OwningFlid**: 5131002 (boundary field)
- **Properties**:
  - `BoundaryMarkerRA`: Would reference a boundary marker (e.g., word boundary, syllable boundary)
  - `IndexInOwner`: -1
- **Role**: Specifies a boundary condition in the output

**[2] PhSimpleContextNC (HVO: 14809)**
- **Type**: Output natural class element
- **OwningFlid**: 5131003 (natural class field)
- **Properties**:
  - `NatlClassRA`: Would reference a natural class
  - `IndexInOwner`: 0 (ordered)
- **Role**: Specifies a natural class as part of the output

#### Component 1: PhSimpleContextSeg (INPUT/STRUCTURE DESCRIPTION)
- **HVO**: 16756
- **ClassName**: PhSimpleContextSeg
- **Purpose**: The input specification (structure description) of the rule
- **Owner**: PhRegularRule (HVO: 13203)
- **OwningFlid**: 5128006 (structure description field)
- **Properties**:
  - `FeatureStructureRA`: Currently None (unset in test data - would reference what input transforms)
  - `LeftContextOA`: Would specify left context environment
  - `RightContextOA`: Would specify right context environment
  - `IndexInOwner`: 0

## Reference Properties Structure

### How References Work

In FlexLibs2/LCM, rule formulas reference phonemes, natural classes, and boundaries:

```python
# Setting properties (as shown in PhonologicalRuleOperations.py):
output_seg.FeatureStructureRA = phoneme_or_class  # References a phoneme/feature
left_ctx.FeatureStructureRA = context_item        # References context
nc.NatlClassRA = natural_class                    # References natural class
```

### Property Naming Convention

- **RA** suffix: Single owned reference (object or None)
- **RC** suffix: Reference collection (multiple objects)
- **OS** suffix: Owned sequence (children owned by this object)

### For PhSimpleContextSeg:
- `FeatureStructureRA`: References the phoneme/feature this segment represents

### For PhSimpleContextNC:
- `NatlClassRA`: References the natural class

### For PhSimpleContextBdry:
- `BoundaryMarkerRA`: References the boundary marker type

## Data Flow in Test Rule

The test data shows the structure but with unset references:

```
Input Transformation:
  PhSimpleContextSeg (HVO: 16756)
    └── FeatureStructureRA: None (would point to /a/)
        ├── LeftContextOA: None (no left context specified)
        └── RightContextOA: None (no right context specified)

Output Specification:
  PhSegRuleRHS (HVO: 6777)
    ├── PhSimpleContextSeg (HVO: 4429) FeatureStructureRA: None (would be /ə/ or similar)
    ├── PhSimpleContextBdry (HVO: 11292) BoundaryMarkerRA: None
    └── PhSimpleContextNC (HVO: 14809) NatlClassRA: None
```

## Key Findings

1. **OwnedObjects Structure**: The rule's immediate OwnedObjects contain both the output (RHS) and input (StrucDesc), not in separate container objects.

2. **Hierarchy is Shallow**:
   - PhRegularRule owns PhSegRuleRHS and PhSimpleContextSeg directly
   - PhSegRuleRHS owns its context elements (PhSimpleContextSeg, PhSimpleContextBdry, PhSimpleContextNC)
   - No deeper nesting beyond this

3. **Context Storage**: Left and right contexts are stored as:
   - `LeftContextOA`: Single owned object (PhSimpleContextSeg or similar)
   - `RightContextOA`: Single owned object
   - These are properties OF the input PhSimpleContextSeg, not separate OwnedObjects

4. **No StrucChangeOS**: Despite code references to `StrucChangeOS`, this property does not exist on PhSegRuleRHS in our test data. The output elements are stored directly in `OwnedObjects`.

5. **References Are Lazy**: The test data shows references not yet set (`FeatureStructureRA` returns None). These would be filled in when the rule is fully configured.

## Implementation Notes for FlexLibs2

When creating or modifying phonological rules:

1. Access RHS objects via `rule.OwnedObjects` (not `RightHandSidesOS` which may not be accessible)
2. Access input via `rule.StrucDescOS`
3. Set segment references: `obj.FeatureStructureRA = phoneme_or_class`
4. Set natural class references: `nc_obj.NatlClassRA = natural_class`
5. Set boundary references: `bdry_obj.BoundaryMarkerRA = boundary_marker`
6. Add contexts: `input_obj.LeftContextOA = left_ctx`, `input_obj.RightContextOA = right_ctx`

## Property Access Patterns

**NOT**:
```python
rule.LeftContextOA  # PhRegularRule doesn't have this - it's on the input segment
rule.RightContextOA # Same
```

**YES**:
```python
input_seg = list(rule.StrucDescOS)[0]
input_seg.LeftContextOA  # PhSimpleContextSeg has this
input_seg.RightContextOA # PhSimpleContextSeg has this
```

## HVO Reference Summary

| Object | HVO | Type | Purpose |
|--------|-----|------|---------|
| Rule | 13203 | PhRegularRule | Main rule container |
| RHS | 6777 | PhSegRuleRHS | Output specification container |
| Output Seg | 4429 | PhSimpleContextSeg | Output segment/feature |
| Output Bdry | 11292 | PhSimpleContextBdry | Output boundary |
| Output NC | 14809 | PhSimpleContextNC | Output natural class |
| Input | 16756 | PhSimpleContextSeg | Input/structure description |
