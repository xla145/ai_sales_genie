import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '@/views/auth/LoginView.vue'
import ProjectListView from '@/views/projects/ProjectListView.vue'
import ProjectOverviewView from '@/views/workspace/ProjectOverviewView.vue'
import RequirementInputView from '@/views/workspace/RequirementInputView.vue'
import RequirementAnalysisView from '@/views/workspace/RequirementAnalysisView.vue'
import SolutionDesignView from '@/views/workspace/SolutionDesignView.vue'
import IntelligenceAnalysisView from '@/views/workspace/IntelligenceAnalysisView.vue'
import PricingView from '@/views/workspace/PricingView.vue'
import DevelopmentView from '@/views/workspace/DevelopmentView.vue'
import SystemConfigView from '@/views/workspace/SystemConfigView.vue'
import TaskListView from '@/views/workspace/TaskListView.vue'
import { useMock } from '@/config/env'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/',
      redirect: '/projects',
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectListView,
    },
    {
      path: '/projects/:projectId/overview',
      name: 'overview',
      component: ProjectOverviewView,
    },
    {
      path: '/projects/:projectId/input',
      name: 'input',
      component: RequirementInputView,
    },
    {
      path: '/projects/:projectId/requirement',
      name: 'requirement',
      component: RequirementAnalysisView,
    },
    {
      path: '/projects/:projectId/solution',
      name: 'solution',
      component: SolutionDesignView,
    },
    {
      path: '/projects/:projectId/intelligence',
      name: 'intelligence',
      component: IntelligenceAnalysisView,
    },
    {
      path: '/projects/:projectId/pricing',
      name: 'pricing',
      component: PricingView,
    },
    {
      path: '/projects/:projectId/development',
      name: 'development',
      component: DevelopmentView,
    },
    {
      path: '/projects/:projectId/config',
      name: 'config',
      component: SystemConfigView,
    },
    {
      path: '/projects/:projectId/config/tasks',
      name: 'tasks',
      component: TaskListView,
    },
    {
      path: '/projects/:projectId/knowledge',
      redirect: (to) => `/projects/${to.params.projectId}/config?section=knowledge`,
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  authStore.hydrate()

  if (useMock && !authStore.isLoggedIn) {
    authStore.login('demo@example.com')
  }

  if (to.meta.public) {
    if (authStore.isLoggedIn && to.name === 'login') {
      return '/projects'
    }
    return true
  }

  if (!authStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
