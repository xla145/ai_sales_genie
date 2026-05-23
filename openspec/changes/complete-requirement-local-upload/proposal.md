## Why

Requirement intake needs a usable first path for users to provide source requirement material before downstream analysis can run. The first implementation should support local file upload so users can start from documents already on their machine without depending on external integrations.

## What Changes

- Add local requirement file upload for a project during the requirement intake flow.
- Store uploaded files under the project workspace with metadata that can be listed and reused by later requirement analysis steps.
- Expose backend APIs for uploading, listing, and removing locally uploaded requirement files scoped to the current user and project.
- Add frontend UI/service support for selecting local files, uploading them, displaying upload state, and showing uploaded files in the requirement intake area.
- Keep this first phase limited to local upload; external URL import, cloud drive import, OCR, and semantic parsing can be handled later.

## Capabilities

### New Capabilities
- `requirement-local-upload`: Users can upload local requirement files to a project, manage the uploaded file list, and keep uploads scoped to their own projects.

### Modified Capabilities

## Impact

- Project API routes and service/storage logic for project-scoped requirement attachments.
- Requirement intake frontend views/components, project service module, and related types.
- Project workspace file storage and persisted attachment metadata.
- Tests or verification covering upload validation, user scoping, listing, and deletion.
