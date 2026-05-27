# Template: CHANGELOG Entry

Use this when adding a single change to `CHANGELOG.md` under `[Unreleased]`. Pick the most-specific section. One entry per logical change. Reference the PR or commit hash inline.

## Format

```markdown
## [Unreleased]

### Breaking Changes
- **<one-line summary>** (#<PR>) — <one paragraph: what broke, who is affected, how to migrate>

### Added
- **<one-line summary>** (#<PR>) — <one sentence describing the new surface>

### Changed
- **<one-line summary>** (#<PR>) — <one sentence describing the change in behaviour>

### Deprecated
- **<one-line summary>** (#<PR>) — <method/param being deprecated, when removal is scheduled>

### Removed
- **<one-line summary>** (#<PR>) — <what was removed, what to use instead>

### Fixed
- **<one-line summary>** (#<PR>) — <one sentence describing the bug fixed>

### Security
- **<one-line summary>** (#<PR>) — <one sentence describing the security improvement>
```

## Worked examples

### Breaking change with migration link

```markdown
### Breaking Changes
- **`flat=` parameter renamed to `recursive=` on hierarchical list ops** (#<PR>) — Default semantics inverted: `flat=True` is now `recursive=False`. Affects POS, GramCat, LexSense, SemanticDomain, Anthropology, Location, Publication, and PossibilityLists. See `docs/MIGRATION_GUIDE.md` for migration steps.
```

### Added (new public method)

```markdown
### Added
- **`project.GetFactory(interface_type)`** (#<PR>) — Discoverable entry point for LCM factory and service lookup; works around pythonnet generic-method binding quirks.
```

### Fixed (bug fix)

```markdown
### Fixed
- **`WfiAnalysisOperations.Delete` no longer raises `AttributeError`** (#<PR>) — `analysis.Owner` is now cast to `IWfiWordform` before accessing `AnalysesOC`.
```

## Rules

- **One change per bullet.** Don't merge "fixed X and refactored Y" into one entry.
- **Bold the headline.** It's the only thing skim-readers see.
- **Reference the PR.** No bare commit hashes (link the PR, which links the commits).
- **No issue numbers in the bullet text.** The PR body carries the issue cross-references.
- **No emojis.** Project CLAUDE.md rule.
- **No marketing prose.** "Improved performance" is not an entry; "Reduced `GetEntryCount(top_pos)` from O(n*m) to O(n) by precomputing the value-lookup map" is.
- **Promote `[Unreleased]` only at release cut.** Do not assign a version number until the release is being tagged.
