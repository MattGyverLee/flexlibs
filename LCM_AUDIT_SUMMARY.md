# LCM Capabilities Audit - Executive Summary

## Quick Overview

This audit analyzes **25 SIL packages** imported across **72 files** in the flexlibs2 codebase, containing **90+ LCM classes/interfaces** organized into **57 user-facing Operations classes**.

### Key Numbers

| Metric | Count |
|---|---|
| Total Python files analyzed | 101 |
| Files with SIL imports | 72 |
| Distinct SIL modules imported | 25 |
| LCM classes/interfaces imported | 90+ |
| User-facing Operations classes | 57 |
| Helper/Infrastructure files | 7 |
| TODOs found | 2 |
| Critical risks identified | 0 |

---

## The Architecture in 30 Seconds

FlexLibs2 uses a **Repository -> Factory -> Wrapper** pattern:

```
Users
  ↓
FLExProject.DOMAIN.METHOD()        ← 57 Operations classes
  ↓
Repository/Factory/Manager         ← Wrapped LCM APIs
  ↓
SIL.LCModel (90+ classes)          ← FieldWorks internals
```

**Result:** Users never touch the raw LCM API. Everything is safe, validated, and documented.

---

## What's Imported

### The 25 SIL Modules (Categorized)

**Data Access (Repositories)**
```
SIL.LCModel (core)
├── ICmObjectRepository
├── ILexEntryRepository, IWfiWordformRepository, IWfiAnalysisRepository
├── ICmPossibilityRepository, ITextRepository, ISegmentRepository
└── And 6 more...
```

**Object Creation (Factories)**
```
SIL.LCModel
├── ICmPossibilityListFactory, IPartOfSpeechFactory, IPhEnvironmentFactory
├── IMoStemAllomorphFactory, IMoAffixAllomorphFactory
└── And 7 more...
```

**Text Handling**
```
SIL.LCModel.Core.KernelInterfaces
├── ITsString (immutable text)
├── ITsStrBldr (mutable text)
└── IMultiUnicode, IMultiString

SIL.LCModel.Core.Text
└── TsStringUtils (text utilities)
```

**Services & Management**
```
SIL.LCModel
├── IUndoStackManager (save operations)
└── IFwMetaDataCacheManaged (schema)

SIL.LCModel.Infrastructure
└── IDataReader (advanced)
```

**System/Metadata**
```
SIL.LCModel.Core.Cellar
├── CellarPropertyType (property types)
└── CellarPropertyTypeFilter

SIL.LCModel
├── LexEntryTags, LexSenseTags, etc. (field names)
├── LcmCache, LcmSettings, LcmFileHelper (core)
└── Exception types (5 total)
```

**FieldWorks Integration**
```
SIL.FieldWorks.*
├── ProjectId, ProjectIdentifier
├── FwLcmUI (user interface)
├── ChooseLangProjectDialog
├── FwDirectoryFinder, FwRegistryHelper (paths)
└── ThreadHelper, ProgressDialog (threading)

SIL.WritingSystems
├── WritingSystemDefinition
└── Sldr (language data)
```

---

## Exposure Matrix

### Fully Exposed (User-Facing API)

**57 Domain Operations** - All accessed via `project.DOMAIN` property:

```python
# Grammar (13)
project.POS
project.Phonemes
project.Environments
project.Allomorphs
project.MorphRules
project.PhonRules
(+ 7 more)

# Lexicon (11)
project.LexEntry
project.Senses
project.Examples
(+ 8 more)

# TextsWords (5)
project.Texts
project.Wordforms
project.Segments
(+ 2 more)

# And 6 more domains...
```

Each exposes methods like:
```python
.GetAll()          # List all items
.Find(name)        # Find by name
.Create(...)       # Create new item
.Update(...)       # Modify item
.Delete(item)      # Remove item
```

### Partially Exposed

| Feature | Imported | Exposed | Notes |
|---|---|---|---|
| Undo/Redo | IUndoStackManager | NO | Auto-save only, no manual control |
| Metadata | IFwMetaDataCacheManaged | NO | Not currently used |
| Advanced Text | ITsStrBldr | NO | Hidden, available via .project for power users |
| Direct Access | .project, .lp, .lexDB | YES | Available but discouraged |

### Not Exposed (Internal Only)

| Category | Count | Examples |
|---|---|---|
| Repository/Factory bases | 21 | Repository implementations, not interfaces |
| Text tags | 11 | LexEntryTags, TextTags, etc. |
| Property system | 2 | CellarPropertyType, CellarPropertyTypeFilter |
| Utilities | 7+ | ReflectionHelper, ThreadHelper, etc. |
| UI/Infrastructure | 10+ | Dialogs, file finders, registry |

---

## Risk Assessment

### Critical Risks: **NONE FOUND**

Dangerous operations are all protected:
- ✓ Undo stack: Internal, no user access
- ✓ Cache management: Hidden, auto-managed
- ✓ Thread handling: Infrastructure only
- ✓ Direct casting: Wrapped, marked as internal

### Medium Risks: **2 IDENTIFIED**

1. **Direct `.project` access** (discouraged but allowed)
   - Users can bypass wrappers if they try hard
   - Mitigation: Document as "use at own risk"
   - Current status: Not advertised, available in docstring example only

2. **Incomplete domain coverage** (Scripture, advanced Discourse)
   - Some FLEx features not yet wrapped
   - Mitigation: Document workarounds
   - Current status: Known limitation, accept as is for now

### Low Risks: **HANDLED**

- Text string handling (ITsString) - wrapped in `BestStr()`
- Exception mapping - custom exceptions hide LCM errors
- Factory calls - all guarded by write-enabled checks
- Repository access - wrapped in safe query methods

---

## Recommendations Summary

### 1. Immediate (High Priority)

**[DOCUMENT]** Create `docs/ADVANCED_LCM_ACCESS.md`
- How to use `.project` for advanced patterns
- When to use raw LCM vs. Operations
- ITsString examples for power users

**[UPDATE]** Add to CLAUDE.md: "Power User Access" section
- Brief guide to bypassing wrappers safely
- Examples of accessing unexposed features

### 2. Short Term (Medium Priority)

**[IMPLEMENT]** Expose `IFwMetaDataCacheManaged`
- Enable "what fields does X have?" queries
- Useful for introspection and documentation

**[IMPLEMENT]** Create `TextBuilderOperations` wrapper
- Wrap ITsStrBldr for complex text building
- Document multi-writing-system patterns

**[COMPLETE]** Scripture domain operations
- Several key operations still missing
- Would provide complete coverage

### 3. Long Term (Low Priority)

**[ENHANCE]** Linux flatpak support
- Update FLExGlobals.py path detection
- Test with FW flatpak installation

**[ENHANCE]** Project selection dialog
- Use native `ChooseLangProjectDialog()`
- Support network drives

---

## What Should Be Wrapped vs. Not

### Should Always Be Wrapped
- [✓] Factories (object creation)
- [✓] Write operations (write-enabled checks)
- [✓] Complex queries (validation)
- [✓] Text handling (multi-lingual support)

### Should NOT Be Wrapped
- [✓] Read-only metadata
- [✓] Constants/enumerations
- [✓] Version information
- [✓] Configuration data

### Should Be Exposed (for power users)
- [ ] IFwMetaDataCacheManaged (schema introspection)
- [ ] ITsStrBldr (complex text building)
- [ ] Direct repository access (optional, documented)

---

## File Organization

```
flexlibs2/code/
├── FLExProject.py              ← User API entry point (57 properties)
├── BaseOperations.py           ← Parent class for all operations
├── FLExInit.py                 ← Initialization
├── FLExLCM.py                  ← Project opening
├── FLExGlobals.py              ← FW paths and globals
├── lcm_casting.py              ← Type casting utilities (INTERNAL)
├── CastingOperations.py        ← Casting for operations (INTERNAL)
├── PythonicWrapper.py          ← Suffix-free property access (INTERNAL)
│
├── Grammar/                    ← 13 Operations classes
│   ├── POSOperations.py
│   ├── PhonemeOperations.py
│   ├── EnvironmentOperations.py
│   ├── PhonologicalRuleOperations.py
│   └── ... (9 more)
│
├── Lexicon/                    ← 11 Operations classes
│   ├── LexEntryOperations.py
│   ├── SenseOperations.py
│   ├── AllomorphOperations.py
│   └── ... (8 more)
│
├── TextsWords/                 ← 5 Operations classes
│   ├── TextOperations.py
│   ├── WfiWordformOperations.py
│   ├── SegmentOperations.py
│   └── ... (2 more)
│
├── Notebook/                   ← 5 Operations classes
├── Lists/                      ← 6 Operations classes
├── System/                     ← 7 Operations classes
├── Discourse/                  ← 8 Operations classes
├── Reversal/                   ← 2 Operations classes
├── Scripture/                  ← 2 Operations classes
│
└── Shared/                     ← Utilities
    ├── string_utils.py         ← Text normalization
    ├── smart_collection.py     ← SmartCollection base
    ├── wrapper_base.py         ← LCMObjectWrapper base
    └── ... (utilities)
```

---

## TODOs in Code

### TODO #1: Linux Flatpak Support
- **File:** `FLExGlobals.py:102-105`
- **Issue:** Old path logic doesn't work with flatpak
- **Current:** Windows/macOS only
- **Effort:** LOW - Detection + path fallback
- **Impact:** MEDIUM - Linux users need workaround

### TODO #2: Use FW Project Chooser
- **File:** `FLExLCM.py:53-54`
- **Issue:** Using simple file listing, not FW native dialog
- **Current:** Works but not user-friendly
- **Effort:** LOW - Use existing dialog class
- **Impact:** LOW - Cosmetic enhancement

---

## Testing & Quality

**Current Coverage:**
- Contract tests validate API compatibility
- Operations classes follow consistent patterns
- Casting operations thoroughly tested

**Recommended Additions:**
- Edge case tests for polymorphic collections
- Multi-writing-system text handling
- Locked project exception handling
- Concurrent access patterns

---

## Usage Examples

### User-Level (Safe)
```python
from flexlibs2.code.FLExProject import FLExProject

project = FLExProject()
project.OpenProject("MyProject", writeEnabled=True)

# All safe - wrapped and validated
for pos in project.POS.GetAll():
    print(project.POS.GetName(pos))

entry = project.LexEntry.Create("run", "stem")
sense = project.LexEntry.AddSense(entry, "to move")

project.CloseProject()
```

### Power User (Documented but Not Recommended)
```python
# Direct repository access (available in docstrings)
repo = project.ObjectRepository(ICmObjectRepository)
obj = repo.GetObject(hvo)

# Text building with ITsString
from SIL.LCModel.Core.Text import TsStringUtils
ws_handle = project.WSHandle('en')
ts = TsStringUtils.MakeString("text", ws_handle)

# Type casting
from flexlibs2.code.lcm_casting import cast_to_concrete
concrete = cast_to_concrete(base_interface_obj)
```

---

## Conclusion

**The LCM audit reveals a well-designed abstraction layer that:**

1. **Successfully hides complexity** - 90+ LCM classes wrapped in 57 user-friendly operations
2. **Protects users** - Write operations guarded, exceptions mapped, factories validated
3. **Allows escape hatches** - Power users can access raw LCM if documented properly
4. **Maintains consistency** - Repository → Factory → Wrapper pattern throughout
5. **Has minimal risk** - No critical security/stability concerns found

**The main improvement area is documentation** - Adding guides for:
- Power user access patterns
- Advanced text handling
- Schema introspection
- When to wrap new features

**Overall Assessment: HEALTHY ARCHITECTURE** ✓

The project successfully achieves its goal of making FLEx data accessible without overwhelming users with LCM complexity. The separation of concerns is clean, and the abstraction layers are appropriate to the task.

---

## Document References

- **LCM_CAPABILITIES_AUDIT.md** - Comprehensive 90+ import analysis
- **LCM_CAPABILITIES_AUDIT_REFERENCES.md** - Code file and line references
- **LCM_AUDIT_SUMMARY.md** - This executive summary

---

**Audit Date:** 2025-03-16
**Scope:** flexlibs2/code directory (101 Python files)
**Methodology:** Import analysis, usage pattern documentation, risk assessment
**Confidence Level:** HIGH - All imports traced, all operations documented

