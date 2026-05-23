export type PhaseId = 'phase1' | 'phase2' | 'phase3'
export type RunStatus = 'pending' | 'running' | 'success' | 'failed'

export interface ProjectRun {
  run_id: string
  project_id: string
  session_id: string
  phase_id: PhaseId
  phase_name: string
  skill_name: string
  input_files: string[]
  expected_outputs: string[]
  status: RunStatus
  started_at: string
  ended_at: string | null
  error_message: string | null
  result_summary: Record<string, unknown> | null
  log_path: string
}

export interface CreateRunRequest {
  session_id?: string | null
  phase_id: PhaseId
  phase_name: string
  skill_name: string
  input_files?: string[]
  expected_outputs?: string[]
  prompt?: string | null
  fail?: boolean
  sleep_seconds?: number
}

export interface LogsResponse {
  content: string
}
