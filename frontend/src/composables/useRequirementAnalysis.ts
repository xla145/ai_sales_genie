import { computed, reactive, ref } from 'vue'
import { PROJECT_TYPE_OPTIONS } from '@/constants/project'
import { buildRequirementKey, createDefaultRequirementAnalysis, isFilled, normalizeRequirementAnalysis, renumberRiskItems, renumberScenarioItems } from '@/utils/requirement'
import type {
  RequirementAnalysis,
  RequirementAttachmentItem,
  RequirementFunctions,
  RequirementPendingItem,
  RequirementRiskItem,
  RequirementScenarioItem,
} from '@/types/project'

interface BasicFormItem {
  key: keyof RequirementAnalysis['basic']
  label: string
  value: string
  placeholder?: string
  hint?: string
  type?: 'text' | 'textarea' | 'radio'
  rows?: number
  options?: string[]
}

interface CoreFormItem {
  key: keyof RequirementAnalysis['core']
  title: string
  value: string
  placeholder: string
  rows?: number
}

interface FunctionFieldItem {
  label: string
  value: string
  placeholder?: string
  type?: 'text' | 'textarea'
  rows?: number
}

interface FunctionGroupItem {
  key: 'function-desc' | 'non-function' | 'constraints'
  title: string
  fields: FunctionFieldItem[]
}

const getFunctionGroup = (key: FunctionGroupItem['key']): keyof RequirementFunctions => {
  if (key === 'function-desc') return 'functionDesc'
  if (key === 'non-function') return 'nonFunction'
  return 'constraints'
}

const countFilled = (values: string[]) => values.filter((value) => isFilled(value)).length

export const useRequirementAnalysis = () => {
  const requirementState = reactive<RequirementAnalysis>(createDefaultRequirementAnalysis())
  const supplementNotes = ref('')
  const pendingUnknownInfo = ref('')
  const pendingAssumptions = ref('')
  const attachments = reactive<RequirementAttachmentItem[]>([])
  const basicItems = reactive<BasicFormItem[]>([
    { key: 'projectName', label: '项目名称', value: '', placeholder: '请输入项目名称' },
    { key: 'projectSummary', label: '项目摘要', value: '', placeholder: '请输入项目摘要', hint: '简要描述项目目标与背景', type: 'textarea', rows: 3 },
    { key: 'industry', label: '对应行业', value: '', placeholder: '如：制造业、电商、金融等' },
    {
      key: 'projectType',
      label: '项目类型',
      value: '',
      type: 'radio',
      options: [...PROJECT_TYPE_OPTIONS],
    },
    { key: 'keywords', label: '项目关键词', value: '', placeholder: '多个关键词用逗号分隔' },
  ])
  const coreItems = reactive<CoreFormItem[]>([
    { key: 'background', title: '项目背景', value: '', placeholder: '为什么要做这个项目？当前现状和行业背景如何？', rows: 4 },
    { key: 'goal', title: '项目目标', value: '', placeholder: '明确业务目标、用户目标和成功指标', rows: 4 },
    { key: 'users', title: '核心用户', value: '', placeholder: '用户类型、用户角色与核心行为', rows: 4 },
    { key: 'painPoints', title: '当前痛点', value: '', placeholder: '用户当前遇到的主要问题和困难', rows: 4 },
  ])
  const scenarioItems = reactive<RequirementScenarioItem[]>([])
  const functionItems = reactive<FunctionGroupItem[]>([
    {
      key: 'function-desc',
      title: '功能描述',
      fields: [
        { label: '显性核心功能点', value: '', placeholder: '明确提出的功能需求', type: 'textarea', rows: 3 },
        { label: '潜在功能点', value: '', placeholder: '隐含的、可能需要的功能', type: 'textarea', rows: 3 },
        { label: '技术选型', value: '', placeholder: '技术栈、框架等' },
        { label: '技术架构', value: '', placeholder: '系统架构设计', type: 'textarea', rows: 2 },
        { label: '依赖系统', value: '', placeholder: '需要对接的其他系统' },
      ],
    },
    {
      key: 'non-function',
      title: '非功能需求',
      fields: [
        { label: '性能要求', value: '', placeholder: '如：并发量、响应时间等' },
        { label: '可用性要求', value: '', placeholder: '如：系统可用性99.9%' },
        { label: '安全性要求', value: '', placeholder: '如：数据加密、权限控制等' },
        { label: '兼容性要求', value: '', placeholder: '如：浏览器、操作系统兼容性' },
      ],
    },
    {
      key: 'constraints',
      title: '约束条件',
      fields: [
        { label: '性能约束', value: '', placeholder: '性能方面的限制条件' },
        { label: '可用性约束', value: '', placeholder: '可用性方面的限制条件' },
        { label: '安全性约束', value: '', placeholder: '安全性方面的限制条件' },
        { label: '兼容性约束', value: '', placeholder: '兼容性方面的限制条件' },
      ],
    },
  ])
  const riskItems = reactive<RequirementRiskItem[]>([])
  const pendingItems = reactive<RequirementPendingItem[]>([])

  const syncViewStateFromRequirement = (data: RequirementAnalysis) => {
    basicItems.forEach((item) => {
      item.value = data.basic[item.key] ?? ''
    })

    coreItems.forEach((item) => {
      item.value = data.core[item.key] ?? ''
    })

    scenarioItems.splice(0, scenarioItems.length, ...data.scenarios.map((item) => ({ ...item })))

    functionItems.forEach((group) => {
      const values = data.functions[getFunctionGroup(group.key)]
      group.fields.forEach((field) => {
        field.value = values?.[field.label] ?? ''
      })
    })

    riskItems.splice(0, riskItems.length, ...data.risks.map((item) => ({ ...item })))
    pendingUnknownInfo.value = data.pending.unknownInfo
    pendingAssumptions.value = data.pending.assumptions
    pendingItems.splice(0, pendingItems.length, ...data.pending.items.map((item) => ({ ...item })))
    attachments.splice(0, attachments.length, ...data.attachments.map((item) => ({ ...item })))
    supplementNotes.value = data.supplement.notes
  }

  const buildRequirementAnalysis = (): RequirementAnalysis => ({
    basic: {
      projectName: basicItems.find((item) => item.key === 'projectName')?.value ?? '',
      projectSummary: basicItems.find((item) => item.key === 'projectSummary')?.value ?? '',
      industry: basicItems.find((item) => item.key === 'industry')?.value ?? '',
      projectType: basicItems.find((item) => item.key === 'projectType')?.value ?? '',
      keywords: basicItems.find((item) => item.key === 'keywords')?.value ?? '',
    },
    core: {
      background: coreItems.find((item) => item.key === 'background')?.value ?? '',
      goal: coreItems.find((item) => item.key === 'goal')?.value ?? '',
      users: coreItems.find((item) => item.key === 'users')?.value ?? '',
      painPoints: coreItems.find((item) => item.key === 'painPoints')?.value ?? '',
    },
    scenarios: scenarioItems.map((item) => ({ ...item })),
    functions: {
      functionDesc: Object.fromEntries(functionItems[0].fields.map((field) => [field.label, field.value])),
      nonFunction: Object.fromEntries(functionItems[1].fields.map((field) => [field.label, field.value])),
      constraints: Object.fromEntries(functionItems[2].fields.map((field) => [field.label, field.value])),
    },
    risks: riskItems.map((item) => ({ ...item })),
    pending: {
      unknownInfo: pendingUnknownInfo.value,
      assumptions: pendingAssumptions.value,
      items: pendingItems.map((item) => ({ ...item })),
    },
    attachments: attachments.map((item) => ({ ...item })),
    supplement: {
      notes: supplementNotes.value,
    },
  })

  const replaceRequirementState = (data: RequirementAnalysis) => {
    Object.assign(requirementState, data)
    syncViewStateFromRequirement(data)
  }

  const applyRequirementAnalysis = (source?: RequirementAnalysis) => {
    const normalized = normalizeRequirementAnalysis(source)
    replaceRequirementState(normalized)
    return normalized
  }

  const sectionProgress = computed(() => {
    const basicValues = basicItems.map((item) => item.value)
    const coreValues = coreItems.map((item) => item.value)
    const functionValues = functionItems.flatMap((group) => group.fields.map((field) => field.value))
    const scenarioValueCount = scenarioItems.filter((item) => isFilled(item.description) || isFilled(item.flow)).length
    const riskValueCount = riskItems.filter((item) => isFilled(item.description) || isFilled(item.impact) || isFilled(item.strategy)).length
    const pendingChecklistCount = pendingItems.filter((item) => item.checked).length
    const pendingExtraCount = [pendingUnknownInfo.value, pendingAssumptions.value].filter((item) => isFilled(item)).length

    return {
      basic: { filled: countFilled(basicValues), total: basicValues.length },
      core: { filled: countFilled(coreValues), total: coreValues.length },
      scenario: { filled: scenarioValueCount, total: Math.max(scenarioItems.length, 1) },
      function: { filled: countFilled(functionValues), total: functionValues.length },
      risk: { filled: riskValueCount, total: Math.max(riskItems.length, 1) },
      pending: { filled: pendingChecklistCount + pendingExtraCount, total: pendingItems.length + 2 },
    }
  })

  const completionRate = computed(() => {
    const values = Object.values(sectionProgress.value)
    const total = values.reduce((sum, item) => sum + item.total, 0)
    const filled = values.reduce((sum, item) => sum + item.filled, 0)
    return total ? Math.round((filled / total) * 100) : 0
  })

  const readinessScore = computed(() => completionRate.value)
  const readinessLevel = computed(() => {
    if (readinessScore.value >= 85) return { level: 'A', label: '优秀' }
    if (readinessScore.value >= 65) return { level: 'B', label: '良好' }
    if (readinessScore.value >= 40) return { level: 'C', label: '待完善' }
    return { level: 'D', label: '较弱' }
  })

  const readinessMetrics = computed(() => [
    { label: '需求就绪度', value: `${readinessScore.value}分` },
    { label: '需求清晰度', value: `${Math.min(sectionProgress.value.basic.filled + sectionProgress.value.core.filled, 9) * 10}分` },
    { label: '项目风险度', value: `${Math.min(riskItems.length * 15 + pendingItems.filter((item) => !item.checked).length * 5, 100)}分` },
    { label: '技术复杂度', value: `${Math.min(sectionProgress.value.function.filled * 8 + scenarioItems.length * 6, 100)}分` },
  ])

  const addScenarioItem = () => {
    scenarioItems.push({
      key: buildRequirementKey('scenario'),
      title: `场景${scenarioItems.length + 1}`,
      description: '',
      flow: '',
    })
  }

  const removeScenarioItem = (key: string) => {
    const index = scenarioItems.findIndex((item) => item.key === key)
    if (index === -1) return
    scenarioItems.splice(index, 1)
    if (!scenarioItems.length) addScenarioItem()
    renumberScenarioItems(scenarioItems)
  }

  const addRiskItem = () => {
    riskItems.push({
      key: buildRequirementKey('risk'),
      title: `风险点${riskItems.length + 1}`,
      level: '中',
      description: '',
      impact: '',
      strategy: '',
    })
  }

  const removeRiskItem = (key: string) => {
    const index = riskItems.findIndex((item) => item.key === key)
    if (index === -1) return
    riskItems.splice(index, 1)
    if (!riskItems.length) addRiskItem()
    renumberRiskItems(riskItems)
  }

  return {
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
    replaceRequirementState,
    requirementState,
    riskItems,
    scenarioItems,
    sectionProgress,
    supplementNotes,
    addRiskItem,
    addScenarioItem,
    applyRequirementAnalysis,
    removeRiskItem,
    removeScenarioItem,
  }
}
