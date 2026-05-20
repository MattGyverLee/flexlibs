# flexlibs Open Issues — Phased Resolution Plan

**Created:** 2026-05-20
**Source:** https://github.com/MattGyverLee/flexlibs/issues (10 open issues at time of writing)
**Agent team:** [../agents/](../agents/)

## Issue groupings

The 10 open issues collapse into 5 work units. Three are quick additive wins; two are cross-cutting bug families; one is a major coverage gap.

| Group | Issues | Theme | Risk |
|---|---|---|---|
| A. Discoverability | #13, #12 | Additive escape hatches | Low |
| B. Orphan-NPE family | #4 (umbrella), #6, #7, #8 | Ownership-ordering bugs in factory-create paths | Medium |
| C. Unicode / WS lookup | #9 (umbrella), #10 | Silent `Find()`/`Exists()` failures on NFD diacritics + tuple WS default | Medium |
| D. PhonRules wrapper | #5 | `Find()` returns None; `Delete()` TypeError | Low |
| E. Phonology coverage | #11 | Feature system, NC features, IPA setter, alpha-feature rules | High (large) |

## Phase 1 — Quick additive wins (#13, #12)

Pure additions; zero risk to existing callers. Ships first so workarounds get cleaner while bigger fixes are in flight.

**Scope:**
- Add `FLExProject.Cache` property
- Add `FLExProject.GetService(interface_type)` method
- Add `GetDefaultVernacularWSHandle()` returning `int`
- Add `GetDefaultAnalysisWSHandle()` returning `int`

**Agents:**
- **Programmer** — Implement on [flexlibs2/code/FLExProject.py](../flexlibs2/code/FLExProject.py).
- **QC** — Confirm docstrings, no behavior change to existing methods, follows project header conventions.
- **Verification** — `dir(project)` exposes new names; smoke test against a real LCM project.

**Acceptance:**
- `project.Cache` is the LcmCache
- `project.GetService(IPhPhonemeFactory)` returns the factory
- `project.GetDefaultVernacularWSHandle()` returns an `int` usable in `TsStringUtils.MakeString(text, ws)`
- Existing `GetDefaultVernacularWS()` tuple-returning API unchanged

## Phase 2 — Orphan-NPE family (#4 umbrella, #6, #7, #8)

Single root cause: setting properties on factory-created objects before they have an owner. Fix all instances together so the pattern doesn't reappear.

**Scope:**
- Confirmed sites:
  - [flexlibs2/code/Grammar/PhonemeOperations.py:184-193](../flexlibs2/code/Grammar/PhonemeOperations.py#L184-L193) — `Create`
  - [flexlibs2/code/Lexicon/LexSenseOperations.py:1024-1031](../flexlibs2/code/Lexicon/LexSenseOperations.py#L1024-L1031) — `SetPartOfSpeech` (new MSA path)
  - [flexlibs2/code/Grammar/PhonologicalRuleOperations.py:709-715](../flexlibs2/code/Grammar/PhonologicalRuleOperations.py#L709-L715) — `AddOutputSegment`
- Audit targets (per issue #8):
  - [PhonologicalRuleOperations.py:763-766](../flexlibs2/code/Grammar/PhonologicalRuleOperations.py#L763-L766) — left context wiring
  - [PhonologicalRuleOperations.py:815-818](../flexlibs2/code/Grammar/PhonologicalRuleOperations.py#L815-L818) — right context wiring
  - Allomorph creators, MSA creators, code/grapheme creators (grep `factory.Create()` followed by property set before `.Add(`)

**Agents:**
- **Team Lead** — Define audit scope and accept fix list before Programmer starts.
- **Domain Expert** — Confirm LCM ownership semantics: when does `Services` attach? Any cases where the current order is intentional?
- **Programmer** — Apply `Create → Add → Mutate` ordering to confirmed + audited sites.
- **QC** — Verify each fix follows the pattern; check no regressions in already-correct paths.
- **Verification** — Add regression tests from each issue's "Test" block.
- **Synthesis** — Document the pattern as a guideline in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) or new "LCM ownership ordering" note.

**Acceptance:**
- `Phonemes.Create("ö")` no longer NPEs
- `LexSense.SetPartOfSpeech(sense, pos)` works on freshly-created sense
- `PhonRules.AddOutputSegment(rule, phoneme)` works
- Regression tests pass
- Architecture note describing the pattern is checked in

## Phase 3 — Unicode + WS lookup (#9, #10)

**Scope:**
- Add NFD-normalizing helper to [flexlibs2/code/Shared/string_utils.py](../flexlibs2/code/Shared/string_utils.py)
- Apply to `Find()` / `Exists()` across:
  - `PhonemeOperations`
  - `NaturalClassOperations`
  - `POSOperations`
  - `SemanticDomainOperations`
  - any other multistring-keyed `Find`
- Fix the WS tuple default cascade: any path that resolves `wsHandle=None` via `GetDefaultVernacularWS()` / `GetDefaultAnalysisWS()` must unpack to `int`

**Agents:**
- **Domain Expert** — Confirm FLEx storage is NFD across the modules listed above.
- **Programmer** — Implement helper + apply across modules.
- **QC** — Normalize on both sides (query and stored); preserve case-folding behavior.
- **Verification** — Regression tests with NFC diacritic input (`ö`, `ç`, `ş`, `ü`, `ğ`) finding NFD-stored entries; confirm Phase 1's `GetDefaultVernacularWSHandle()` is used internally for default-resolution.

**Acceptance:**
- `project.Phonemes.Find("ö")` returns the phoneme even when stored as NFD
- `Phonemes.Create("ö")` no longer hits the C# NPE via tuple-WS default

## Phase 4 — PhonRules wrapper (#5)

**Scope:**
1. Fix `PhonologicalRule.name` in [flexlibs2/code/Grammar/phonological_rule.py:118-141](../flexlibs2/code/Grammar/phonological_rule.py#L118-L141): remove bare `except`, resolve the real `OwnerOfClass.project.DefaultAnalWs` failure (or switch `Find` to call `GetName(wrapper)`).
2. Fix `__ResolveObject` / `Delete` in [flexlibs2/code/Grammar/PhonologicalRuleOperations.py:246-252](../flexlibs2/code/Grammar/PhonologicalRuleOperations.py#L246-L252) to unwrap `PhonologicalRule` → `concrete` before `PhonRulesOS.Remove`.

**Agents:**
- **Programmer** — Implement both fixes.
- **Original Author** — Confirm unwrap pattern matches `LCMObjectWrapper` convention in other wrapper classes.
- **Verification** — Round-trip test: `GetAll() → Find(name) → Delete(wrapper)`.

## Phase 5 — Phonology coverage (#11)

Largest item. Splits into 4 sub-PRs per the issue. Full-team workflow.

**Sub-PR sequence (set by Team Lead):**
1. `PhonFeatureOperations` — feature system: features, values, structures, specs
2. `NaturalClassOperations.CreateFeatureBased()` — `PhNCFeatures` support
3. `PhonemeOperations.SetBasicIPASymbol()` + IPA code management
4. Alpha-features (`IPhFeatureConstraint`) + `WireRule()` builder

**Agents:**
- **Team Lead** — Sequence sub-PRs; final approval per sub-PR.
- **Domain Expert** — Validate SPE/generative phonology terminology; Turkish vowel harmony as canonical acceptance test.
- **Original Author** — Confirm `PhonFeatureOperations` shape matches `InflectionFeatureOperations`; wrappers follow [docs/ARCHITECTURE_WRAPPERS.md](../docs/ARCHITECTURE_WRAPPERS.md).
- **Programmer** — Implement each sub-PR. Apply Phase 2's ordering lesson throughout.
- **QC** — Enforce wrapper conventions, type capability checks, smart-collection patterns.
- **Verification** — Turkish vowel harmony end-to-end test as acceptance.
- **Synthesis** — Document the new `PhonFeatureOperations` module in API docs.

## Dependencies

```
Phase 1 (independent)     ─┐
Phase 2 (orphan-NPE)      ─┤
Phase 3 (Unicode/WS)      ─┤
Phase 4 (PhonRules)       ─┤
                           └──> Phase 5 (Phonology coverage) — depends on Phase 2 ordering lesson
```

Phases 1–4 can proceed in parallel via separate branches. Phase 5 should wait for Phase 2 to merge so new factory-create paths follow the corrected ordering.

## Estimated relative effort

| Phase | Effort | Issues closed |
|---|---|---|
| 1 | ~half day | #13, #12 |
| 2 | 1–2 days | #4, #6, #7, #8 |
| 3 | 1 day | #9, #10 |
| 4 | half day | #5 |
| 5 | 1–2 weeks (4 sub-PRs) | #11 |

## Progress log

- 2026-05-20 — Plan drafted; user approved; Phase 1 starting.
