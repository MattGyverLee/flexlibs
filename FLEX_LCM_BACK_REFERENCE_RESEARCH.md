# FLEx LCM Back-Reference Properties Research Report

## Overview
This document details the implementation of back-reference properties in FLEx LCM:
1. VisibleComplexFormBackRefs (ILexEntry, ILexSense)
2. ComplexFormsNotSubentries (ILexEntry, ILexSense) 
3. MinimalLexReferences (ILexSense, ILexEntry)
4. AllSenses (ILexEntry - recursive subsenses)

Source: D:/Github/liblcm/src/SIL.LCModel/DomainImpl/OverridesLing_Lex.cs (10,147 lines)

---

## 1. VisibleComplexFormBackRefs

### Purpose
Returns all LexEntryRef objects that refer to this entry/sense in ShowComplexFormsIn field and are complex forms (RefType == krtComplexForm).

### For LexEntry (lines 1075-1090)
Returns IEnumerable<ILexEntryRef> via:
1. ComplexFormRefsVisibleInThisEntry (internal helper)
2. Calls EnsureCompleteIncomingRefsFrom(LexEntryRefTags.kflidShowComplexFormsIn)
3. Iterates m_incomingRefs, filters by Flid and RefType
4. Applies VirtualOrderingServices for user customization
5. Sorts via LexEntryRefRepository.SortEntryRefs()

### For LexSense (lines 4738-4746)
Same implementation pattern using:
- ComplexFormRefsVisibleInThisSense helper
- LexSenseVisibleComplexFormBackRefs FLID

### Key LCM API Calls
- EnsureCompleteIncomingRefsFrom(LexEntryRefTags.kflidShowComplexFormsIn)
- LexEntryRefTags.krtComplexForm (RefType constant)
- Virtuals.LexEntryVisibleComplexFormBackRefs
- Virtuals.LexSenseVisibleComplexFormBackRefs

---

## 2. ComplexFormsNotSubentries

### Purpose
Filtered subset of VisibleComplexFormBackRefs excluding subentries.

### For LexEntry (lines 1092-1099)
```
return VisibleComplexFormBackRefs.Where(ler => !ler.PrimaryLexemesRS.Contains(this))
```

### For LexSense (lines 4748-4755)
Same logic applied to VisibleComplexFormBackRefs

### Key Property
- ILexEntryRef.PrimaryLexemesRS - Used to check if in subentry collection

---

## 3. MinimalLexReferences

### Purpose
Returns only essential LexReferences - filtered by mapping type and target count.

### For LexEntry (lines 2406-2415)
```
EnsureCompleteIncomingRefsFrom(LexReferenceTags.kflidTargets)
return DomainObjectServices.ExtractMinimalLexReferences(m_incomingRefs)
```

### For LexSense (lines 5011-5020)
Same pattern using EnsureCompleteIncomingRefsFrom

### Filtering Criteria (from DomainObjectServices)
References included if:
- TargetsRS.Count > 1 (multi-target), OR
- MappingType is one of:
  - kmtSenseSequence
  - kmtEntrySequence  
  - kmtEntryOrSenseSequence

### Key LCM API Calls
- EnsureCompleteIncomingRefsFrom(LexReferenceTags.kflidTargets)
- DomainObjectServices.ExtractMinimalLexReferences()

---

## 4. AllSenses (Recursive)

### Purpose
Returns all senses owned by entry/sense, including subsenses recursively.

### For LexEntry (lines 2407-2420)
```
var senses = new List<ILexSense>()
foreach (var ls in SensesOS)
    senses.AddRange(ls.AllSenses)  // Recursive call
return senses
```

### For LexSense (lines 5019-5030)
```
var senses = new List<ILexSense>()
senses.Add(this)  // Include self
foreach (var ls in SensesOS)
    senses.AddRange(ls.AllSenses)  // Recursive call
return senses
```

### Recursion Pattern
```
LexEntry.AllSenses
  LexSense[1].AllSenses (includes self)
    LexSense[1.1].AllSenses (includes self)
      LexSense[1.1.1].AllSenses
    LexSense[1.2].AllSenses
  LexSense[2].AllSenses
```

### Related Property
- LexEntry.NumberOfSensesForEntry (cached count of AllSenses.Count)

---

## Implementation Details: Back-Reference Resolution

### Incoming References Collection (lines 958-975)
All back-reference properties use similar pattern:

1. Call EnsureCompleteIncomingRefsFrom(fieldId) to load refs
2. Iterate m_incomingRefs (SimpleBag collection)
3. Cast items to LcmReferenceSequence<ICmObject>
4. Filter by Flid and RefType
5. Return filtered ILexEntryRef objects

### Virtual Ordering Service
After collecting back-refs:
- Call VirtualOrderingServices.GetOrderedValue()
- Provides user-customizable ordering
- Uses Flid to identify virtual property
- Applies LexEntryRefRepository.SortEntryRefs()

---

## Key Constants

From LexEntryRefTags:
- kflidShowComplexFormsIn - Field ID for ShowComplexFormsIn
- krtComplexForm - RefType constant for complex forms (value: 1)

From LexReferenceTags:
- kflidTargets - Field ID for Targets

---

## Architecture Insights

### Virtual Properties Pattern
All use [VirtualProperty] attribute:
```
[VirtualProperty(CellarPropertyType.ReferenceSequence, "LexEntryRef")]
public IEnumerable<ILexEntryRef> VisibleComplexFormBackRefs { get; }
```

### Incoming References
Maintained in m_incomingRefs (from CmObject base class)
- SimpleBag<IReferenceSource> collection
- Loaded on-demand via EnsureCompleteIncomingRefsFrom()
- Caches results within transaction scope

### Virtual Ordering Support
Enables user to customize display order in UI
- Stored separately from main property
- Applied post-filtering in GetOrderedValue()

---

## Performance Considerations

1. VisibleComplexFormBackRefs: O(n) where n = incoming refs
2. AllSenses: O(n) where n = total senses (recursive)
3. Results cached within transaction
4. EnsureCompleteIncomingRefsFrom() can be expensive for large DBs

---

## Implementation Checklist

For flexlibs Python.NET wrapper:

- [ ] VisibleComplexFormBackRefs for LexEntry
- [ ] VisibleComplexFormBackRefs for LexSense
- [ ] ComplexFormsNotSubentries for LexEntry
- [ ] ComplexFormsNotSubentries for LexSense
- [ ] MinimalLexReferences for LexEntry
- [ ] MinimalLexReferences for LexSense
- [ ] AllSenses for LexEntry (recursive)
- [ ] AllSenses for LexSense (recursive)

