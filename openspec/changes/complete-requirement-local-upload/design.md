## Context

The application already has project-scoped requirement analysis data and project attachment persistence in the backend. Requirement intake is not complete because users still need a concrete way to provide local source documents before later analysis steps can consume them.

## Goals / Non-Goals

**Goals:**
- Provide a project-scoped local upload API for requirement source files.
- Persist uploaded file metadata so users can list and remove uploaded files later.
- Store uploaded bytes inside the project workspace, not in a global shared location.
- Scope every upload/list/delete operation to the authenticated user through the existing project ownership checks.
- Add frontend support for selecting local files, showing upload progress/state, and listing/removing uploaded requirement files.

**Non-Goals:**
- Do not implement URL import, cloud drive import, OCR, or document parsing in this change.
- Do not automatically run requirement analysis after upload.
- Do not introduce a new external object storage dependency.
- Do not allow uploads to bypass project ownership checks.

## Decisions

- Store files under a deterministic project workspace subdirectory such as `requirements/uploads/`. This keeps uploaded material close to project artifacts and avoids a new storage service.
- Persist attachment metadata in the existing project attachment model/table where practical, extending it only if implementation reveals missing metadata needed for local uploads. This reuses existing project-scoped persistence rather than creating a parallel upload registry.
- Use authenticated project access as the security boundary. Upload, list, and delete APIs should first resolve the project for the current user, then operate only within that project's upload directory and metadata rows.
- Sanitize generated storage filenames instead of trusting the browser-provided filename. The original filename can be preserved as display metadata, but filesystem paths should be generated server-side.
- Keep supported file validation simple for the first phase: enforce size and extension/content-type allowlists at the API boundary, and return clear validation errors for unsupported files.
- Keep frontend integration inside the requirement intake area so users do not need to leave the intake flow to manage source files.

## Risks / Trade-offs

- Uploaded files may be large → Enforce a backend size limit and show frontend validation/errors before or after upload.
- Browser-provided filenames may contain unsafe path characters → Store with server-generated safe filenames and keep the original name only as metadata.
- Metadata and file bytes can drift if deletion partially fails → Delete metadata and file in a controlled service method, tolerating missing files when metadata exists.
- Users may expect parsing immediately after upload → Make the UI wording clear that this phase only uploads and manages local files.
