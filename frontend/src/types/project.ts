export type ProjectStatus = 'created' | 'running' | 'success' | 'failed' | 'stopped'

export interface RequirementBasicItem {
  projectName: string
  projectSummary: string
  industry: string
  projectType: string
  keywords: string
}

export interface RequirementCoreItem {
  background: string
  goal: string
  users: string
  painPoints: string
}

export interface RequirementScenarioItem {
  key: string
  title: string
  description: string
  flow: string
}

export interface RequirementFunctionFieldGroup {
  [fieldLabel: string]: string
}

export interface RequirementFunctions {
  functionDesc: RequirementFunctionFieldGroup
  nonFunction: RequirementFunctionFieldGroup
  constraints: RequirementFunctionFieldGroup
}

export interface RequirementRiskItem {
  key: string
  title: string
  level: string
  description: string
  impact: string
  strategy: string
}

export interface RequirementPendingItem {
  title: string
  text: string
  checked: boolean
}

export interface RequirementPending {
  unknownInfo: string
  assumptions: string
  items: RequirementPendingItem[]
}

export interface RequirementAttachmentItem {
  name: string
  meta: string
}

export interface RequirementSupplement {
  notes: string
}

export interface RequirementAnalysis {
  basic: RequirementBasicItem
  core: RequirementCoreItem
  scenarios: RequirementScenarioItem[]
  functions: RequirementFunctions
  risks: RequirementRiskItem[]
  pending: RequirementPending
  attachments: RequirementAttachmentItem[]
  supplement: RequirementSupplement
}

export interface UpdateProjectOverviewRequest {
  name?: string
  description?: string | null
  clientInfo?: string
  province?: string
  city?: string
  stage?: string
  industry?: string
}

export interface UpdateRequirementAnalysisRequest {
  basic?: Partial<RequirementBasicItem>
  core?: Partial<RequirementCoreItem>
  scenarios?: RequirementScenarioItem[]
  functions?: Partial<RequirementFunctions>
  risks?: RequirementRiskItem[]
  pending?: Partial<RequirementPending>
  attachments?: RequirementAttachmentItem[]
  supplement?: Partial<RequirementSupplement>
}

export interface ProjectConfig extends Record<string, unknown> {
  requirementAnalysis?: RequirementAnalysis
}

export interface Project {
  project_id: string
  created_id: string | null
  update_id: string | null
  name: string
  description: string | null
  status: ProjectStatus
  workspace_path: string
  current_session_id: string | null
  config: ProjectConfig
  created_at: string
  updated_at: string
}

export interface RunPhase1Request {
  prompt: string
  session_id?: string | null
}

export interface RunPhase1Response {
  project: Project
  run_id: string
  session_id: string
  status: string
  result_summary: Record<string, unknown> | null
}

export interface CreateProjectRequest {
  name: string
  description?: string | null
  config?: ProjectConfig
}

export interface UpdateProjectRequest {
  name: string
  description?: string | null
  config?: ProjectConfig
}
