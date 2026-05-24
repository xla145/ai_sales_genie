## Context

The current prototype workflow is defined as three skill stages: requirement intake structuring, system function design/planning, and prototype generation. The full workflow requires strict stage ordering and artifact checks, while the new requirement emphasizes speed and safe parallel execution.

The change introduces a LangGraph-based orchestration layer that models the workflow as a graph of explicit nodes, state transitions, and validation gates. This keeps the overall process deterministic while allowing independent sub-work to run concurrently inside stages when dependencies are satisfied.

## Goals / Non-Goals

**Goals:**
- Provide a single entry point that accepts raw requirement text and runs the full requirement-to-prototype workflow.
- Use LangGraph to represent workflow stages, state, dependencies, retries, and validation gates.
- Reuse the existing skill contracts and expected artifacts rather than redefining the business process.
- Support safe parallelism for independent work, especially during design/page planning and prototype page generation.
- Make the flow testable end-to-end with clear success and failure states.

**Non-Goals:**
- Replace or rewrite the underlying skill prompts themselves.
- Generate production-ready application code from the prototype.
- Bypass stage validation to improve speed.
- Persist intermediate draft artifacts as final deliverables.

## Decisions

1. **Use LangGraph as the workflow engine.**
   - Rationale: The workflow has explicit stages, dependencies, validation gates, and retry paths that fit graph execution better than a linear script.
   - Alternative considered: Keep a procedural runner script. This is simpler initially but makes branching, validation, and parallel execution harder to reason about and test.

2. **Represent workflow state as a typed object containing input, artifact paths, stage status, validation results, and final output metadata.**
   - Rationale: A shared state object gives each graph node a small, testable contract and makes recovery/debugging easier.
   - Alternative considered: Pass loose dictionaries between functions. This is faster to write but weaker for tests and easier to break as the graph grows.

3. **Keep the three macro stages sequential while allowing concurrency within eligible stage work.**
   - Rationale: The full workflow requires structured requirements before system design and system/page design before prototype generation. Parallelism must not violate these gates.
   - Alternative considered: Run all skills concurrently. This would be faster but could produce inconsistent or incomplete outputs because later stages depend on prior artifacts.

4. **Validate required artifacts after every stage and route failures to targeted repair nodes.**
   - Rationale: The existing workflow depends on concrete files being present and non-empty. Validation nodes make failures observable and fixable.
   - Alternative considered: Validate only at the end. This delays feedback and makes root cause diagnosis harder.

5. **Expose a local test runner before wiring broader product integrations.**
   - Rationale: The first implementation goal is to test that requirement input can produce a prototype quickly and reliably.
   - Alternative considered: Wire directly into backend/API surfaces first. That would increase integration risk before the core flow is proven.

## Risks / Trade-offs

- LangGraph dependency or runtime mismatch → Pin/update dependencies and include a minimal smoke test that imports and runs the graph.
- Parallel generation can create artifact conflicts → Assign deterministic output paths per stage/page and merge only after validation.
- Skill output formats may drift → Keep validators focused on required files, non-empty content, and minimum required sections rather than exact prose.
- Faster execution may hide poor-quality intermediate results → Preserve validation gates and require final validation report before reporting success.
- Local runner may diverge from product APIs → Keep the graph orchestration reusable and make CLI/API entry points thin wrappers around it.

## Migration Plan

1. Add the LangGraph workflow implementation behind a local runner or service entry point.
2. Add tests for graph state transitions, artifact validation, and end-to-end prototype generation on sample input.
3. Wire the graph into the existing prototype flow script for manual validation.
4. Optionally expose the same orchestration through backend APIs after the local flow is stable.
5. Roll back by continuing to use the existing skill-driven/manual flow if graph execution fails.

## Open Questions

- Which exact backend/API entry point should trigger the workflow after the local runner is validated?
- Should final prototype artifacts be stored only locally at first, or uploaded through existing storage once generated?
