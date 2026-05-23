import type { PhaseId, RunStatus } from './run'

export type WorkflowStatus = 'pending' | 'running' | 'success' | 'failed' | 'blocked'

export interface WorkflowPhaseState {
  phase_id: PhaseId
  phase_name: string
  skill_name: string
  status: WorkflowStatus
  input_files: string[]
  expected_outputs: string[]
  subtask_ids: string[]
  result_summary: Record<string, unknown> | null
  error_message: string | null
  started_at: string | null
  ended_at: string | null
  input_tokens: number
  output_tokens: number
}

export interface WorkflowRun {
  workflow_id: string
  project_id: string
  session_id: string
  status: WorkflowStatus
  phases: WorkflowPhaseState[]
  current_phase_id: PhaseId | null
  created_at: string
  started_at: string | null
  ended_at: string | null
  error_message: string | null
  result_summary: Record<string, unknown> | null
  log_path: string
}

export interface SubtaskRun {
  subtask_id: string
  workflow_id: string
  project_id: string
  session_id: string
  phase_id: PhaseId
  phase_name: string
  skill_name: string
  title: string
  prompt: string
  input_files: string[]
  expected_outputs: string[]
  status: RunStatus
  started_at: string | null
  ended_at: string | null
  error_message: string | null
  result_summary: Record<string, unknown> | null
  log_path: string
  order: number
}

export interface CreateWorkflowRequest {
  session_id?: string | null
  prompt?: string | null
  max_parallel_subagents?: number
  fail?: boolean
  sleep_seconds?: number
}
