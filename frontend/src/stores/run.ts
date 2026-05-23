import { defineStore } from 'pinia'
import { runService } from '@/services/modules/run.service'
import type { CreateRunRequest, ProjectRun } from '@/types/api'

interface RunState {
  items: ProjectRun[]
  current: ProjectRun | null
  logs: string
  loading: boolean
}

export const useRunStore = defineStore('run', {
  state: (): RunState => ({
    items: [],
    current: null,
    logs: '',
    loading: false,
  }),
  actions: {
    async fetchRuns(projectId: string, sessionId?: string) {
      this.loading = true
      try {
        const { data } = await runService.list(projectId, sessionId)
        this.items = data
      } finally {
        this.loading = false
      }
    },
    async createRun(projectId: string, payload: CreateRunRequest) {
      const { data } = payload.session_id
        ? await runService.createForSession(projectId, payload.session_id, payload)
        : await runService.create(projectId, payload)
      this.items.unshift(data)
      this.current = data
      return data
    },
    async fetchRun(projectId: string, runId: string, sessionId?: string) {
      const { data } = await runService.get(projectId, runId, sessionId)
      this.current = data
      return data
    },
    async fetchLogs(projectId: string, runId: string, sessionId?: string) {
      const { data } = await runService.getLogs(projectId, runId, sessionId)
      this.logs = data.content
      return data.content
    },
  },
})
