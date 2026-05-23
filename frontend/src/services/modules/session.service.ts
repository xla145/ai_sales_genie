import { useMock } from '@/config/env'
import { mockApi } from '@/mock/client'
import http from '@/services/http'
import type { ProjectSession, SessionInfoResponse } from '@/types/api'

export const sessionService = {
  list(projectId: string) {
    if (useMock) return mockApi.listSessions(projectId)
    return http.get<ProjectSession[]>(`/projects/${projectId}/sessions`)
  },
  create(projectId: string) {
    if (useMock) return mockApi.createSession(projectId)
    return http.post<ProjectSession>(`/projects/${projectId}/sessions`)
  },
  getInfo(projectId: string, sessionId: string) {
    if (useMock) {
      return mockApi.resumeSession(projectId, sessionId).then(({ data }) => ({
        data: {
          session_id: data.session_id,
          project_id: data.project_id,
          conversation: data.conversation,
          base_url: data.base_url,
          workspace_path: data.workspace_path,
          hermes_session_ref: data.hermes_session_ref,
          status: data.status,
        } satisfies SessionInfoResponse,
      }))
    }
    return http.get<SessionInfoResponse>(`/projects/${projectId}/sessions/${sessionId}/info`)
  },
  resume(projectId: string, sessionId: string) {
    if (useMock) return mockApi.resumeSession(projectId, sessionId)
    return http.post<ProjectSession>(`/projects/${projectId}/sessions/${sessionId}/resume`)
  },
}
