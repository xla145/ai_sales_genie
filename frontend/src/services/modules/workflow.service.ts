import { useMock } from '@/config/env'
import { mockApi } from '@/mock/client'
import http from '@/services/http'
import type { CreateWorkflowRequest, SubtaskRun, WorkflowRun } from '@/types/workflow'

export const workflowService = {
  create(projectId: string, payload: CreateWorkflowRequest) {
    if (useMock) return mockApi.createWorkflow(projectId, payload)
    return http.post<WorkflowRun>(`/projects/${projectId}/workflows`, payload)
  },
  get(projectId: string, workflowId: string, sessionId?: string) {
    if (useMock) return mockApi.getWorkflow(projectId, workflowId)
    return http.get<WorkflowRun>(`/projects/${projectId}/workflows/${workflowId}`, {
      params: sessionId ? { session_id: sessionId } : undefined,
    })
  },
  listTasks(projectId: string, workflowId: string, sessionId?: string) {
    if (useMock) {
      return mockApi.listRuns(projectId).then(({ data }) => ({
        data: data.map(
          (run, index) =>
            ({
              subtask_id: run.run_id,
              workflow_id: workflowId,
              project_id: projectId,
              session_id: run.session_id,
              phase_id: run.phase_id,
              phase_name: run.phase_name,
              skill_name: run.skill_name,
              title: run.phase_name,
              prompt: run.skill_name,
              input_files: run.input_files,
              expected_outputs: run.expected_outputs,
              status: run.status,
              started_at: run.started_at,
              ended_at: run.ended_at,
              error_message: run.error_message,
              result_summary: run.result_summary,
              log_path: run.log_path,
              order: index,
            }) satisfies SubtaskRun,
        ),
      }))
    }
    return http.get<SubtaskRun[]>(`/projects/${projectId}/workflows/${workflowId}/tasks`, {
      params: sessionId ? { session_id: sessionId } : undefined,
    })
  },
}
