export type SessionStatus = 'active' | 'archived'

export interface ProjectSession {
  session_id: string
  project_id: string
  workspace_path: string
  conversation: string
  base_url: string | null
  status: SessionStatus
  metadata: Record<string, unknown>
  hermes_session_ref: string | null
  created_at: string
  updated_at: string
}

export interface SessionInfoResponse {
  session_id: string
  project_id: string
  conversation: string
  base_url: string | null
  workspace_path: string
  hermes_session_ref: string | null
  status: string
}
