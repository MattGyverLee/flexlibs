# Review Process

## Complete Data Access Initiative - Step-by-Step Code Review Process

**Version**: 1.0
**Last Updated**: 2025-11-22
**Reviewer**: Agent 5 - Quality Control & Standards Enforcement Specialist

---

## 🎯 Purpose

This document defines the systematic review process for all cluster implementations. Every cluster must pass through these review stages before being merged.

---

## 📋 Review Stages

1. **Automated Checks** - Pre-commit hooks, CI/CD
2. **Code Review** - Manual review by QC specialist
3. **Testing Verification** - Test execution and coverage
4. **Integration Testing** - Integration with other clusters
5. **Documentation Review** - Documentation completeness
6. **Final Approval** - Overall assessment

---

## STAGE 1: AUTOMATED CHECKS

### 1.1 Pre-commit Validation
```bash
# On agent's branch
git checkout <agent-branch>

# Run pre-commit hooks
pre-commit run --all-files
```

### 1.2 Required Checks
- [ ] **Black formatting**: Code properly formatted
- [ ] **Flake8 linting**: No linting errors
- [ ] **Mypy type checking**: All type hints valid
- [ ] **Import sorting**: Imports properly organized
- [ ] **Trailing whitespace**: Removed
- [ ] **YAML validation**: Config files valid

### 1.3 CI/CD Pipeline
- [ ] All CI tests pass
- [ ] Build succeeds
- [ ] No warnings

### 1.4 If Checks Fail
Request changes from agent with specific errors and fixes needed.

---

## STAGE 2: CODE REVIEW

### 2.1 Review Methodology

#### Step 1: High-Level Review (15 minutes)
- [ ] Code organization makes sense
- [ ] Files in correct directories
- [ ] Naming conventions followed
- [ ] All methods from PROJECT_BOARD.md implemented

#### Step 2: Method-by-Method Review (30-60 minutes)
For each method, check:
- [ ] Type hints present
- [ ] Parameters named correctly
- [ ] Return type correct
- [ ] Logic is clear
- [ ] Error handling appropriate
- [ ] COM interop correct
- [ ] UndoableUnitOfWork used for writes
- [ ] Docstring complete

#### Step 3: Cross-Cutting Concerns (15 minutes)
- [ ] Consistency across methods
- [ ] Error messages are consistent
- [ ] No code duplication
- [ ] Performance considerations

### 2.2 Use QC_CHECKLIST.md
Review against comprehensive checklist covering:
- Method signatures
- Implementation quality
- Documentation
- Testing
- Consistency
- Security

---

## STAGE 3: TESTING VERIFICATION

### 3.1 Test Execution
```bash
# Run tests for cluster
pytest tests/test_cluster_X_Y.py -v

# With coverage
pytest tests/test_cluster_X_Y.py --cov=flexlibs_dev/<module> --cov-report=html
```

### 3.2 Test Review Checklist
- [ ] All specified tests implemented
- [ ] All tests pass
- [ ] Coverage >90%
- [ ] Tests follow AAA pattern
- [ ] Clear test names
- [ ] Tests are independent
- [ ] Proper cleanup

### 3.3 Coverage Analysis
- Review HTML coverage report
- Identify any gaps
- Verify all error paths tested

---

## STAGE 4: INTEGRATION TESTING

### 4.1 Integration Test Execution
```bash
# Run integration tests
pytest tests/test_cluster_X_Y.py::test_integration -v

# Run all integration tests
pytest -m integration
```

### 4.2 Integration Checklist
- [ ] Integration test demonstrates realistic workflow
- [ ] Multiple methods work together
- [ ] Data persists correctly
- [ ] No side effects
- [ ] Cleanup works

### 4.3 Cross-Cluster Integration
If cluster depends on others:
```bash
# Run tests for dependent clusters
pytest tests/test_cluster_X_*.py -v
```

---

## STAGE 5: DOCUMENTATION REVIEW

### 5.1 Method Documentation
For each method:
- [ ] Docstring present and complete
- [ ] Purpose clearly stated
- [ ] Parameters documented with types
- [ ] Return value documented
- [ ] Exceptions documented
- [ ] Usage example (for complex methods)
- [ ] Related methods referenced

### 5.2 Code Comments
- [ ] Complex logic explained
- [ ] "Why" comments present
- [ ] FLEx quirks documented
- [ ] TODOs have issue numbers
- [ ] No commented-out code

---

## STAGE 6: FINAL APPROVAL

### 6.1 Overall Assessment

Check all stages:
- [ ] Stage 1: Automated Checks - PASS
- [ ] Stage 2: Code Review - PASS
- [ ] Stage 3: Testing - PASS
- [ ] Stage 4: Integration - PASS
- [ ] Stage 5: Documentation - PASS

### 6.2 Quality Metrics
- **Test Coverage**: ___% (Target: >90%)
- **Methods Implemented**: ___/___
- **Tests Written**: ___/___
- **Issues Found**: ___ (P0, P1, P2, P3)

### 6.3 Approval Criteria

#### ✅ APPROVED
- All automated checks pass
- No P0 or P1 issues
- Coverage >90%
- All tests pass
- Documentation complete

#### ⚠️ APPROVED WITH MINOR ITEMS
- All automated checks pass
- No P0 or P1 issues
- Minor P2 issues can be follow-up
- Coverage >90%

#### ❌ NEEDS WORK
- Automated checks fail
- P0 or P1 issues present
- Coverage <90%
- Tests failing
- Major documentation gaps

### 6.4 Final Actions

#### If APPROVED:
1. Add approval comment
2. Update PROJECT_BOARD.md status to 🟢 Complete
3. Merge to main branch
4. Notify team

```bash
git checkout claude/expand-flextools-data-access-013mrWNEJ6GpYcbeRNdFuFBi
git merge <agent-branch> --no-ff
git push origin claude/expand-flextools-data-access-013mrWNEJ6GpYcbeRNdFuFBi
```

#### If NEEDS WORK:
1. Create review report (AGENT_REVIEW_TEMPLATE.md)
2. Post as comment
3. Request changes
4. Wait for fixes
5. Re-review when ready

---

## 🔄 RE-REVIEW PROCESS

### When Agent Addresses Feedback

1. **Check Updates**
   ```bash
   git checkout <agent-branch>
   git pull
   ```

2. **Review Changes**
   ```bash
   git log --oneline -n 5
   git diff <previous-commit> HEAD
   ```

3. **Focus Re-Review**
   - Review only flagged items
   - Verify all changes made
   - Check for new issues

4. **Update Review Report**
   - Mark issues resolved
   - Note any new issues
   - Make decision

---

## 📊 REVIEW METRICS

Track for each review:

- **Time Spent**: ___ hours
- **Issues Found**: ___ (by priority)
- **Review Rounds**: ___
- **Time to Approval**: ___ days
- **Code Quality Score**: ___/10

---

## 📝 REVIEW BEST PRACTICES

### For Reviewers

#### DO:
- ✅ Be thorough but not nitpicky
- ✅ Explain why changes needed
- ✅ Provide examples
- ✅ Recognize good work
- ✅ Be consistent
- ✅ Review promptly (within 24 hours)

#### DON'T:
- ❌ Bikeshed over trivial style
- ❌ Request changes without explanation
- ❌ Approve code you don't understand
- ❌ Block on minor issues
- ❌ Rush reviews

### For Agents

#### DO:
- ✅ Run all checks before submitting
- ✅ Self-review first
- ✅ Respond to feedback promptly
- ✅ Ask for clarification if needed
- ✅ Test changes thoroughly

#### DON'T:
- ❌ Submit code with known issues
- ❌ Take feedback personally
- ❌ Argue over standards
- ❌ Rush fixes

---

## 🔍 COMMON ISSUES

### Watch For:

1. **Missing Type Hints**
2. **Incomplete Error Handling**
3. **Missing Docstrings**
4. **No UndoableUnitOfWork**
5. **Tests Missing Cleanup**

---

## 📋 QUICK REVIEW CHECKLIST

Before approving:

- [ ] All automated checks pass
- [ ] All methods implemented
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Error handling appropriate
- [ ] Tests pass
- [ ] Coverage >90%
- [ ] Integration test passes
- [ ] Documentation complete
- [ ] No security issues

---

## 📞 ESCALATION

### When to Escalate
- Fundamental design disagreements
- Security vulnerabilities
- Agent unresponsive
- Timeline blockers

### Process
1. Document issue
2. Attempt resolution with agent
3. If unresolved, escalate to project lead
4. Include all context

---

**End of Review Process**

For questions, contact Agent 5 - QC Specialist.
