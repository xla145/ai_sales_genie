## ADDED Requirements

### Requirement: Phase1 result must map to requirement analysis page fields
The system SHALL transform the first-phase requirement analysis output into the same `requirementAnalysis` structure used by the requirement analysis page, so the returned project data can be rendered and edited without additional frontend transformation.

#### Scenario: Phase1 run returns page-compatible structure
- **WHEN** `POST /projects/{project_id}/phase1/run` completes successfully
- **THEN** the returned project configuration MUST include a `requirementAnalysis` object
- **AND** the object MUST contain the sections `basic`, `core`, `scenarios`, `functions`, `risks`, `pending`, `attachments`, and `supplement`

#### Scenario: Existing page field groups are preserved
- **WHEN** the system writes the phase1 structured result into `requirementAnalysis`
- **THEN** `functions` MUST be grouped as `functionDesc`, `nonFunction`, and `constraints`
- **AND** the field names within each group MUST remain compatible with the current requirement analysis page

### Requirement: Basic and core information must be mapped by semantic meaning
The system SHALL map first-phase textual content into fixed basic and core fields by section meaning, not only by exact literal title matching.

#### Scenario: Basic information is mapped into fixed fields
- **WHEN** phase1 output contains project name, summary, industry, project type, or keywords
- **THEN** the system MUST write them into `basic.projectName`, `basic.projectSummary`, `basic.industry`, `basic.projectType`, and `basic.keywords` respectively

#### Scenario: Core information is mapped into fixed fields
- **WHEN** phase1 output contains project background, goals, users, or pain points using exact or semantically equivalent headings
- **THEN** the system MUST write them into `core.background`, `core.goal`, `core.users`, and `core.painPoints`

#### Scenario: Missing core fields remain editable
- **WHEN** a target basic or core field has no reliable source in the phase1 output
- **THEN** the system MUST keep that field empty or at its default value
- **AND** it MUST NOT fabricate content for the field

### Requirement: Scenario items must be normalized as editable list entries
The system SHALL convert scenario-related content into normalized scenario list items that match the page editing model.

#### Scenario: Multiple scenarios become structured entries
- **WHEN** phase1 output contains multiple business scenarios or诉求项
- **THEN** the system MUST create one `scenarios[]` entry per scenario
- **AND** each entry MUST contain `key`, `title`, `description`, and `flow`

#### Scenario: Scenario titles are normalized for display
- **WHEN** scenario entries are created from phase1 output
- **THEN** the system MUST assign display titles in sequence such as `场景1`, `场景2`
- **AND** it MUST NOT depend on the original markdown numbering to preserve page usability

#### Scenario: Partial scenario content is retained
- **WHEN** a scenario only provides descriptive text or only provides a process outline
- **THEN** the system MUST store the available text in the matching scenario fields
- **AND** it MAY leave the missing field empty

### Requirement: Functional content must map into fixed requirement groups
The system SHALL classify functional content into the page’s fixed groups for explicit functions, non-functional requirements, and constraints.

#### Scenario: Explicit and potential functions map into function description group
- **WHEN** phase1 output contains explicit core functions, potential functions, technical selections, technical architecture, or dependent systems
- **THEN** the system MUST write them into the corresponding keys under `functions.functionDesc`

#### Scenario: Non-functional requirements are written without synthetic constraints
- **WHEN** phase1 output contains performance, usability, security, or compatibility requirements
- **THEN** the system MUST write them into the corresponding keys under `functions.nonFunction`
- **AND** it MUST NOT automatically copy the same text into `functions.constraints`

#### Scenario: Constraints are only filled when clear limiting conditions exist
- **WHEN** phase1 output contains explicit limiting conditions, boundaries, or restrictions for performance, usability, security, or compatibility
- **THEN** the system MUST write them into the corresponding keys under `functions.constraints`

### Requirement: Risk items must be normalized into structured risk records
The system SHALL convert risk-related content into editable risk items with consistent default behavior.

#### Scenario: Risk list is normalized
- **WHEN** phase1 output contains one or more risks, concerns, or blockers
- **THEN** the system MUST create one `risks[]` entry per risk
- **AND** each entry MUST contain `key`, `title`, `level`, `description`, `impact`, and `strategy`

#### Scenario: Missing risk level uses default value
- **WHEN** a risk item does not include an explicit severity level
- **THEN** the system MUST assign the page default level
- **AND** it MUST still preserve the risk description

#### Scenario: Risk titles are generated consistently
- **WHEN** risk entries are created from phase1 output
- **THEN** the system MUST assign sequential display titles such as `风险点1`, `风险点2`

### Requirement: Pending and supplemental information must capture unresolved content
The system SHALL route unresolved, uncertain, or unmapped content into pending confirmation or supplemental fields instead of forcing it into primary business fields.

#### Scenario: Unknown or unresolved content goes to pending section
- **WHEN** phase1 output includes unanswered questions, missing information, or items that require stakeholder confirmation
- **THEN** the system MUST write that content into `pending.unknownInfo`, `pending.assumptions`, or `pending.items` as appropriate

#### Scenario: Pending checklist items are initialized for manual follow-up
- **WHEN** the system creates `pending.items[]` entries from phase1 output
- **THEN** each entry MUST contain `title`, `text`, and `checked`
- **AND** `checked` MUST default to `false`

#### Scenario: Supplemental notes store unmapped but useful details
- **WHEN** phase1 output contains information that is useful for later design but does not belong to a stable page field
- **THEN** the system MUST store it in `supplement.notes`
- **AND** it MUST NOT overwrite confirmed primary fields with that content

### Requirement: Phase1 automation must not fabricate attachment records
The system SHALL avoid generating attachment records from plain textual analysis unless attachment metadata is explicitly available.

#### Scenario: No attachment metadata is present
- **WHEN** phase1 output is derived only from text prompts and contains no explicit attachment records
- **THEN** the system MUST leave `attachments` empty or preserve existing valid attachment records
- **AND** it MUST NOT create fake file names or upload records
