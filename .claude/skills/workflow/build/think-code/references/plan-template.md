# PLAN.md Template

> SCOPE LOCK: [one sentence — exactly what will be built]

## Research Summary
- `path/to/file.py` — [what it does / what's relevant]
- Key finding: [constraint / pattern / dependency]
- Reference impl: [existing code to follow as template]

---

## Implementation Plan

### Overview
[1-2 sentences: what will be built and why]

### Constraints (DO NOT VIOLATE)
- `function/class/endpoint` — [why it's frozen, what breaks if changed]

### Steps

#### Step 1: [verb + what]
- **File**: `path/to/file.py`
- **Change**: add / modify / delete [what]
- **Sketch**: `def foo(x: T) -> R: ...`
- [ ] done

#### Step 2: ...
- [ ] done

### Files to modify / create
| File | Change | Why |
|------|--------|-----|
| `path/a.py` | modify | [reason] |
| `path/b.py` | create | [reason] |

### What will NOT change
- [explicit scope boundary — prevents scope creep]
- [protected interface — callers depend on this]

### Risks / trade-offs
- [what could go wrong, alternatives considered]

---

## Deferred
- [item removed from current scope — consider later]
