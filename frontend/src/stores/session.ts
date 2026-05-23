import { defineStore } from 'pinia'
import { sessionService } from '@/services/modules/session.service'
import type { ProjectSession } from '@/types/api'

interface SessionState {
  items: ProjectSession[]
  current: ProjectSession | null
  loading: boolean
}

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
    items: [],
    current: null,
    loading: false,
  }),
  actions: {
    async fetchSessions(projectId: string) {
      this.loading = true
      try {
        const { data } = await sessionService.list(projectId)
        this.items = data
        this.current = data[0] ?? null
      } finally {
        this.loading = false
      }
    },
    async createSession(projectId: string) {
      const { data } = await sessionService.create(projectId)
      this.items.unshift(data)
      this.current = data
      return data
    },
    async resumeSession(projectId: string, sessionId: string) {
      const { data } = await sessionService.resume(projectId, sessionId)
      this.current = data
      return data
    },
    setCurrent(session: ProjectSession | null) {
      this.current = session
    },
  },
})
