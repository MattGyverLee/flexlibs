# Agent Review Report

## Code Review Report - Cluster [X.Y]

**Cluster**: [X.Y - Name]  
**Agent**: [Agent Name/Number]  
**Reviewer**: Agent 5 - QC Specialist  
**Review Date**: [YYYY-MM-DD]  
**Branch**: [agent-branch-name]

---

## 📊 EXECUTIVE SUMMARY

**Status**: ✅ APPROVED / ⚠️ APPROVED WITH ITEMS / ❌ NEEDS WORK

**Recommendation**: MERGE / REQUEST CHANGES / BLOCK

**Summary**: [2-3 sentence summary]

### Quick Stats
- **Methods**: [X/Y] ([%]%)
- **Tests**: [X/Y] ([%]%)
- **Coverage**: [%]% (Target: >90%)
- **Issues**: [Total] (P0: [X], P1: [Y], P2: [Z])
- **Quality Score**: [X]/10

---

## ✅ STAGE 1: AUTOMATED CHECKS

**Status**: ✅ PASS / ❌ FAIL

### Checks
- [ ] Black formatting
- [ ] Flake8 linting
- [ ] Mypy type checking
- [ ] Import sorting
- [ ] CI/CD pipeline

**Result**: ✅ PASS / ❌ FAIL

---

## 📝 STAGE 2: CODE REVIEW

**Status**: ✅ PASS / ⚠️ ISSUES / ❌ FAIL

### Implementation Completeness
- [x] Method 1
- [x] Method 2
- [ ] Method 3 (MISSING)

**Completeness**: [X/Y] ([%]%)

### Method Reviews
[For each method: signature, implementation, documentation status]

### Code Quality
**Strengths**:
- [Strength 1]

**Areas for Improvement**:
- [Area 1]

**Result**: ✅ PASS / ⚠️ ISSUES / ❌ FAIL

---

## 🧪 STAGE 3: TESTING

**Status**: ✅ PASS / ❌ FAIL

### Test Results
- Total: [X]
- Passed: [X]
- Failed: [X]

### Coverage
- **Target**: >90%
- **Actual**: [X]%
- **Status**: ✅ / ❌

**Result**: ✅ PASS / ❌ FAIL

---

## 🔗 STAGE 4: INTEGRATION

**Status**: ✅ PASS / ❌ FAIL

### Integration Test
- Test: test_[cluster]_integration
- Result: ✅ PASS / ❌ FAIL

**Result**: ✅ PASS / ❌ FAIL

---

## 📚 STAGE 5: DOCUMENTATION

**Status**: ✅ PASS / ⚠️ ISSUES / ❌ FAIL

### Docstrings
- **Complete**: [X/Y] ([%]%)
- All have: purpose, args, returns, exceptions

**Result**: ✅ PASS / ⚠️ ISSUES / ❌ FAIL

---

## 🎯 FINAL ASSESSMENT

| Stage | Result |
|-------|--------|
| 1. Automated | ✅/❌ |
| 2. Code Review | ✅/⚠️/❌ |
| 3. Testing | ✅/❌ |
| 4. Integration | ✅/❌ |
| 5. Documentation | ✅/⚠️/❌ |

### Issues Summary
- **P0 (Critical)**: [X]
- **P1 (High)**: [X]
- **P2 (Medium)**: [X]
- **P3 (Low)**: [X]

---

## 🔍 DETAILED ISSUES

### P0 - Critical (Must Fix)

#### P0-1: [Issue Title]
- **File**: [file:line]
- **Problem**: [description]
- **Fix**: [recommended fix]

### P1 - High (Should Fix)

#### P1-1: [Issue Title]
- **File**: [file:line]
- **Problem**: [description]
- **Fix**: [recommended fix]

---

## ✨ POSITIVE FEEDBACK

**What Went Well**:
- [Positive 1]
- [Positive 2]

---

## 📋 ACTION ITEMS

### Required (Before Merge)
- [ ] Fix P0 issue: [description]
- [ ] Fix P1 issue: [description]

### Optional (Follow-up)
- [ ] Address P2: [description]

---

## 🎯 DECISION

**Status**: ✅ APPROVED / ⚠️ APPROVED WITH ITEMS / ❌ NEEDS WORK

**Rationale**: [explanation]

### Next Steps
- [Step 1]
- [Step 2]

---

**Reviewer**: Agent 5  
**Date**: [YYYY-MM-DD]

---

For template usage instructions, see REVIEW_PROCESS.md.
