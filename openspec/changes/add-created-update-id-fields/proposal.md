## Why

Several persisted business records need consistent creator/updater identifiers for auditability. The current request is to add only `created_id` and `update_id` fields where relevant, without introducing an additional field beyond those two identifiers.

## What Changes

- Add `created_id` and `update_id` persistence fields to relevant database-backed models/tables that currently need audit ownership tracking.
- Remove `owner_user_id` from the affected project-related model/API/storage paths and use `created_id` as the creator/owner user identifier.
- Wire these fields through schemas/services/API flows where records are created or updated so values can be stored and returned consistently.
- Ensure project retrieval includes the user identifier so project access/list/detail queries are scoped to the current user.
- Avoid adding any extra audit field beyond `created_id` and `update_id`.

## Capabilities

### New Capabilities
- `audit-user-identifiers`: Persist and expose creator/updater user identifiers for relevant tables using `created_id` and `update_id`, with project ownership derived from `created_id` instead of `owner_user_id`.

### Modified Capabilities

## Impact

- Database models and migrations/storage initialization for related tables.
- Project model, storage, service, and API handlers currently using or exposing `owner_user_id`.
- Backend domain models, schemas, services, and API handlers that create, update, fetch, or serialize affected records.
- Any frontend/API consumers that display or submit the affected record metadata.
