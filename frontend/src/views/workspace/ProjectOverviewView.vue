<template>
  <ProjectLayout>
    <div class="overview-page">
      <section class="overview-page__stats">
        <article class="overview-page__stat overview-page__stat--blue">
          <div class="overview-page__stat-head"><span>协作</span></div>
          <div class="overview-page__stat-value">7</div>
          <div class="overview-page__stat-label">团队模块</div>
        </article>
        <article class="overview-page__stat overview-page__stat--orange">
          <div class="overview-page__stat-head"><span>待办</span></div>
          <div class="overview-page__stat-value">{{ pendingCount }}</div>
          <div class="overview-page__stat-label">待办任务</div>
        </article>
        <article class="overview-page__stat overview-page__stat--green">
          <div class="overview-page__stat-head"><span>进度</span></div>
          <div class="overview-page__stat-value">{{ completionPercent }}%</div>
          <div class="overview-page__stat-label">完成度</div>
        </article>
        <article class="overview-page__stat overview-page__stat--purple">
          <div class="overview-page__stat-head"><span>产出</span></div>
          <div class="overview-page__stat-value">{{ doneCount }}</div>
          <div class="overview-page__stat-label">文档</div>
        </article>
      </section>

      <section class="overview-page__project">
        <div class="overview-page__project-glow" aria-hidden="true"></div>
        <h2>{{ project?.name }}</h2>
        <p>{{ project?.description || '暂无描述' }}</p>
        <div class="overview-page__project-grid">
          <div class="overview-page__project-item overview-page__project-item--blue">
            <span>甲方名称</span>
            <strong>{{ clientInfo || '未填写' }}</strong>
          </div>
          <div class="overview-page__project-item">
            <span>项目区域</span>
            <strong>{{ locationText || '未填写' }}</strong>
          </div>
          <div class="overview-page__project-item overview-page__project-item--green">
            <span>项目阶段</span>
            <strong>{{ stageText || '未填写' }}</strong>
          </div>
          <div class="overview-page__project-item overview-page__project-item--orange">
            <span>归属行业</span>
            <strong>{{ industryText || '未填写' }}</strong>
          </div>
        </div>
      </section>

      <section class="overview-page__teams">
        <div class="overview-page__teams-head">
          <h3>团队工作进度</h3>
          <span>点击团队卡片查看详情</span>
        </div>
        <div class="overview-page__teams-grid">
          <button
            v-for="team in teamCards"
            :key="team.name"
            type="button"
            class="overview-page__team-card"
            @click="router.push(`/projects/${route.params.projectId}/${team.route}`)"
          >
            <div class="overview-page__team-head">
              <div class="overview-page__team-icon" :class="`overview-page__team-icon--${team.color}`">{{ team.short }}</div>
              <span>{{ team.name }}</span>
            </div>
            <div class="overview-page__team-progress">
              <div class="overview-page__team-progress-row">
                <span>任务完成</span>
                <strong>{{ team.done }}/{{ team.total }}</strong>
              </div>
              <div class="overview-page__team-bar">
                <div class="overview-page__team-bar-fill" :style="{ width: `${team.percent}%` }"></div>
              </div>
              <div v-if="team.pending > 0" class="overview-page__team-pending">{{ team.pending }} 个待办</div>
            </div>
          </button>
        </div>
      </section>

      <section class="overview-page__activity">
        <h3>最近活动</h3>
        <div v-if="recentRuns.length" class="overview-page__activity-list">
          <article v-for="run in recentRuns" :key="run.run_id" class="overview-page__activity-item">
            <i></i>
            <div>
              <p>{{ run.phase_name }} — {{ statusLabel(run.status) }}</p>
              <span>{{ run.skill_name }} · {{ formatTime(run.started_at) }}</span>
            </div>
          </article>
        </div>
        <p v-else class="overview-page__activity-empty">暂无运行记录，可在需求录入后触发 AI 分析</p>
      </section>

      <section class="overview-page__actions">
        <button class="overview-page__workflow" type="button" :disabled="workflowLoading" @click="startWorkflow">
          {{ workflowLoading ? '工作流启动中...' : '启动完整三阶段工作流' }}
        </button>
      </section>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import { useProjectStore } from '@/stores/project'
import { useRunStore } from '@/stores/run'
import { useWorkflowStore } from '@/stores/workflow'
import type { ProjectConfig } from '@/types/project'
import type { ProjectRun } from '@/types/run'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const runStore = useRunStore()
const workflowStore = useWorkflowStore()
const workflowLoading = ref(false)

const project = computed(() => projectStore.current)
const projectMeta = computed(() => (project.value?.config ?? {}) as ProjectConfig)
const clientInfo = computed(() => String(projectMeta.value.clientInfo ?? ''))
const locationText = computed(() => [projectMeta.value.province, projectMeta.value.city].filter(Boolean).join(' · '))
const stageText = computed(() => String(projectMeta.value.stage ?? ''))
const industryText = computed(() => String(projectMeta.value.industry ?? ''))

const pendingCount = computed(() => runStore.items.filter((item) => item.status === 'pending' || item.status === 'running').length)
const doneCount = computed(() => runStore.items.filter((item) => item.status === 'success').length)
const completionPercent = computed(() => {
  if (!runStore.items.length) return 0
  return Math.round((doneCount.value / runStore.items.length) * 100)
})

const recentRuns = computed(() => [...runStore.items].slice(0, 4))

const teamCards = computed(() => [
  { name: '情报支撑团队', route: 'intelligence', color: 'purple', short: '情', done: countByPhase('phase1'), total: 3, pending: pendingByRoute('intelligence'), percent: 20 },
  { name: '需求分析团队', route: 'requirement', color: 'blue', short: '需', done: countByPhase('phase1'), total: 3, pending: pendingByRoute('requirement'), percent: 35 },
  { name: '方案设计团队', route: 'solution', color: 'green', short: '方', done: countByPhase('phase2') + countByPhase('phase3'), total: 4, pending: pendingByRoute('solution'), percent: 40 },
  { name: '报价决策团队', route: 'pricing', color: 'yellow', short: '报', done: 0, total: 1, pending: 0, percent: 0 },
])

function countByPhase(phaseId: string) {
  return runStore.items.filter((item) => item.phase_id === phaseId && item.status === 'success').length
}

function pendingByRoute(_route: string) {
  return runStore.items.filter((item) => item.status === 'pending' || item.status === 'running').length
}

function statusLabel(status: ProjectRun['status']) {
  return ({ pending: '待处理', running: '进行中', success: '已完成', failed: '失败' } as const)[status]
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

const startWorkflow = async () => {
  workflowLoading.value = true
  try {
    const workflow = await workflowStore.createWorkflow(String(route.params.projectId), {
      session_id: project.value?.current_session_id,
      prompt: projectMeta.value.prompt as string | undefined,
    })
    ElMessage.success(`工作流已启动：${workflow.workflow_id}`)
    await runStore.fetchRuns(String(route.params.projectId), workflow.session_id)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '工作流启动失败')
  } finally {
    workflowLoading.value = false
  }
}
</script>

<style scoped>
.overview-page {
  display: grid;
  gap: 24px;
  padding: 24px;
}

.overview-page__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.overview-page__stat {
  padding: 20px;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 4px 6px rgba(15, 23, 42, 0.08);
}

.overview-page__stat--blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.overview-page__stat--orange { background: linear-gradient(135deg, #f97316, #ea580c); }
.overview-page__stat--green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.overview-page__stat--purple { background: linear-gradient(135deg, #a855f7, #9333ea); }

.overview-page__stat-head span {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 12px;
}

.overview-page__stat-value {
  margin: 12px 0 4px;
  font-size: 30px;
  font-weight: 700;
}

.overview-page__stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.overview-page__project {
  position: relative;
  overflow: hidden;
  padding: 24px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 12px;
  background: #fff;
}

.overview-page__project-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 256px;
  height: 256px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.3), transparent);
  filter: blur(48px);
}

.overview-page__project h2 {
  position: relative;
  margin: 0 0 8px;
  font-size: 20px;
}

.overview-page__project p {
  position: relative;
  margin: 0 0 16px;
  color: #475569;
  font-size: 14px;
  line-height: 1.625;
}

.overview-page__project-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.overview-page__project-item {
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.overview-page__project-item span {
  display: block;
  margin-bottom: 4px;
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
}

.overview-page__project-item strong {
  color: #0f172a;
  font-size: 14px;
}

.overview-page__project-item--blue { background: #eff6ff; }
.overview-page__project-item--blue span { color: #1d4ed8; }
.overview-page__project-item--green { background: #f0fdf4; }
.overview-page__project-item--green span { color: #15803d; }
.overview-page__project-item--orange { background: #fff7ed; }
.overview-page__project-item--orange span { color: #c2410c; }

.overview-page__teams,
.overview-page__activity {
  padding: 24px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 12px;
  background: #fff;
}

.overview-page__teams-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.overview-page__teams-head h3,
.overview-page__activity h3 {
  margin: 0;
  font-size: 18px;
}

.overview-page__teams-head span {
  color: #64748b;
  font-size: 12px;
}

.overview-page__teams-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.overview-page__team-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: linear-gradient(135deg, #f8fafc, #fff);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.overview-page__team-card:hover {
  transform: translateY(-2px);
  border-color: #93c5fd;
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.08);
}

.overview-page__team-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.overview-page__team-icon {
  display: inline-flex;
  width: 32px;
  height: 32px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.overview-page__team-icon--purple { background: #a855f7; }
.overview-page__team-icon--blue { background: #3b82f6; }
.overview-page__team-icon--green { background: #22c55e; }
.overview-page__team-icon--yellow { background: #eab308; }

.overview-page__team-progress-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 12px;
}

.overview-page__team-bar {
  height: 8px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.overview-page__team-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: #3b82f6;
}

.overview-page__team-pending {
  margin-top: 8px;
  color: #ea580c;
  font-size: 12px;
  font-weight: 500;
}

.overview-page__activity-list {
  display: grid;
  gap: 12px;
}

.overview-page__activity-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
}

.overview-page__activity-item:hover {
  background: #f8fafc;
}

.overview-page__activity-item i {
  width: 6px;
  height: 6px;
  margin-top: 8px;
  border-radius: 999px;
  background: #3b82f6;
}

.overview-page__activity-item p {
  margin: 0 0 4px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
}

.overview-page__activity-item span {
  color: #64748b;
  font-size: 12px;
}

.overview-page__activity-empty {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.overview-page__actions {
  display: flex;
  justify-content: flex-end;
}

.overview-page__workflow {
  padding: 10px 20px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #2563eb, #9333ea);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

.overview-page__workflow:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .overview-page__stats,
  .overview-page__project-grid,
  .overview-page__teams-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
