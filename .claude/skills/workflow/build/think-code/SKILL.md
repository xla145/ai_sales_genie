---
name: think-code
description: "Research → Plan → Annotate → Implement workflow for programming tasks. Never writes code until a written plan is reviewed and approved."
---

# Think Before You Code

**Core Rule: DO NOT write any implementation code until the user explicitly approves the plan.**

## Phase 1: Research

**Reading standard — these words mean exactly what they say:**
- Read files **deeply** — every function, every import, not headers only
- Understand **in great detail** how data flows between layers
- Grasp the **intricacies** of edge cases, error paths, and implicit contracts

Steps:
1. Read all relevant files in full — no skimming
2. Use `Grep` / `Glob` to find: callers, related modules, dependencies, test files
3. Trace call chains: entry points → service → model → DB
4. Identify: data shapes at every boundary, constraints, non-obvious assumptions
5. Write all findings into the `## Research Summary` section of `PLAN.md`

See format: `references/plan-template.md`

## Phase 2: Planning

Append `## Implementation Plan` to `PLAN.md` — code sketches only, no real implementation.

See format: `references/plan-template.md`

Then output: **"PLAN READY — review PLAN.md, annotate corrections, say 'go' when ready."**

**Stop. Wait for user.**

## Phase 3: Annotation Cycle

User edits `PLAN.md` with inline notes. Typical annotations:
- Parameter constraints: `// max 100 chars, not unlimited`
- API corrections: `// use .get_by_id(), not session.query()`
- Schema changes: `// add status field, remove priority`
- Rejections: `// SKIP — out of scope`
- Domain knowledge: `// this runs in a transaction, must be atomic`

After receiving annotated plan:
1. Re-read every annotation carefully
2. Update PLAN.md to reflect all corrections
3. Confirm changes: `"Updated: [list of changes made]"`
4. **Repeat until user says go** — expect 1–6 cycles

**CRITICAL: Never start implementing during annotation cycles. The guard phrase is "don't implement yet".**

## Phase 4: Implementation

**Trigger**: user says `"go"` / `"implement"` / `"approved"`

1. Read final `PLAN.md` — every step, every constraint
2. Execute all steps in order — **do not stop until all tasks are completed**
3. Mark each step complete in PLAN.md as you finish it
4. Run type checks / linter **continuously** after each file change — fix failures before moving on
5. Accept terse corrections mid-flight and apply immediately without explanation
6. For visual/structural consistency, reference existing code: *"this must match [existing component] exactly"*
7. Summarize all changes when done

**During implementation — accept single-sentence corrections:**
- `"All I want now is X. Revert everything else."`
- `"This must match [existing file] exactly."`
- `"Do not touch [interface]."`

**Skip to Phase 4** for trivial 1-line changes.
