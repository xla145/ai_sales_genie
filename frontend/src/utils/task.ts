import type { ProjectRun } from '@/types/run'

export type TaskDisplayStatus = 'pending' | 'running' | 'done' | 'error'

export interface TaskDisplayItem {
  id: string
  title: string
  description: string
  status: TaskDisplayStatus
  module: string
  assignee: string
  createdAt: string
  startedAt?: string
  finishedAt?: string
  durationMs?: number
  tags: string[]
  runId: string
  logPath?: string
}

const PHASE_MODULE_MAP: Record<string, string> = {
  phase1: '需求分析',
  phase2: '方案设计',
  phase3: '方案设计',
}

const STATUS_MAP: Record<ProjectRun['status'], TaskDisplayStatus> = {
  pending: 'pending',
  running: 'running',
  success: 'done',
  failed: 'error',
}

export function mapRunToTask(run: ProjectRun): TaskDisplayItem {
  const startedAt = run.started_at
  const finishedAt = run.ended_at ?? undefined
  const durationMs =
    startedAt && finishedAt ? new Date(finishedAt).getTime() - new Date(startedAt).getTime() : undefined

  return {
    id: run.run_id,
    runId: run.run_id,
    title: run.phase_name,
    description: run.skill_name,
    status: STATUS_MAP[run.status],
    module: PHASE_MODULE_MAP[run.phase_id] ?? run.phase_name,
    assignee: 'AI 助手',
    createdAt: run.started_at,
    startedAt,
    finishedAt,
    durationMs,
    tags: [run.phase_id, run.skill_name],
    logPath: run.log_path,
  }
}

export function mapRunsToTasks(runs: ProjectRun[]): TaskDisplayItem[] {
  return runs.map(mapRunToTask)
}
