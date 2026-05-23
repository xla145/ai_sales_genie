import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { useRunStore } from '@/stores/run'
import { useSessionStore } from '@/stores/session'

export function useProjectContext() {
  const route = useRoute()
  const projectStore = useProjectStore()
  const sessionStore = useSessionStore()
  const runStore = useRunStore()

  const projectId = () => String(route.params.projectId ?? '')

  const bootstrap = async () => {
    const id = projectId()
    if (!id) return

    await projectStore.fetchProject(id)
    await Promise.all([
      sessionStore.fetchSessions(id),
      runStore.fetchRuns(id, projectStore.current?.current_session_id ?? undefined),
    ])
  }

  onMounted(bootstrap)
  watch(
    () => route.params.projectId,
    () => {
      bootstrap()
    },
  )

  return {
    projectId,
    bootstrap,
  }
}
