## Context

The backend already contains multiple persisted models and service flows for project/runtime data. The requested audit change is intentionally narrow: related tables should gain `created_id` and `update_id`, project ownership should use `created_id` instead of `owner_user_id`, and the implementation must not add a third audit identifier field.

## Goals / Non-Goals

**Goals:**
- Add `created_id` and `update_id` to all related persisted tables/models that require creator/updater tracking.
- Remove `owner_user_id` from affected project-related paths and use `created_id` as the creator/owner identifier.
- Ensure create flows set `created_id` and `update_id` consistently when an authenticated user is available.
- Ensure update flows refresh `update_id` without overwriting `created_id`.
- Ensure project retrieval receives/applies the current user identifier so users only fetch their own scoped project records.
- Keep API serialization and request/response models aligned with the persisted fields.

**Non-Goals:**
- Do not introduce any extra audit user field beyond `created_id` and `update_id`.
- Do not keep `owner_user_id` as an alias, compatibility shim, or duplicate ownership field.
- Do not redesign authentication or user identity resolution.
- Do not backfill historical records beyond safe nullable/default handling required by storage migration.

## Decisions

- Use `created_id` and `update_id` as the canonical field names across database models, domain models, schemas, and API payloads. This avoids aliases that could accidentally preserve or introduce the unwanted extra field.
- Replace `owner_user_id` with `created_id` in project-related persistence, service filtering, and response models instead of maintaining both names.
- Treat both fields as nullable where required for existing data compatibility. New authenticated create/update paths should populate them when user context is available.
- Preserve `created_id` after record creation and update only `update_id` during mutations. This keeps creator attribution stable while reflecting the last modifier.
- Pass the current user identifier into project retrieval/list/detail flows and filter by `created_id` where user scoping is required.
- Apply the change consistently across related tables in one implementation pass rather than adding the fields to only one table, because partial audit metadata would make downstream consumers inconsistent.

## Risks / Trade-offs

- Existing rows may not have creator/updater data → Use nullable columns or safe defaults so migrations do not fail on current data.
- Some internal/background flows may not have an authenticated user → Allow absence of user context rather than fabricating an identifier.
- Related-table scope may be ambiguous → Identify all database-backed models participating in the affected feature area before implementation and keep the change limited to those tables.
