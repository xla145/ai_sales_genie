<template>
  <ProjectLayout>
    <div class="system-config-page">
      <aside class="system-config-page__nav">
        <button
          v-for="item in sections"
          :key="item.key"
          type="button"
          class="system-config-page__nav-item"
          :class="{ 'system-config-page__nav-item--active': activeSection === item.key }"
          @click="switchSection(item.key)"
        >
          {{ item.label }}
        </button>
      </aside>

      <section class="system-config-page__content">
        <template v-if="activeSection === 'tasks'">
          <header class="system-config-page__head">
            <h2>任务列表</h2>
            <p>查看所有 AI 生成任务与人工待办</p>
          </header>
          <button type="button" class="system-config-page__link" @click="router.push(`/projects/${route.params.projectId}/config/tasks`)">
            进入任务列表
          </button>
        </template>

        <template v-else-if="activeSection === 'knowledge'">
          <header class="system-config-page__head">
            <h2>知识库</h2>
            <p>行业知识与经验沉淀</p>
          </header>
          <WorkflowStageGrid :stages="knowledgeStages" />
        </template>

        <template v-else-if="activeSection === 'templates'">
          <header class="system-config-page__head">
            <h2>模板库</h2>
            <p>PPT、方案模板管理</p>
          </header>
          <WorkflowStageGrid :stages="templateStages" />
        </template>

        <template v-else-if="activeSection === 'cases'">
          <header class="system-config-page__head">
            <h2>案例库</h2>
            <p>历史项目案例沉淀</p>
          </header>
          <WorkflowStageGrid :stages="caseStages" />
        </template>

        <template v-else>
          <header class="system-config-page__head">
            <h2>{{ currentSection?.label }}</h2>
            <p>{{ currentSection?.description }}</p>
          </header>
          <WorkflowStageGrid :stages="currentStages" />
        </template>
      </section>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import WorkflowStageGrid from '@/components/workspace/WorkflowStageGrid.vue'
import { KNOWLEDGE_WORKFLOW_STAGES, SYSTEM_CONFIG_WORKFLOW_STAGES } from '@/constants/workspace'

const route = useRoute()
const router = useRouter()

const sections = [
  { key: 'tasks', label: '任务列表', description: '查看所有 AI 生成任务与人工待办' },
  { key: 'model', label: '模型管理', description: 'AI模型配置与管理' },
  { key: 'agent', label: '智能体管理', description: '智能体团队配置' },
  { key: 'knowledge', label: '知识库', description: '行业知识与经验沉淀' },
  { key: 'templates', label: '模板库', description: 'PPT、方案模板管理' },
  { key: 'cases', label: '案例库', description: '历史项目案例沉淀' },
]

const knowledgeStages = KNOWLEDGE_WORKFLOW_STAGES
const templateStages = [{ name: 'PPT 模板', description: '售前演示模板管理' }, { name: '方案模板', description: '标准方案文档模板' }]
const caseStages = [{ name: '历史案例', description: '历史项目案例沉淀' }]

const activeSection = computed(() => String(route.query.section ?? 'tasks'))
const currentSection = computed(() => sections.find((item) => item.key === activeSection.value) ?? sections[0])
const currentStages = computed(() => {
  if (activeSection.value === 'model' || activeSection.value === 'agent') {
    return SYSTEM_CONFIG_WORKFLOW_STAGES.filter((item) =>
      activeSection.value === 'model' ? item.name === '模型管理' : item.name === '智能体管理',
    )
  }
  return SYSTEM_CONFIG_WORKFLOW_STAGES
})

const switchSection = (key: string) => {
  router.replace({ query: { ...route.query, section: key } })
}

watch(
  () => route.query.section,
  (section) => {
    if (!section) {
      router.replace({ query: { ...route.query, section: 'tasks' } })
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.system-config-page {
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: calc(100vh - 120px);
}

.system-config-page__nav {
  display: grid;
  gap: 4px;
  align-content: start;
  padding: 16px;
  border-right: 1px solid #e2e8f0;
  background: #fff;
}

.system-config-page__nav-item {
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #475569;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  text-align: left;
}

.system-config-page__nav-item--active,
.system-config-page__nav-item:hover {
  background: #eff6ff;
  color: #1d4ed8;
}

.system-config-page__content {
  padding: 24px;
}

.system-config-page__head h2 {
  margin: 0 0 8px;
  font-size: 20px;
}

.system-config-page__head p {
  margin: 0 0 20px;
  color: #64748b;
  font-size: 14px;
}

.system-config-page__link {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}
</style>
