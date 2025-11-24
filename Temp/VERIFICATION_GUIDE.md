# Verification Guide for Phase 2 Development

**Purpose**: Guide for development agents to use the automated verification system
**Last Updated**: 2025-11-22
**Applies To**: Phase 2 and beyond

---

## Overview

The verification system consists of three automated agents that work together to ensure code quality:

1. **Verification Agent** (Agent 4) - Basic automated checks
2. **Pre-QC Agent** (Agent 7) - Comprehensive pre-quality control
3. **CI/CD Pipeline** (Agent 5) - Continuous integration on every commit

These agents catch issues early and reduce rework cycles.

---

## Verification Agent (Agent 4)

### Purpose
Fast, automated verification of basic requirements before claiming work is complete.

### When to Use
- **Required**: Before marking any task as complete
- **Required**: Before pushing code to remote
- **Optional**: During development for quick checks

### How to Run

```bash
# From project root
./verify_agent_work.sh

# Or with specific parameters
./verify_agent_work.sh flexlibs_dev 29
```

### What It Checks

1. ✅ Python environment is set up
2. ✅ Required packages installed (pytest, black, flake8, mypy)
3. ✅ All modules import successfully
4. ✅ Directory structure is correct
5. ✅ Required files exist
6. ✅ No critical syntax errors
7. ✅ Tests run and pass
8. ✅ Test count meets expectations
9. ✅ Documentation files exist

### Expected Output

**Success:**
```
=========================================
VERIFICATION AGENT - Starting Verification
=========================================
...
✅ ALL VERIFICATION CHECKS PASSED
Agent work is verified and ready for the next stage.
```

**Failure:**
```
❌ VERIFICATION FAILED
Please fix the issues above before proceeding.
```

### What to Do If Verification Fails

1. **Read the error messages** - They show exactly what failed
2. **Fix the issues** - Address each failure one by one
3. **Re-run verification** - Repeat until all checks pass
4. **Do NOT bypass** - Verification gates must pass

---

## Pre-QC Agent (Agent 7)

### Purpose
Comprehensive automated quality checks before submitting to QC Agent for review.

### When to Use
- **Required**: Before requesting QC review
- **Required**: Before creating pull request
- **Recommended**: At 50% and 75% checkpoints

### How to Run

```bash
# From project root
python pre_qc_check.py

# Or specify module
python pre_qc_check.py flexlibs_dev
```

### What It Checks

1. ✅ All claimed files exist
2. ✅ All modules import successfully
3. ✅ Tests run and pass
4. ✅ No critical syntax errors (flake8)
5. ✅ Type hints present on functions
6. ✅ Docstrings present in modules
7. ✅ No undefined names
8. ✅ File count meets expectations
9. ✅ Required documentation exists
10. ⚠️  Debug print statements (warning only)

### Expected Output

**Success:**
```
============================================================
PRE-QC AGENT REPORT
============================================================
✅ Checks Passed: 8
⚠️  Warnings: 2
✅ ALL PRE-QC CHECKS PASSED
Code is ready for QC Agent review.
```

**Failure:**
```
❌ Checks Failed: 2
   - Some modules fail to import
   - Tests are failing
❌ PRE-QC FAILED - Please fix issues before QC review
```

### Understanding Warnings vs Failures

- **Failures (❌)**: Must be fixed - blocks QC review
- **Warnings (⚠️)**: Should be addressed - does not block QC

### What to Do If Pre-QC Fails

1. **Fix all failures first** - These are blocking issues
2. **Address warnings** - Optional but recommended
3. **Re-run Pre-QC** - Verify all issues resolved
4. **Submit to QC** - Only after Pre-QC passes

---

## CI/CD Pipeline (Agent 5)

### Purpose
Automatic verification on every commit and pull request.

### When It Runs
- **Automatically**: On every `git push` to `claude/**` branches
- **Automatically**: On pull requests
- **Multiple Python versions**: Tests on 3.9, 3.10, 3.11, 3.12

### What It Does

1. **Verify Job**: Runs on all Python versions
   - Installs dependencies
   - Verifies imports
   - Runs tests with coverage
   - Lints code
   - Checks formatting
   - Type checks
   - Runs verification script

2. **Integration Test Job**: Cross-module testing
   - Runs integration tests
   - Verifies cross-module compatibility

3. **Code Quality Job**: Advanced checks
   - Code complexity analysis
   - Maintainability index
   - Pylint checks

4. **Documentation Job**: Doc verification
   - Checks required docs exist
   - Verifies docstring coverage

### How to View Results

1. **Push code to GitHub**
2. **Go to Actions tab** in GitHub repository
3. **Find your commit** in the workflow runs
4. **Review results** - Green = passed, Red = failed

### What to Do If CI/CD Fails

1. **Click on failed job** to see details
2. **Read error logs** - Identifies specific failures
3. **Fix locally** - Address the issues in your code
4. **Re-run verification locally** before pushing
5. **Push fix** - CI/CD will run again automatically

---

## Complete Verification Workflow

### For Development Agents

**Step 1: During Development**
```bash
# Quick check (optional, but helpful)
./verify_agent_work.sh
```

**Step 2: At Checkpoints (25%, 50%, 75%)**
```bash
# Run Pre-QC check
python pre_qc_check.py

# Fix any issues
# Commit checkpoint
git add .
git commit -m "Checkpoint: 25% complete - passed Pre-QC"
git push
```

**Step 3: Before Claiming Complete**
```bash
# Run full verification
./verify_agent_work.sh flexlibs_dev 29

# Run Pre-QC
python pre_qc_check.py

# Both must pass before claiming complete
```

**Step 4: Before QC Review Request**
```bash
# Final verification
python pre_qc_check.py

# Must pass before requesting QC review
```

**Step 5: After Pushing to GitHub**
- Wait for CI/CD pipeline to complete
- Verify all checks pass (green checkmarks)
- If any fail, fix and push again

### For QC Agent

**Pre-Review Checklist**
1. ✅ Verification Agent passed
2. ✅ Pre-QC Agent passed
3. ✅ CI/CD pipeline all green
4. ✅ Code coverage ≥ 90%
5. ✅ No P0 or P1 issues

If any of these fail, **reject** and send back to developer.

---

## Proof-of-Execution Requirements

### What to Provide

When claiming work is complete, you **must** provide:

1. **Verification Script Output**
   ```bash
   ./verify_agent_work.sh > verification_output.txt 2>&1
   ```
   - Commit `verification_output.txt` to repository

2. **Pre-QC Script Output**
   ```bash
   python pre_qc_check.py > pre_qc_output.txt 2>&1
   ```
   - Commit `pre_qc_output.txt` to repository

3. **Test Results**
   ```bash
   pytest flexlibs_dev/tests/ -v > test_results.txt 2>&1
   ```
   - Commit `test_results.txt` to repository

4. **Timestamp and Environment**
   ```bash
   echo "Timestamp: $(date)" > environment.txt
   echo "Python: $(python --version)" >> environment.txt
   echo "Branch: $(git branch --show-current)" >> environment.txt
   echo "Commit: $(git rev-parse HEAD)" >> environment.txt
   ```
   - Commit `environment.txt` to repository

### Where to Store

Create directory for each cluster:
```
flexlibs_dev/tests/verification_results/
└── cluster_2_1/
    ├── verification_output.txt
    ├── pre_qc_output.txt
    ├── test_results.txt
    └── environment.txt
```

---

## Troubleshooting

### Common Issues

**Issue 1: "Module import failed"**
- **Cause**: Missing `__init__.py` or syntax error
- **Fix**: Check all directories have `__init__.py`, verify syntax

**Issue 2: "Tests failed"**
- **Cause**: Code changes broke tests or tests not updated
- **Fix**: Run pytest with `-v` to see which tests failed, fix code or tests

**Issue 3: "Syntax errors found"**
- **Cause**: Python syntax errors (missing colons, parens, etc.)
- **Fix**: Run `flake8` to see exact errors, fix syntax

**Issue 4: "Type hints missing"**
- **Cause**: Functions without type annotations
- **Fix**: Add type hints: `def foo(x: int) -> str:`

**Issue 5: "CI/CD pipeline fails but local passes"**
- **Cause**: Environment differences
- **Fix**: Check Python version, ensure all dependencies in requirements.txt

### Getting Help

1. **Check error messages** - Most issues are clearly indicated
2. **Review documentation** - CODING_STANDARDS.md, TESTING_GUIDELINES.md
3. **Ask Coordination Agent** - Update AGENT_STATUS.md with blocker
4. **Review similar code** - Check how other modules do it

---

## Best Practices

### ✅ DO

- Run verification frequently during development
- Fix issues immediately when found
- Commit verification outputs as proof
- Address warnings even if not blocking
- Keep verification scripts up to date

### ❌ DON'T

- Skip verification steps
- Bypass verification gates
- Commit without running Pre-QC
- Ignore warnings indefinitely
- Claim completion without proof

---

## Verification Checklist Template

Use this checklist for each cluster:

```markdown
## Cluster X.Y Verification

- [ ] All methods implemented
- [ ] All tests written and passing
- [ ] Verification Agent passed
- [ ] Pre-QC Agent passed
- [ ] CI/CD pipeline green
- [ ] Code coverage ≥ 90%
- [ ] Documentation complete
- [ ] Verification outputs committed
- [ ] Ready for QC review

**Verification Output**: tests/verification_results/cluster_X_Y/
**Date**: YYYY-MM-DD
**Agent**: Agent #
```

---

## Phase 2 Improvements Implemented

These verification tools address Phase 1 issues:

| Phase 1 Issue | Phase 2 Solution |
|---------------|------------------|
| Synthesis agent false claims | Verification Agent (automated proof) |
| Missing files discovered late | Verification checks file existence |
| Import errors not caught | Both agents verify imports |
| Tests not actually run | Pre-QC runs tests, requires output |
| No pre-merge checks | CI/CD pipeline on every push |
| Late issue discovery | Checkpoint-based verification |
| False completion claims | Proof-of-execution requirement |

---

## Summary

The verification system ensures:

1. **Quality** - Code meets standards before review
2. **Speed** - Issues caught early, less rework
3. **Confidence** - Automated proof of completion
4. **Consistency** - Same checks for all agents

**Remember**: The goal is not to slow down development, but to **prevent costly rework cycles**.

Run verification early and often!

---

**Document Owner**: Agent 6 (Coordination Agent)
**Last Updated**: 2025-11-22
**Version**: 1.0
