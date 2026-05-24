import { defineStore } from 'pinia'
import { projectService } from '@/services/modules/project.service'
import type { CreateProjectRequest, Project, RequirementAttachmentItem, RunPhase1Request, RunPhase1Response, UpdateProjectOverviewRequest, UpdateProjectRequest, UpdateRequirementAnalysisRequest } from '@/types/api'

interface ProjectState {
  items: Project[]
  current: Project | null
  loading: boolean
}

const syncProjectState = (items: Project[], current: Project | null, projectId: string, data: Project) => ({
  items: items.map((item) => (item.project_id === projectId ? data : item)),
  current: current?.project_id === projectId ? data : current,
})

export const useProjectStore = defineStore('project', {
  state: (): ProjectState => ({
    items: [],
    current: null,
    loading: false,
  }),
  actions: {
    async fetchProjects() {
      this.loading = true
      try {
        const { data } = await projectService.list()
        this.items = data
      } finally {
        this.loading = false
      }
    },
    async fetchProject(projectId: string) {
      const { data } = await projectService.get(projectId)
      this.current = data
      return data
    },
    async createProject(payload: CreateProjectRequest) {
      const { data } = await projectService.create(payload)
      this.items.unshift(data)
      return data
    },
    async updateProject(projectId: string, payload: UpdateProjectRequest) {
      const { data } = await projectService.update(projectId, payload)
      const next = syncProjectState(this.items, this.current, projectId, data)
      this.items = next.items
      this.current = next.current
      return data
    },
    async updateProjectOverview(projectId: string, payload: UpdateProjectOverviewRequest) {
      const { data } = await projectService.updateOverview(projectId, payload)
      const next = syncProjectState(this.items, this.current, projectId, data)
      this.items = next.items
      this.current = next.current
      return data
    },
    async updateRequirementAnalysis(projectId: string, payload: UpdateRequirementAnalysisRequest) {
      const { data } = await projectService.updateRequirementAnalysis(projectId, payload)
      const next = syncProjectState(this.items, this.current, projectId, data)
      this.items = next.items
      this.current = next.current
      return data
    },
    async listRequirementUploads(projectId: string) {
      const { data } = await projectService.listRequirementUploads(projectId)
      return data
    },
    async uploadRequirementFile(projectId: string, file: File) {
      const { data } = await projectService.uploadRequirementFile(projectId, file)
      this.mergeRequirementAttachments(projectId, [data])
      return data
    },
    async deleteRequirementUpload(projectId: string, uploadId: string) {
      await projectService.deleteRequirementUpload(projectId, uploadId)
      this.mergeRequirementAttachments(projectId, undefined, uploadId)
    },
    mergeRequirementAttachments(projectId: string, added?: RequirementAttachmentItem[], removedId?: string) {
      const apply = (project: Project) => {
        const currentAnalysis = project.config.requirementAnalysis
        if (!currentAnalysis) return project
        const filtered = currentAnalysis.attachments.filter((item) => !removedId || item.id !== removedId)
        return {
          ...project,
          config: {
            ...project.config,
            requirementAnalysis: {
              ...currentAnalysis,
              attachments: [...(added ?? []), ...filtered],
            },
          },
        }
      }
      this.items = this.items.map((item) => (item.project_id === projectId ? apply(item) : item))
      if (this.current?.project_id === projectId) {
        this.current = apply(this.current)
      }
    },
    async runPhase1(projectId: string, payload: RunPhase1Request) {
      const { data } = await projectService.runPhase1(projectId, payload)
      const next = syncProjectState(this.items, this.current, projectId, data.project)
      this.items = next.items
      this.current = next.current
      return data
    },
    async deleteProject(projectId: string) {
      await projectService.remove(projectId)
      this.items = this.items.filter((item) => item.project_id !== projectId)
      if (this.current?.project_id === projectId) {
        this.current = null
      }
    },
  },
})
