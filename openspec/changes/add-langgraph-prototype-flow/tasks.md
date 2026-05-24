## 1. Workflow Foundation

- [x] 1.1 Add or confirm LangGraph dependency and import smoke test coverage.
- [x] 1.2 Define the workflow state model with raw input, stage statuses, artifact paths, validation results, and final output metadata.
- [x] 1.3 Create the LangGraph workflow module with nodes for requirement intake, system design, prototype generation, validation, and completion.

## 2. Stage Orchestration

- [x] 2.1 Implement the requirement intake node to run the existing requirement structuring stage and record `需求结构化.md`.
- [x] 2.2 Implement the system design node to run the existing function/page planning stage after structured requirements pass validation.
- [x] 2.3 Implement the prototype generation node to run after system design validation and produce the required prototype directory.
- [x] 2.4 Add safe parallel execution for independent page-level or artifact-level work without conflicting output paths.

## 3. Validation and Error Handling

- [x] 3.1 Implement validators for required stage files, required directories, non-empty content, and final prototype assets.
- [x] 3.2 Route validation failures to explicit failed or repair-needed workflow states without running dependent stages.
- [x] 3.3 Expose run status, artifact paths, validation results, and final output metadata to callers.

## 4. Runner and Integration

- [x] 4.1 Add a local executable runner that accepts requirement input and invokes the LangGraph workflow.
- [x] 4.2 Update the existing prototype flow script or service entry point to use the LangGraph workflow.
- [x] 4.3 Ensure only final deliverables are persisted or exposed as workflow outputs.

## 5. Tests and Verification

- [x] 5.1 Add unit tests for workflow state transitions and stage gate ordering.
- [x] 5.2 Add tests for artifact validators covering missing, empty, and valid outputs.
- [x] 5.3 Add an end-to-end smoke test that starts from sample requirement text and verifies final prototype artifacts.
- [x] 5.4 Run the local workflow manually and confirm generated prototype pages, shared assets, mock data, generation report, and validation report exist.
