import { useMock } from '@/config/env'
import { mockApi } from '@/mock/client'
import http from '@/services/http'
import type { CreateRunRequest, LogsResponse, ProjectRun } from '@/types/api'

export const runService = {
  list(projectId: string, sessionId?: string) {
    if (useMock) return mockApi.listRuns(projectId)
    return http.get<ProjectRun[]>(`/projects/${projectId}/runs`, {
      params: sessionId ? { session_id: sessionId } : undefined,
    })
  },
  create(projectId: string, payload: CreateRunRequest) {
    if (useMock) return mockApi.createRun(projectId, payload)
    return http.post<ProjectRun>(`/projects/${projectId}/runs`, payload)
  },
  createForSession(projectId: string, sessionId: string, payload: CreateRunRequest) {
    if (useMock) return mockApi.createRun(projectId, { ...payload, session_id: sessionId })
    return http.post<ProjectRun>(`/projects/${projectId}/sessions/${sessionId}/runs`, payload)
  },
  get(projectId: string, runId: string, sessionId?: string) {
    if (useMock) return mockApi.getRun(projectId, runId)
    return http.get<ProjectRun>(`/projects/${projectId}/runs/${runId}`, {
      params: sessionId ? { session_id: sessionId } : undefined,
    })
  },
  getLogs(projectId: string, runId: string, sessionId?: string) {
    if (useMock) return mockApi.getRunLogs(projectId, runId)
    return http.get<LogsResponse>(`/projects/${projectId}/runs/${runId}/logs`, {
      params: sessionId ? { session_id: sessionId } : undefined,
    })
  },
}
