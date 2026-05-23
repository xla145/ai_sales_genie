<template>
  <div class="project-layout">
    <header class="project-layout__topbar">
      <div class="project-layout__topbar-left">
        <button class="project-layout__back" type="button" @click="router.push('/projects')">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m12 19-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          返回
        </button>
        <div class="project-layout__divider"></div>
        <div class="project-layout__project">
          <h1>{{ project?.name ?? '未命名项目' }}</h1>
          <div class="project-layout__meta">
            <span v-if="clientInfo">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" stroke="currentColor" stroke-width="2"/></svg>
              {{ clientInfo }}
            </span>
            <span v-if="locationText">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/></svg>
              {{ locationText }}
            </span>
            <span v-if="stageText">
              <i class="project-layout__stage-dot"></i>
              {{ stageText }}
            </span>
          </div>
        </div>
      </div>
      <div v-if="pendingCount > 0" class="project-layout__todo">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        {{ pendingCount }} 个待办
      </div>
    </header>

    <nav class="project-layout__tabs" aria-label="Project sections">
      <button
        v-for="item in tabs"
        :key="item.name"
        type="button"
        class="project-layout__tab"
        :class="{ 'project-layout__tab--active': activeTab === item.name }"
        @click="handleTabChange(item.name)"
      >
        <span class="project-layout__tab-icon" :class="[
          `project-layout__tab-icon--${item.color}`,
          { 'project-layout__tab-icon--active': activeTab === item.name },
        ]">
          <TabIcon :name="item.icon" />
        </span>
        <span>{{ item.label }}</span>
        <span
          v-if="item.badge"
          class="project-layout__tab-badge"
          :class="{ 'project-layout__tab-badge--active': activeTab === item.name }"
        >
          {{ item.badge }}
        </span>
      </button>
    </nav>

    <section class="project-layout__content">
      <slot />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabIcon from '@/components/icons/TabIcon.vue'
import { PROJECT_TABS } from '@/constants/projectTabs'
import { useProjectContext } from '@/composables/useProjectContext'
import { useProjectStore } from '@/stores/project'
import { useRunStore } from '@/stores/run'
import type { ProjectConfig } from '@/types/project'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const runStore = useRunStore()

useProjectContext()

const tabs = PROJECT_TABS

const project = computed(() => projectStore.current)
const projectMeta = computed(() => (project.value?.config ?? {}) as ProjectConfig)
const clientInfo = computed(() => String(projectMeta.value.clientInfo ?? ''))
const locationText = computed(() => [projectMeta.value.province, projectMeta.value.city].filter(Boolean).join(' · '))
const stageText = computed(() => String(projectMeta.value.stage ?? ''))
const pendingCount = computed(() => runStore.items.filter((item) => item.status === 'pending' || item.status === 'running').length)

const activeTab = computed(() => {
  if (route.name === 'tasks') return 'config'
  return String(route.name ?? 'overview')
})

const handleTabChange = (name: string) => {
  router.push(`/projects/${route.params.projectId}/${name}`)
}
</script>

<style scoped>
.project-layout {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, rgba(239, 246, 255, 0.2) 50%, #f8fafc 100%);
}

.project-layout__topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
}

.project-layout__topbar-left {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 16px;
}

.project-layout__back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #475569;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.project-layout__back svg {
  width: 16px;
  height: 16px;
}

.project-layout__back:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.project-layout__divider {
  width: 1px;
  height: 20px;
  background: #cbd5e1;
}

.project-layout__project h1 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.project-layout__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-top: 2px;
  color: #475569;
  font-size: 12px;
}

.project-layout__meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.project-layout__meta svg {
  width: 12px;
  height: 12px;
}

.project-layout__stage-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
}

.project-layout__todo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  background: #fff7ed;
  color: #c2410c;
  font-size: 14px;
  font-weight: 600;
}

.project-layout__todo svg {
  width: 16px;
  height: 16px;
}

.project-layout__tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding: 0 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  background: rgba(255, 255, 255, 0.95);
  scrollbar-width: none;
}

.project-layout__tabs::-webkit-scrollbar {
  display: none;
}

.project-layout__tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: none;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.project-layout__tab-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #64748b;
}

.project-layout__tab-icon--active {
  color: #2563eb;
}

.project-layout__tab-icon--active.project-layout__tab-icon--slate { background: rgba(100, 116, 139, 0.15); color: #475569; }
.project-layout__tab-icon--active.project-layout__tab-icon--indigo { background: rgba(99, 102, 241, 0.15); color: #4f46e5; }
.project-layout__tab-icon--active.project-layout__tab-icon--purple { background: rgba(168, 85, 247, 0.15); color: #9333ea; }
.project-layout__tab-icon--active.project-layout__tab-icon--blue { background: rgba(59, 130, 246, 0.15); color: #2563eb; }
.project-layout__tab-icon--active.project-layout__tab-icon--green { background: rgba(34, 197, 94, 0.15); color: #16a34a; }
.project-layout__tab-icon--active.project-layout__tab-icon--yellow { background: rgba(234, 179, 8, 0.15); color: #ca8a04; }
.project-layout__tab-icon--active.project-layout__tab-icon--red { background: rgba(239, 68, 68, 0.15); color: #dc2626; }
.project-layout__tab-icon--active.project-layout__tab-icon--gray { background: rgba(107, 114, 128, 0.15); color: #4b5563; }

.project-layout__tab:hover {
  color: #0f172a;
}

.project-layout__tab--active {
  color: #1d4ed8;
}

.project-layout__tab--active::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.project-layout__tab-badge {
  padding: 2px 6px;
  border-radius: 999px;
  background: #ffedd5;
  color: #c2410c;
  font-size: 11px;
  font-weight: 600;
}

.project-layout__tab-badge--active {
  background: #dbeafe;
  color: #1d4ed8;
}

.project-layout__content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
