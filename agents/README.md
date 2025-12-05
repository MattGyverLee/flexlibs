# AI Agent Personalities for Software Development

This directory contains detailed descriptions of specialized AI agent personalities that can be used for complex software development tasks requiring multi-perspective review and coordination.

## Overview

These agent personalities were developed and refined during the flexlibs v2.0.0 refactoring project. They represent distinct expertise areas and review perspectives that, when combined, provide comprehensive coverage of software development quality concerns.

## Agent Personalities

### Core Development Agents
- [Programmer Agent](./programmer-agent.md) - Implementation specialist
- [Verification Agent](./verification-agent.md) - Completeness and correctness validation
- [QC Agent](./qc-agent.md) - Code quality and standards enforcement

### Expert Review Agents
- [Domain Expert Agent](./domain-expert-agent.md) - Domain-specific terminology and workflow validation
- [Original Author Agent](./original-author-agent.md) - Philosophy, style, and backward compatibility review
- [Synthesis Agent](./synthesis-agent.md) - Pattern analysis and recommendations

### Coordination
- [Team Lead Agent](./team-lead.md) - Planning, coordination, and final approval

## Agent Personality Overview

| Agent | Core Expertise | Primary Focus |
|-------|----------------|---------------|
| **Programmer** | Implementation | Writing code, solving technical problems |
| **Verification** | Validation | Completeness, correctness, testing |
| **QC** | Quality | Standards, error handling, edge cases |
| **Domain Expert** | Domain Knowledge | Terminology, workflows, user perspective |
| **Original Author** | Philosophy | Style consistency, simplicity, maintainability |
| **Synthesis** | Analysis | Patterns, metrics, recommendations |
| **Team Lead** | Coordination | Planning, tracking, approval |

## Generic Workflow Pattern

These agents can be orchestrated in various ways depending on project needs:

### Sequential Workflow (Comprehensive)
```
Team Lead → Programmer(s) → Verification → QC → Domain Expert →
Original Author → Synthesis → Team Lead (Approval)
```

### Parallel Review Workflow (Faster)
```
Team Lead → Programmer(s) → Verification →
                              ├─ QC ────────┐
                              ├─ Domain Expert ─┤→ Synthesis → Team Lead
                              └─ Original Author ┘
```

### Iterative Workflow (Complex Projects)
```
Team Lead → Programmer → QC → Fix Issues → QC → (repeat until passing) →
Verification → Expert Reviews → Synthesis → Team Lead
```

## When to Use Each Agent

### Programmer Agent
**Use for:** Implementation tasks, bug fixes, feature development
**Key value:** Technical execution, code writing

### Verification Agent
**Use for:** Checking completeness, testing coverage, API compatibility
**Key value:** Ensures nothing is missing, all requirements met

### QC Agent
**Use for:** Code quality review, standards enforcement
**Key value:** Maintains code health, catches quality issues

### Domain Expert Agent
**Use for:** Projects with specialized domain knowledge (linguistics, finance, healthcare, etc.)
**Key value:** Ensures domain concepts are correctly represented
**Customize:** Adapt domain knowledge section to your field

### Original Author Agent
**Use for:** Refactoring existing codebases, maintaining consistency
**Key value:** Preserves design philosophy, prevents regression
**Customize:** Define the "philosophy" based on project/author style

### Synthesis Agent
**Use for:** End of implementation phase, pattern analysis
**Key value:** Extracts lessons learned, identifies improvements

### Team Lead Agent
**Use for:** All projects requiring coordination
**Key value:** Orchestrates workflow, makes final decisions

## Customizing Agent Personalities

Each agent personality can be adapted to your project by:

1. **Adjusting Domain Knowledge**
   - Replace "linguistics" with your domain (finance, healthcare, etc.)
   - Update terminology standards
   - Modify workflow examples

2. **Defining Philosophy**
   - Set coding standards (PEP 8, Google Style, etc.)
   - Define design principles (SOLID, DRY, etc.)
   - Establish team conventions

3. **Setting Quality Thresholds**
   - Define acceptable scores (e.g., QC ≥ 85/100)
   - Set coverage requirements (e.g., tests ≥ 80%)
   - Establish blocking vs non-blocking issues

4. **Adapting Workflows**
   - Choose sequential vs parallel
   - Add or remove agent roles
   - Adjust review depth

## Example Use Cases

### Use Case 1: API Refactoring
**Agents:** Team Lead → Programmer → Verification → QC → Original Author → Synthesis
**Focus:** Backward compatibility, pattern consistency

### Use Case 2: New Feature Development
**Agents:** Team Lead → Programmer → QC → Domain Expert → Team Lead
**Focus:** Domain correctness, code quality

### Use Case 3: Bug Fix
**Agents:** Programmer → QC → Verification
**Focus:** Quick turnaround, quality check

### Use Case 4: Major Refactoring
**Agents:** Full team (all 7 agents)
**Focus:** Comprehensive review from all perspectives

## Benefits of Multi-Agent Approach

1. **Comprehensive Coverage** - Each agent brings unique perspective
2. **Separation of Concerns** - Clear responsibilities reduce overlap
3. **Quality Gating** - Multiple checkpoints catch different issues
4. **Documented Process** - Agent reports create audit trail
5. **Reusable Patterns** - Lessons learned documented systematically

## Getting Started

1. **Choose Agents** - Select which agent personalities fit your task
2. **Customize** - Adapt domain knowledge, philosophy, and standards
3. **Define Workflow** - Sequential, parallel, or hybrid approach
4. **Set Criteria** - Define success criteria and quality thresholds
5. **Execute** - Launch agents in defined order
6. **Review** - Team Lead synthesizes results and approves

## Related Documentation

- See project documentation in the `/docs` directory for implementation examples
- Agent usage examples can be found in historical project documentation

## Contributing

To add new agent personalities or improve existing ones:
1. Base on proven expertise area
2. Define clear responsibilities
3. Create checklists and templates
4. Document success criteria
5. Provide usage examples

---

**Last Updated:** 2025-11-24
**Status:** Production-ready agent personalities
