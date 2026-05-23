import { defineStore } from 'pinia'

interface WorkspaceState {
  activeTeam: string
  requirementSection: string
}

export const useWorkspaceStore = defineStore('workspace', {
  state: (): WorkspaceState => ({
    activeTeam: 'overview',
    requirementSection: 'overview',
  }),
  actions: {
    setActiveTeam(team: string) {
      this.activeTeam = team
    },
    setRequirementSection(section: string) {
      this.requirementSection = section
    },
  },
})
