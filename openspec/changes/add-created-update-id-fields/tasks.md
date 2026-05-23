## 1. Scope Audit

- [x] 1.1 Identify all related database-backed models/tables that need `created_id` and `update_id`.
- [x] 1.2 Identify every affected use of `owner_user_id` and plan replacement with `created_id` instead of propagation.
- [x] 1.3 Identify project list/detail retrieval paths that need the current user identifier added to the lookup.

## 2. Persistence Model Updates

- [x] 2.1 Add nullable `created_id` and `update_id` columns/fields to each related storage model/table.
- [x] 2.2 Update database initialization or migration logic so existing records remain readable.
- [x] 2.3 Remove `owner_user_id` from affected project-related storage/model/schema definitions and replace ownership references with `created_id`.
- [x] 2.4 Remove or avoid any extra audit user identifier field beyond `created_id` and `update_id`.

## 3. Backend Flow Updates

- [x] 3.1 Update create flows to set both `created_id` and `update_id` from authenticated user context when available.
- [x] 3.2 Update mutation flows to preserve `created_id` and refresh only `update_id` from authenticated user context when available.
- [x] 3.3 Update project list/detail retrieval to accept the current user identifier and filter/look up projects by `created_id`.
- [x] 3.4 Align domain models, request schemas, response schemas, and serialization with the two canonical fields.

## 4. Verification

- [x] 4.1 Add or update backend tests for create/update/read behavior of `created_id` and `update_id`.
- [x] 4.2 Add or update tests confirming project retrieval is scoped by the current user identifier through `created_id`.
- [x] 4.3 Run relevant test or verification commands to confirm `owner_user_id` and any extra audit identifier field are not exposed.
