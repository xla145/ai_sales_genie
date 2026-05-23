## ADDED Requirements

### Requirement: Upload local requirement files
The system SHALL allow an authenticated user to upload local requirement source files to a project they can access.

#### Scenario: Successful local upload
- **WHEN** an authenticated user uploads a supported local file to one of their projects
- **THEN** the system stores the file inside that project's workspace and records metadata including original filename, stored path, size, and upload time

#### Scenario: Upload to another user's project
- **WHEN** an authenticated user attempts to upload a file to a project they do not own
- **THEN** the system rejects the request as not found or unauthorized and does not store the file

### Requirement: Validate uploaded files
The system MUST validate local requirement uploads at the API boundary before storing file bytes.

#### Scenario: Unsupported file type
- **WHEN** a user uploads a file whose extension or content type is not supported for requirement intake
- **THEN** the system rejects the upload with a validation error and does not persist metadata

#### Scenario: Oversized file
- **WHEN** a user uploads a file larger than the configured local upload limit
- **THEN** the system rejects the upload with a validation error and does not persist metadata

### Requirement: List uploaded requirement files
The system SHALL allow an authenticated user to list local requirement files uploaded to one of their projects.

#### Scenario: Listing project uploads
- **WHEN** an authenticated user opens the requirement intake area for their project
- **THEN** the system returns the uploaded local file metadata for that project only

### Requirement: Delete uploaded requirement files
The system SHALL allow an authenticated user to remove a previously uploaded local requirement file from one of their projects.

#### Scenario: Successful upload deletion
- **WHEN** an authenticated user deletes an uploaded requirement file from their project
- **THEN** the system removes the metadata and deletes the stored file when it exists

#### Scenario: Deleting another user's upload
- **WHEN** an authenticated user attempts to delete an uploaded file from a project they do not own
- **THEN** the system rejects the request as not found or unauthorized and leaves the file and metadata unchanged

### Requirement: Provide requirement intake upload UI
The system SHALL provide frontend controls in the requirement intake flow for uploading and managing local requirement files.

#### Scenario: User uploads from the browser
- **WHEN** a user selects a supported local file in the requirement intake UI
- **THEN** the UI uploads the file to the current project, shows upload state, and refreshes the uploaded file list after success

#### Scenario: User removes an uploaded file
- **WHEN** a user removes a file from the uploaded file list
- **THEN** the UI calls the delete API and removes the file from the displayed list after success
