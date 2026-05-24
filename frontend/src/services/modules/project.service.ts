import { useMock } from '@/config/env'
import { mockApi } from '@/mock/client'
import http from '@/services/http'
import type { CreateProjectRequest, Project, RequirementAttachmentItem, RunPhase1Request, RunPhase1Response, UpdateProjectOverviewRequest, UpdateProjectRequest, UpdateRequirementAnalysisRequest } from '@/types/api'

export const projectService = {
  list() {
    if (useMock) return mockApi.listProjects()
    return http.get<Project[]>('/projects')
  },
  get(projectId: string) {
    if (useMock) return mockApi.getProject(projectId)
    return http.get<Project>(`/projects/${projectId}`)
  },
  create(payload: CreateProjectRequest) {
    if (useMock) return mockApi.createProject(payload)
    return http.post<Project>('/projects', payload)
  },
  update(projectId: string, payload: UpdateProjectRequest) {
    if (useMock) return mockApi.updateProject(projectId, payload)
    return http.put<Project>(`/projects/${projectId}`, payload)
  },
  updateOverview(projectId: string, payload: UpdateProjectOverviewRequest) {
    if (useMock) return mockApi.updateOverview(projectId, payload)
    return http.patch<Project>(`/projects/${projectId}/overview`, payload)
  },
  updateRequirementAnalysis(projectId: string, payload: UpdateRequirementAnalysisRequest) {
    if (useMock) return mockApi.updateRequirementAnalysis(projectId, payload)
    return http.patch<Project>(`/projects/${projectId}/requirement-analysis`, payload)
  },
  listRequirementUploads(projectId: string) {
    if (useMock) return mockApi.listRequirementUploads(projectId)
    return http.get<RequirementAttachmentItem[]>(`/projects/${projectId}/requirement-uploads`)
  },
  uploadRequirementFile(projectId: string, file: File) {
    if (useMock) return mockApi.uploadRequirementFile(projectId, file)
    const formData = new FormData()
    formData.append('file', file)
    return http.post<RequirementAttachmentItem>(`/projects/${projectId}/requirement-uploads`, formData)
  },
  deleteRequirementUpload(projectId: string, uploadId: string) {
    if (useMock) return mockApi.deleteRequirementUpload(projectId, uploadId)
    return http.delete(`/projects/${projectId}/requirement-uploads/${uploadId}`)
  },
  runPhase1(projectId: string, payload: RunPhase1Request) {
    if (useMock) return mockApi.runPhase1(projectId, payload)
    return http.post<RunPhase1Response>(`/projects/${projectId}/phase1/run`, payload)
  },
  remove(projectId: string) {
    if (useMock) return mockApi.deleteProject(projectId)
    return http.delete(`/projects/${projectId}`)
  },
}
