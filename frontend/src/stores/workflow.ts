import { defineStore } from 'pinia'
import { workflowService } from '@/services/modules/workflow.service'
import type { CreateWorkflowRequest, SubtaskRun, WorkflowRun } from '@/types/workflow'

interface WorkflowState {
  current: WorkflowRun | null
  subtasks: SubtaskRun[]
  loading: boolean
}

export const useWorkflowStore = defineStore('workflow', {
  state: (): WorkflowState => ({
    current: null,
    subtasks: [],
    loading: false,
  }),
  actions: {
    async createWorkflow(projectId: string, payload: CreateWorkflowRequest) {
      this.loading = true
      try {
        const { data } = await workflowService.create(projectId, payload)
        this.current = data
        return data
      } finally {
        this.loading = false
      }
    },
    async fetchWorkflow(projectId: string, workflowId: string, sessionId?: string) {
      this.loading = true
      try {
        const { data } = await workflowService.get(projectId, workflowId, sessionId)
        this.current = data
        return data
      } finally {
        this.loading = false
      }
    },
    async fetchSubtasks(projectId: string, workflowId: string, sessionId?: string) {
      const { data } = await workflowService.listTasks(projectId, workflowId, sessionId)
      this.subtasks = data
      return data
    },
    reset() {
      this.current = null
      this.subtasks = []
    },
  },
})
