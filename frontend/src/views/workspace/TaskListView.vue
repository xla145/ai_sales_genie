<template>
  <ProjectLayout>
    <div class="task-list-page">
      <aside class="task-list-page__main">
        <header class="task-list-page__header">
          <div>
            <h2>任务列表</h2>
            <p>追踪所有 AI 生成任务与人工待办</p>
          </div>
          <button type="button" class="task-list-page__create" @click="refreshTasks">刷新任务</button>
        </header>

        <div class="task-list-page__filters">
          <button
            v-for="item in statusFilters"
            :key="item.key"
            type="button"
            class="task-list-page__filter"
            :class="{ 'task-list-page__filter--active': filterStatus === item.key }"
            @click="filterStatus = item.key"
          >
            {{ item.label }} <strong>{{ item.count }}</strong>
          </button>
        </div>

        <div class="task-list-page__toolbar">
          <input v-model="search" type="search" placeholder="搜索任务..." />
          <select v-model="filterModule">
            <option v-for="module in modules" :key="module" :value="module">{{ module }}</option>
          </select>
        </div>

        <div v-loading="runStore.loading" class="task-list-page__list">
          <article
            v-for="task in filteredTasks"
            :key="task.id"
            class="task-list-page__item"
            :class="{ 'task-list-page__item--active': selectedTask?.id === task.id }"
            @click="selectedTask = selectedTask?.id === task.id ? null : task"
          >
            <div class="task-list-page__item-status" :class="`task-list-page__item-status--${task.status}`"></div>
            <div class="task-list-page__item-body">
              <div class="task-list-page__item-head">
                <strong :class="{ 'task-list-page__item-title--done': task.status === 'done' }">{{ task.title }}</strong>
                <button v-if="task.status === 'error'" type="button" @click.stop="retryRun(task.runId)">重试</button>
              </div>
              <p>{{ task.description }}</p>
              <div class="task-list-page__item-meta">
                <span>{{ task.module }}</span>
                <span>{{ task.assignee }}</span>
                <span>{{ formatTime(task.createdAt) }}</span>
              </div>
            </div>
          </article>
          <p v-if="!filteredTasks.length && !runStore.loading" class="task-list-page__empty">没有匹配的任务</p>
        </div>
      </aside>

      <aside class="task-list-page__sidebar">
        <section>
          <h3>总体进度</h3>
          <div class="task-list-page__progress">{{ completionPercent }}% 完成</div>
        </section>
        <section>
          <h3>最近完成</h3>
          <div v-for="task in doneTasks.slice(0, 3)" :key="task.id" class="task-list-page__done-item">
            <strong>{{ task.title }}</strong>
            <span>{{ formatTime(task.finishedAt) }}</span>
          </div>
          <p v-if="!doneTasks.length" class="task-list-page__empty">暂无已完成任务</p>
        </section>
      </aside>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import { useProjectStore } from '@/stores/project'
import { useRunStore } from '@/stores/run'
import { mapRunsToTasks, type TaskDisplayItem, type TaskDisplayStatus } from '@/utils/task'

const route = useRoute()
const projectStore = useProjectStore()
const runStore = useRunStore()

const filterStatus = ref<TaskDisplayStatus | 'all'>('all')
const filterModule = ref('全部')
const search = ref('')
const selectedTask = ref<TaskDisplayItem | null>(null)

const tasks = computed(() => mapRunsToTasks(runStore.items))
const modules = computed(() => ['全部', ...new Set(tasks.value.map((item) => item.module))])

const statusFilters = computed(() => [
  { key: 'all' as const, label: '全部', count: tasks.value.length },
  { key: 'running' as const, label: '进行中', count: tasks.value.filter((item) => item.status === 'running').length },
  { key: 'pending' as const, label: '待处理', count: tasks.value.filter((item) => item.status === 'pending').length },
  { key: 'done' as const, label: '已完成', count: tasks.value.filter((item) => item.status === 'done').length },
  { key: 'error' as const, label: '失败', count: tasks.value.filter((item) => item.status === 'error').length },
])

const filteredTasks = computed(() => {
  let result = tasks.value
  if (filterStatus.value !== 'all') result = result.filter((item) => item.status === filterStatus.value)
  if (filterModule.value !== '全部') result = result.filter((item) => item.module === filterModule.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    result = result.filter((item) => item.title.toLowerCase().includes(q) || item.description.toLowerCase().includes(q))
  }
  return result
})

const doneTasks = computed(() => tasks.value.filter((item) => item.status === 'done'))
const completionPercent = computed(() => (tasks.value.length ? Math.round((doneTasks.value.length / tasks.value.length) * 100) : 0))

const formatTime = (value?: string) => (value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '—')

const refreshTasks = async () => {
  await runStore.fetchRuns(String(route.params.projectId), projectStore.current?.current_session_id ?? undefined)
}

const retryRun = async (runId: string) => {
  const run = runStore.items.find((item) => item.run_id === runId)
  if (!run) return
  try {
    await runStore.createRun(String(route.params.projectId), {
      session_id: run.session_id,
      phase_id: run.phase_id,
      phase_name: run.phase_name,
      skill_name: run.skill_name,
      input_files: run.input_files,
      expected_outputs: run.expected_outputs,
    })
    ElMessage.success('已重新发起任务')
    await refreshTasks()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '重试失败')
  }
}
</script>

<style scoped>
.task-list-page {
  display: flex;
  min-height: calc(100vh - 120px);
}

.task-list-page__main {
  flex: 1;
  min-width: 0;
  border-right: 1px solid #e2e8f0;
  background: #f8fafc;
}

.task-list-page__header,
.task-list-page__filters,
.task-list-page__toolbar,
.task-list-page__list {
  padding-left: 24px;
  padding-right: 24px;
}

.task-list-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24px;
  padding-bottom: 16px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.task-list-page__header h2 {
  margin: 0;
  font-size: 20px;
}

.task-list-page__header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.task-list-page__create {
  padding: 8px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.task-list-page__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 16px;
  padding-bottom: 16px;
  background: #fff;
}

.task-list-page__filter {
  display: inline-flex;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  background: #f1f5f9;
  color: #334155;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}

.task-list-page__filter--active {
  background: #1e293b;
  color: #fff;
}

.task-list-page__toolbar {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  padding-bottom: 16px;
}

.task-list-page__toolbar input,
.task-list-page__toolbar select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  font: inherit;
  font-size: 14px;
}

.task-list-page__toolbar input {
  flex: 1;
  max-width: 320px;
}

.task-list-page__list {
  display: grid;
  gap: 8px;
  padding-top: 8px;
  padding-bottom: 24px;
}

.task-list-page__item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
}

.task-list-page__item--active {
  border-color: #a5b4fc;
  box-shadow: 0 8px 16px rgba(79, 70, 229, 0.08);
}

.task-list-page__item-status {
  width: 12px;
  height: 12px;
  margin-top: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}

.task-list-page__item-status--pending { background: #94a3b8; }
.task-list-page__item-status--running { background: #3b82f6; }
.task-list-page__item-status--done { background: #22c55e; }
.task-list-page__item-status--error { background: #ef4444; }

.task-list-page__item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-list-page__item-head strong {
  font-size: 14px;
}

.task-list-page__item-title--done {
  color: #94a3b8;
  text-decoration: line-through;
}

.task-list-page__item-head button {
  border: none;
  border-radius: 8px;
  background: #fee2e2;
  color: #dc2626;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
}

.task-list-page__item-body p {
  margin: 4px 0 8px;
  color: #64748b;
  font-size: 12px;
}

.task-list-page__item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #94a3b8;
  font-size: 12px;
}

.task-list-page__sidebar {
  width: 256px;
  flex-shrink: 0;
  padding: 24px;
  background: #fff;
}

.task-list-page__sidebar section + section {
  margin-top: 24px;
}

.task-list-page__sidebar h3 {
  margin: 0 0 12px;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.task-list-page__progress {
  font-size: 28px;
  font-weight: 700;
}

.task-list-page__done-item {
  display: grid;
  gap: 4px;
  margin-bottom: 12px;
}

.task-list-page__done-item strong {
  font-size: 12px;
}

.task-list-page__done-item span,
.task-list-page__empty {
  color: #94a3b8;
  font-size: 12px;
}
</style>
