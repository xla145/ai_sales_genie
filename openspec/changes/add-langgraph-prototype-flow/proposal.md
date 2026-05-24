## Why

The project needs a fast, repeatable flow that turns a user requirement into a generated prototype by orchestrating the existing requirement structuring, system design, and prototype generation skills. A LangGraph-based engine will make the workflow explicit, testable, and easier to parallelize where stage boundaries allow.

## What Changes

- Add a LangGraph-backed prototype workflow that accepts raw user requirements and produces final prototype artifacts.
- Orchestrate the three required stages: requirement intake structuring, system function design/planning, and prototype generation.
- Preserve stage order and artifact validation while enabling parallel execution of independent work inside stages where safe.
- Add a testable prototype flow so the end-to-end path can be verified from requirement input to prototype output.

## Capabilities

### New Capabilities
- `langgraph-prototype-workflow`: Orchestrates raw requirement input through structured requirements, system/page design, and multi-page prototype generation using a LangGraph engine.

### Modified Capabilities

## Impact

- Adds or updates workflow orchestration code for requirement-to-prototype generation.
- Integrates with the existing skill-based stages: `requirement-intake-structuring`, `system-function-design-planning`, and `prototype-generator`.
- Affects local prototype flow scripts/tests and any APIs or services that trigger requirement analysis and prototype generation.
- May add LangGraph runtime dependencies and related test dependencies.
