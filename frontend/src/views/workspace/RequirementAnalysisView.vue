<template>
  <ProjectLayout>
    <div class="requirement-page">
      <RequirementSectionNav :active-key="currentSection" :items="navItems" @select="handleSectionSelect" />

      <div class="requirement-page__main">
        <div class="requirement-page__container">
          <template v-if="currentSection === 'overview'">
            <article class="overview-panel">
              <div class="overview-panel__head">
                <div class="overview-panel__head-left">
                  <span class="overview-panel__head-icon">📊</span>
                  <div>
                    <h2>需求全景</h2>
                    <p>项目需求整体概览</p>
                  </div>
                </div>
                <button type="button" class="overview-panel__supplement" @click="supplementVisible = true">+ 需求补充</button>
              </div>

              <div class="overview-grid">
                <article
                  v-for="card in overviewCards"
                  :key="card.title"
                  class="overview-card"
                  :class="`overview-card--${card.tone}`"
                  role="button"
                  tabindex="0"
                  @click="handleSectionSelect(card.sectionKey)"
                  @keydown.enter="handleSectionSelect(card.sectionKey)"
                >
                  <div class="overview-card__head">
                    <span class="overview-card__icon" :class="`overview-card__icon--${card.tone}`">{{ card.icon }}</span>
                    <h4>{{ card.title }}</h4>
                  </div>
                  <div v-if="card.rows" class="overview-card__rows">
                    <div v-for="row in card.rows" :key="row.label" class="overview-card__row">
                      <span>{{ row.label }}</span>
                      <strong :class="row.emphasisClass">{{ row.value }}</strong>
                    </div>
                  </div>
                  <div v-else class="overview-card__bullets">
                    <p v-for="item in card.bullets" :key="item"><span>•</span> {{ item }}</p>
                  </div>
                </article>
              </div>
            </article>

            <article class="completeness-panel">
              <div class="completeness-panel__head">
                <span class="completeness-panel__icon">☰</span>
                <h4>需求完整度总览</h4>
              </div>
              <div class="completeness-panel__grid">
                <button
                  v-for="item in completenessItems"
                  :key="item.title"
                  type="button"
                  class="completeness-panel__item"
                  @click="handleSectionSelect(item.sectionKey)"
                >
                  <div class="completeness-panel__item-title">{{ item.title }}</div>
                  <div class="completeness-panel__item-icon" :class="`completeness-panel__item-icon--${item.type}`">
                    {{ item.icon }}
                  </div>
                </button>
              </div>
            </article>
          </template>

          <template v-else>
            <RequirementOverviewPanel
              :title="activeSection.title"
              :subtitle="activeSection.subtitle"
              :icon-color="activeSection.iconColor"
            >
              <template #icon>
                <SectionIcon :name="activeSection.iconName" />
              </template>

              <component
                :is="activeSection.component"
                v-bind="activeSection.props"
                @add="activeSection.onAdd?.()"
                @remove="activeSection.onRemove?.($event)"
                @update:unknownInfo="pendingUnknownInfo = $event"
                @update:assumptions="pendingAssumptions = $event"
              />

              <div v-if="hasChanges" class="requirement-page__warning">
                <span>?</span>
                <div>
                  <p>您有未确认的修改</p>
                  <small>请点击"确认分析"保存您的修改</small>
                </div>
              </div>

              <div class="requirement-page__footer-action">
                <button type="button" class="requirement-page__save" :disabled="saving" @click="saveRequirementAnalysis">
                  {{ saving ? '保存中...' : '✓ 确认分析' }}
                </button>
              </div>
            </RequirementOverviewPanel>
          </template>
        </div>
      </div>

      <aside class="requirement-page__aside">
        <ReadinessPanel
          :score="readinessScore"
          :level="readinessLevel.level"
          :level-label="readinessLevel.label"
          :metrics="readinessMetricItems"
        />
        <AttachmentPanel :items="displayAttachments" @upload="handleAttachmentUpload" @remove="handleAttachmentRemove" />
      </aside>

      <button v-if="!assistantVisible" class="requirement-page__fab" type="button" title="AI需求专家" @click="assistantVisible = true">
        AI
        <span class="requirement-page__fab-dot"></span>
      </button>
      <AIAssistantPanel
        v-else
        floating
        :messages="assistantMessages"
        @close="assistantVisible = false"
        @send="handleAssistantSend"
      />

      <SupplementDialog v-model="supplementVisible" :notes="supplementNotes" @update:notes="supplementNotes = $event" @confirm="handleSupplementConfirm" />
      <AIAnalysisDialog v-model="analysisVisible" :items="analysisItems" />
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import SectionIcon from '@/components/icons/SectionIcon.vue'
import RequirementSectionNav from '@/components/requirement/RequirementSectionNav.vue'
import RequirementOverviewPanel from '@/components/requirement/RequirementOverviewPanel.vue'
import BasicInfoForm from '@/components/requirement/BasicInfoForm.vue'
import CoreElementsForm from '@/components/requirement/CoreElementsForm.vue'
import ScenarioForm from '@/components/requirement/ScenarioForm.vue'
import FunctionRequirementForm from '@/components/requirement/FunctionRequirementForm.vue'
import RiskForm from '@/components/requirement/RiskForm.vue'
import PendingChecklistForm from '@/components/requirement/PendingChecklistForm.vue'
import ReadinessPanel from '@/components/requirement/ReadinessPanel.vue'
import AttachmentPanel from '@/components/requirement/AttachmentPanel.vue'
import AIAssistantPanel from '@/components/requirement/AIAssistantPanel.vue'
import SupplementDialog from '@/components/requirement/SupplementDialog.vue'
import AIAnalysisDialog from '@/components/requirement/AIAnalysisDialog.vue'
import { useRequirementAnalysis } from '@/composables/useRequirementAnalysis'
import { useProjectStore } from '@/stores/project'
import { isFilled } from '@/utils/requirement'
import type { RequirementAttachmentItem } from '@/types/project'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const assistantVisible = ref(false)
const supplementVisible = ref(false)
const analysisVisible = ref(false)
const saving = ref(false)
const loading = ref(false)
const hasChanges = ref(false)

const projectId = computed(() => String(route.params.projectId ?? ''))
const currentSection = computed(() => String(route.query.section ?? 'overview'))

const {
  attachments,
  basicItems,
  buildRequirementAnalysis,
  completionRate,
  coreItems,
  functionItems,
  pendingAssumptions,
  pendingItems,
  pendingUnknownInfo,
  readinessLevel,
  readinessMetrics,
  readinessScore,
  riskItems,
  scenarioItems,
  sectionProgress,
  supplementNotes,
  addRiskItem,
  addScenarioItem,
  applyRequirementAnalysis,
  removeRiskItem,
  removeScenarioItem,
} = useRequirementAnalysis()

const navItems = computed(() => {
  const progress = sectionProgress.value
  const pendingBasic = progress.basic.total - progress.basic.filled
  const pendingCore = progress.core.total - progress.core.filled

  return [
    { key: 'overview', title: '需求全景', iconName: 'eye' },
    {
      key: 'basic',
      title: '项目基础信息',
      iconName: 'file-text',
      badge: pendingBasic > 0 ? { text: `${pendingBasic}项待确认`, type: 'warning' as const } : undefined,
    },
    {
      key: 'core',
      title: '项目核心要素',
      iconName: 'circle',
      badge: pendingCore > 0 ? { text: `${pendingCore}项未填写`, type: 'error' as const } : undefined,
    },
    {
      key: 'scenario',
      title: '场景与诉求分析',
      iconName: 'circle',
      badge: { text: `${Math.max(scenarioItems.length, 1)}个场景`, type: 'info' as const },
    },
    {
      key: 'function',
      title: '功能需求',
      iconName: 'circle',
      badge: progress.function.filled === 0 ? { text: '待填写', type: 'error' as const } : undefined,
    },
    {
      key: 'risk',
      title: '风险点与关注点',
      iconName: 'alert-circle',
      badge: riskItems.length > 0 ? { text: `${riskItems.length}个风险`, type: 'warning' as const } : undefined,
    },
    {
      key: 'pending',
      title: '待确认需求清单',
      iconName: 'clock',
      badge: { text: `${pendingItems.filter((item) => !item.checked).length + 2}项待确认`, type: 'warning' as const },
    },
  ]
})

const sectionConfigs = computed(() => [
  {
    key: 'basic',
    title: '项目基础信息',
    subtitle: '填写项目基本情况',
    iconName: 'file-text',
    iconColor: 'blue' as const,
    component: BasicInfoForm,
    props: { items: basicItems },
  },
  {
    key: 'core',
    title: '项目核心要素',
    subtitle: '定义核心目标和用户',
    iconName: 'circle',
    iconColor: 'purple' as const,
    component: CoreElementsForm,
    props: { items: coreItems },
  },
  {
    key: 'scenario',
    title: '场景与诉求分析',
    subtitle: '梳理业务场景流程',
    iconName: 'circle',
    iconColor: 'green' as const,
    component: ScenarioForm,
    props: { items: scenarioItems },
    onAdd: () => addScenarioItem(),
    onRemove: (key: string) => removeScenarioItem(key),
  },
  {
    key: 'function',
    title: '功能需求',
    subtitle: '详细功能点描述',
    iconName: 'circle',
    iconColor: 'indigo' as const,
    component: FunctionRequirementForm,
    props: { items: functionItems },
  },
  {
    key: 'risk',
    title: '风险点与关注点',
    subtitle: '识别潜在风险',
    iconName: 'alert-circle',
    iconColor: 'orange' as const,
    component: RiskForm,
    props: { items: riskItems },
    onAdd: () => addRiskItem(),
    onRemove: (key: string) => removeRiskItem(key),
  },
  {
    key: 'pending',
    title: '待确认需求清单',
    subtitle: '记录待明确事项',
    iconName: 'clock',
    iconColor: 'yellow' as const,
    component: PendingChecklistForm,
    props: { items: pendingItems, unknownInfo: pendingUnknownInfo.value, assumptions: pendingAssumptions.value },
  },
])

const activeSection = computed(() => sectionConfigs.value.find((item) => item.key === currentSection.value) ?? sectionConfigs.value[0])

const overviewCards = computed(() => {
  const basic = buildRequirementAnalysis().basic
  const keyFocus = [
    ...riskItems.map((item) => item.description || item.impact || item.strategy).filter((item) => isFilled(item)),
    ...pendingItems.filter((item) => !item.checked).map((item) => item.title),
  ].slice(0, 3)

  return [
    {
      icon: '📄',
      tone: 'blue',
      title: '项目基本情况',
      sectionKey: 'basic',
      rows: [
        { label: '项目名称：', value: basic.projectName || '智能仓储管理系统' },
        { label: '所属行业：', value: basic.industry || '物流/仓储' },
        { label: '项目类型：', value: basic.projectType || '新产品' },
      ],
    },
    {
      icon: '✓',
      tone: 'green',
      title: '完成情况统计',
      sectionKey: 'pending',
      rows: [
        { label: '已填写章节：', value: `${Object.values(sectionProgress.value).filter((item) => item.filled > 0).length} / 6`, emphasisClass: 'is-green' },
        { label: '待确认项：', value: `${pendingItems.filter((item) => !item.checked).length + 2} 项`, emphasisClass: 'is-orange' },
        { label: '识别风险：', value: `${Math.max(riskItems.length, 2)} 项`, emphasisClass: 'is-red' },
      ],
    },
    {
      icon: '📊',
      tone: 'purple',
      title: '核心指标',
      sectionKey: 'core',
      rows: [
        { label: '预计工期：', value: '6 个月' },
        { label: '技术难度：', value: '中等', emphasisClass: 'is-orange' },
        { label: '优先级：', value: 'P0 - 最高', emphasisClass: 'is-red' },
      ],
    },
    {
      icon: '!',
      tone: 'orange',
      title: '关键关注点',
      sectionKey: 'risk',
      bullets: keyFocus.length ? keyFocus : ['ERP系统对接时间不确定', '移动端设备版本兼容性', '实时库存更新性能要求'],
    },
  ]
})

const completenessItems = computed(() => {
  const buildItem = (title: string, sectionKey: string, filled: number, total: number) => ({
    title,
    sectionKey,
    icon: filled === total ? '✓' : '⚠',
    type: filled === total ? 'success' : 'warning',
  })

  return [
    buildItem('项目基础信息', 'basic', sectionProgress.value.basic.filled, sectionProgress.value.basic.total),
    buildItem('项目核心要素', 'core', sectionProgress.value.core.filled, sectionProgress.value.core.total),
    buildItem('场景与诉求分析', 'scenario', sectionProgress.value.scenario.filled, sectionProgress.value.scenario.total),
    buildItem('功能需求', 'function', sectionProgress.value.function.filled, sectionProgress.value.function.total),
    buildItem('风险点与关注点', 'risk', sectionProgress.value.risk.filled, sectionProgress.value.risk.total),
    buildItem('待确认需求清单', 'pending', sectionProgress.value.pending.filled, sectionProgress.value.pending.total),
  ]
})

const readinessMetricItems = computed(() => {
  const clarity = Math.min(sectionProgress.value.basic.filled + sectionProgress.value.core.filled, 9) * 8
  const risk = Math.min(riskItems.length * 15 + pendingItems.filter((item) => !item.checked).length * 5, 100)
  const complexity = Math.min(sectionProgress.value.function.filled * 8 + scenarioItems.length * 6, 100)

  return [
    {
      label: '需求就绪度',
      value: `${readinessScore.value}分`,
      barWidth: `${readinessScore.value}%`,
      barClass: readinessScore.value >= 80 ? 'readiness-panel__bar-fill--green' : readinessScore.value >= 60 ? 'readiness-panel__bar-fill--yellow' : 'readiness-panel__bar-fill--red',
      hint: '根据各项需求的确认程度进行评估',
    },
    {
      label: '需求清晰度',
      value: `${clarity}分`,
      barWidth: `${clarity}%`,
      barClass: clarity >= 80 ? 'readiness-panel__bar-fill--green' : clarity >= 60 ? 'readiness-panel__bar-fill--yellow' : 'readiness-panel__bar-fill--red',
      scoreClass: clarity >= 80 ? 'is-green' : clarity >= 60 ? 'is-yellow' : 'is-red',
      hint: '基础信息、附件、核心要素填写情况',
    },
    {
      label: '项目风险度',
      value: `${risk}分`,
      barWidth: `${risk}%`,
      barClass: risk < 50 ? 'readiness-panel__bar-fill--green' : 'readiness-panel__bar-fill--red',
      scoreClass: risk < 50 ? 'is-green' : 'is-red',
      hint: '分数越低风险越小，待确认清单和风险点数量',
    },
    {
      label: '技术复杂度',
      value: `${complexity}分`,
      barWidth: `${complexity}%`,
      barClass: complexity >= 80 ? 'readiness-panel__bar-fill--red' : complexity >= 60 ? 'readiness-panel__bar-fill--yellow' : 'readiness-panel__bar-fill--green',
      scoreClass: complexity >= 80 ? 'is-red' : complexity >= 60 ? 'is-yellow' : 'is-green',
      hint: '根据功能规划数量进行评估',
    },
  ]
})

const displayAttachments = computed(() => {
  if (attachments.length) {
    return attachments.map((item) => ({ name: item.name, meta: item.meta, size: '2.3 MB' }))
  }
  return [
    { name: '招标文件_v1.pdf', meta: '2026-04-20 14:30', size: '2.3 MB' },
    { name: '客户访谈录音.mp3', meta: '2026-04-19 10:15', size: '15.6 MB' },
  ]
})

const assistantMessages = ref<Array<{ text: string; role: 'assistant' | 'user' }>>([
  { text: '您好！我是AI需求专家助手，很高兴为您服务。请问有什么需要帮助的吗？', role: 'assistant' },
])

const analysisItems = computed(() => [
  { title: '需求亮点', text: completionRate.value >= 60 ? '项目目标明确，业务场景清晰，技术选型合理。' : '当前已形成部分需求输入，建议继续补充核心信息。' },
  { title: '待改进项', text: '建议补充用户画像的量化数据，非功能性需求的具体指标需要细化。' },
  { title: 'AI 建议', text: '考虑到项目规模，建议采用微服务架构，便于后期扩展和维护。' },
  { title: '待确认清单', text: pendingItems.filter((item) => !item.checked).map((item) => item.title).join('、') || '与客户确认实时库存更新的精确时间要求' },
])

const loadProjectRequirementAnalysis = async () => {
  if (!projectId.value) return
  loading.value = true
  try {
    const project = await projectStore.fetchProject(projectId.value)
    applyRequirementAnalysis(project.config?.requirementAnalysis)
  }
  finally {
    loading.value = false
  }
}

const saveRequirementAnalysis = async () => {
  if (!projectId.value) return
  saving.value = true
  try {
    const requirementAnalysis = buildRequirementAnalysis()
    applyRequirementAnalysis(requirementAnalysis)
    await projectStore.updateRequirementAnalysis(projectId.value, requirementAnalysis)
    hasChanges.value = false
    ElMessage.success('需求分析已保存')
  }
  catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '需求分析保存失败')
  }
  finally {
    saving.value = false
  }
}

const handleSectionSelect = (value: string) => {
  router.replace({ query: { ...route.query, section: value } })
}

const handleAttachmentUpload = async () => {
  if (!projectId.value) return
  const nextAttachments = [
    { name: `附件_${attachments.length + 1}.txt`, meta: new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-') },
    ...attachments.map((item) => ({ ...item })),
  ]

  try {
    await projectStore.updateRequirementAnalysis(projectId.value, { attachments: nextAttachments })
    applyRequirementAnalysis({ ...buildRequirementAnalysis(), attachments: nextAttachments })
    ElMessage.success('附件记录已保存')
  }
  catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '附件保存失败')
  }
}

const handleAttachmentRemove = async (target: RequirementAttachmentItem) => {
  if (!projectId.value) return
  const nextAttachments = attachments
    .filter((item) => !(item.name === target.name && item.meta === target.meta))
    .map((item) => ({ ...item }))

  try {
    await projectStore.updateRequirementAnalysis(projectId.value, { attachments: nextAttachments })
    applyRequirementAnalysis({ ...buildRequirementAnalysis(), attachments: nextAttachments })
    ElMessage.success('附件记录已删除')
  }
  catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '附件删除失败')
  }
}

const handleSupplementConfirm = async () => {
  await saveRequirementAnalysis()
  supplementVisible.value = false
  analysisVisible.value = true
}

const handleAssistantSend = (text: string) => {
  assistantMessages.value.push({ text, role: 'user' })
  setTimeout(() => {
    assistantMessages.value.push({
      text: '我已经收到您的问题。作为需求专家，我建议您先完善项目基础信息，确保需求描述清晰明确。',
      role: 'assistant',
    })
  }, 800)
}

onMounted(() => {
  loadProjectRequirementAnalysis()
})
</script>

<style scoped>
.requirement-page {
  display: flex;
  flex: 1;
  min-height: 0;
  background: #f8fafc;
  overflow: hidden;
}

.requirement-page__main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}

.requirement-page__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

.requirement-page__aside {
  display: flex;
  width: 320px;
  flex-shrink: 0;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding: 16px;
  border-left: 1px solid #e2e8f0;
  background: #fff;
}

.overview-panel,
.completeness-panel {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.overview-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.overview-panel__head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.overview-panel__head-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-size: 14px;
}

.overview-panel__head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 500;
}

.overview-panel__head p {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 12px;
}

.overview-panel__supplement {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.overview-card {
  padding: 16px;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
}

.overview-card:hover {
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.overview-card--blue { border: 1px solid #bfdbfe; }
.overview-card--green { border: 1px solid #bbf7d0; }
.overview-card--purple { border: 1px solid #e9d5ff; }
.overview-card--orange { border: 1px solid #fed7aa; }

.overview-card__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.overview-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.overview-card__icon--blue { background: #2563eb; }
.overview-card__icon--green { background: #16a34a; }
.overview-card__icon--purple { background: #9333ea; }
.overview-card__icon--orange { background: #ea580c; }

.overview-card__head h4 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 500;
}

.overview-card__rows,
.overview-card__bullets {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overview-card__row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #64748b;
  font-size: 14px;
}

.overview-card__row strong {
  color: #0f172a;
  font-weight: 500;
}

.overview-card__bullets p {
  display: flex;
  gap: 8px;
  margin: 0;
  color: #334155;
  font-size: 14px;
  line-height: 1.6;
}

.overview-card__bullets span {
  color: #f97316;
}

.is-green { color: #16a34a !important; }
.is-orange { color: #ea580c !important; }
.is-red { color: #dc2626 !important; }

.completeness-panel__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.completeness-panel__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-size: 14px;
}

.completeness-panel__head h4 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 500;
}

.completeness-panel__grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 8px;
}

.completeness-panel__item {
  padding: 12px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  text-align: center;
}

.completeness-panel__item-title {
  min-height: 32px;
  margin-bottom: 8px;
  color: #334155;
  font-size: 12px;
  line-height: 1.4;
}

.completeness-panel__item-icon {
  font-size: 24px;
  font-weight: 700;
}

.completeness-panel__item-icon--success { color: #22c55e; }
.completeness-panel__item-icon--warning { color: #f97316; }

.requirement-page__warning {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  border: 2px solid #fde68a;
  border-radius: 12px;
  background: #fffbeb;
}

.requirement-page__warning span {
  color: #d97706;
  font-size: 18px;
  font-weight: 700;
}

.requirement-page__warning p {
  margin: 0;
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
}

.requirement-page__warning small {
  color: #b45309;
  font-size: 12px;
}

.requirement-page__footer-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.requirement-page__save {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.requirement-page__save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.requirement-page__fab {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 40;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 999px;
  background: #9333ea;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(147, 51, 234, 0.35);
}

.requirement-page__fab-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 12px;
  height: 12px;
  border: 2px solid #fff;
  border-radius: 999px;
  background: #22c55e;
}

@media (max-width: 1200px) {
  .requirement-page {
    flex-direction: column;
    overflow: auto;
  }

  .requirement-page__aside {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e2e8f0;
  }

  .overview-grid,
  .completeness-panel__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
