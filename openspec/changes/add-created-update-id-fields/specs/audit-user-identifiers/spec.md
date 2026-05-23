## ADDED Requirements

### Requirement: Persist audit user identifiers
The system SHALL persist `created_id` and `update_id` fields on all related tables that require creator and updater attribution.

#### Scenario: Creating an audited record
- **WHEN** an authenticated user creates a record in a related audited table
- **THEN** the system stores that user's identifier in both `created_id` and `update_id`

#### Scenario: Updating an audited record
- **WHEN** an authenticated user updates a record in a related audited table
- **THEN** the system preserves the existing `created_id` and stores that user's identifier in `update_id`

### Requirement: Exclude unrelated audit fields
The system MUST NOT add or expose any additional audit user identifier field beyond `created_id` and `update_id` for this change.

#### Scenario: Serializing audited records
- **WHEN** the system returns an audited record through an API response
- **THEN** the response includes `created_id` and `update_id` when those fields are part of the resource model and does not include an extra audit identifier field

#### Scenario: Removing owner user field
- **WHEN** the affected project-related models, storage rows, or API responses represent creator ownership
- **THEN** the system uses `created_id` and does not expose or persist `owner_user_id`

### Requirement: Scope project retrieval by user identifier
The system SHALL include the current user identifier when retrieving project records that are scoped to a user.

#### Scenario: Listing current user's projects
- **WHEN** an authenticated user requests project records
- **THEN** the system filters project retrieval using that user's identifier against `created_id`

#### Scenario: Fetching a project detail
- **WHEN** an authenticated user requests a specific project record
- **THEN** the system includes that user's identifier in the lookup so a project created by another user is not returned

### Requirement: Support existing records safely
The system SHALL support existing persisted records that do not yet have creator or updater identifiers.

#### Scenario: Reading existing data after migration
- **WHEN** an existing record has no historical creator or updater identifier
- **THEN** the system can read and serialize the record without failing because `created_id` or `update_id` is absent or null
