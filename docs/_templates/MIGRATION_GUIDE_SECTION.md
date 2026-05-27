# Template: MIGRATION_GUIDE.md Section

Use this when a `refactor!` / `feat!` / deprecation lands and needs a migration entry in `docs/MIGRATION_GUIDE.md`. One section per breaking change.

## Format

```markdown
## Breaking Change: <Short Title>

### What Changed

<One paragraph. Plain prose. What was, what is. No backstory unless needed.>

| Behavior | Before (v<X>) | After (v<Y>) |
|----------|---------------|--------------|
| <surface>| <old behaviour>| <new behaviour>|

### Why This Changed

<One paragraph. The motivating problem the change solves. Link to the bug / issue / PR that drove it.>

### Migration: <Aspect 1>

Update your scripts to do <X> instead of <Y>:

**Before (v<X>):**
```python
# old pattern
```

**After (v<Y>):**
```python
# new pattern
```

### Migration: <Aspect 2>

<Repeat per aspect that needs caller attention.>

### Migration: Detect-and-Fix Recipe

If you have a large script you want to update mechanically:

```bash
# grep / sed / ripgrep one-liners that catch the old pattern
```

### What If I Can't Migrate Yet?

<Pin to old version, or list any back-compat shim available, or state that no shim exists.>
```

## Worked example

```markdown
## Breaking Change: `flat=` → `recursive=` on hierarchical list ops

### What Changed

flexlibs2 standardizes the parameter that controls hierarchical-list traversal across every Operations class. The old `flat=` parameter is renamed to `recursive=`, and the default is now `recursive=True` (return all descendants).

| Behavior | Before (v2.4) | After (v2.5) |
|----------|---------------|--------------|
| `POS.GetAll()` | Top-level POSs only (~30) | All POSs including subcategories (~80) |
| `POS.GetEntryCount(noun)` | Direct-tagged entries only | Entries tagged with `noun` or any descendant |
| `flat=` parameter | Accepted | Raises `TypeError` |

### Why This Changed

The intuitive query ("give me everything under this category") was the harder one to spell. A previous bug missed entries tagged with subcategories because `GetEntryCount` only looked at the requested node. Standardizing on `recursive=` makes the common case simple and the specialized case explicit. See PR #<n>.

### Migration: rename `flat=` to `recursive=`

**Before:**
```python
poses = project.POS.GetAll(flat=True)
```

**After:**
```python
poses = project.POS.GetAll()  # recursive by default
# or, for top-level only:
poses = project.POS.GetAll(recursive=False)
```

### Migration: `GetEntryCount` returns larger numbers

**Before:**
```python
n = project.POS.GetEntryCount(noun)  # direct-tagged only
```

**After:**
```python
n = project.POS.GetEntryCount(noun)  # includes descendants
# for old behaviour:
n = project.POS.GetEntryCount(noun, recursive=False)
```

### Migration: Detect-and-Fix Recipe

```bash
# Find all callers using the old kwarg
rg --type py 'GetAll\(.*flat='
rg --type py 'include_subcategories='

# Most can be replaced with:
sed -i 's/flat=True/recursive=False/g; s/flat=False/recursive=True/g' your_script.py
```

### What If I Can't Migrate Yet?

Pin `flexlibs2<2.5` in your dependencies until you've completed the migration. No back-compat shim is provided.
```

## Rules

- **Always include a before/after table.** Even one row. Skim-readers scan tables first.
- **Always include code snippets.** Prose-only migrations are useless to scripted users.
- **Mention the version both before and after.** Not "old" and "new" — the actual versions.
- **Detect-and-Fix Recipe is optional but valued.** A grep one-liner saves the reader minutes.
- **Link the PR that introduced the change.** Bare descriptions go stale; PR links carry context.
- **Don't reference issue numbers in code blocks.** Project CLAUDE.md convention.
