import { DEFAULT_REQUIREMENT_ANALYSIS } from '@/constants/project'
import type {
  ProjectConfig,
  RequirementAnalysis,
  RequirementAttachmentItem,
  RequirementPendingItem,
  RequirementRiskItem,
  RequirementScenarioItem,
} from '@/types/project'

const cloneScenario = (item: RequirementScenarioItem, index: number): RequirementScenarioItem => ({
  key: item.key || buildRequirementKey('scenario', index),
  title: `场景${index + 1}`,
  description: item.description ?? '',
  flow: item.flow ?? '',
})

const cloneRisk = (item: RequirementRiskItem, index: number): RequirementRiskItem => ({
  key: item.key || buildRequirementKey('risk', index),
  title: `风险点${index + 1}`,
  level: item.level ?? '中',
  description: item.description ?? '',
  impact: item.impact ?? '',
  strategy: item.strategy ?? '',
})

const clonePendingItem = (item: RequirementPendingItem): RequirementPendingItem => ({
  title: item.title ?? '',
  text: item.text ?? '',
  checked: Boolean(item.checked),
})

const cloneAttachment = (item: RequirementAttachmentItem): RequirementAttachmentItem => ({
  id: item.id ?? null,
  name: item.name ?? '',
  meta: item.meta ?? '',
  size: item.size ?? null,
  content_type: item.content_type ?? null,
  storage_path: item.storage_path ?? null,
  uploaded_at: item.uploaded_at ?? null,
})

export const buildRequirementKey = (prefix: 'scenario' | 'risk', index?: number) => {
  const suffix = index == null ? Date.now() : `${Date.now()}-${index}`
  return `${prefix}-${suffix}`
}

export const isFilled = (value: string | null | undefined) => (value ?? '').trim().length > 0

export const createDefaultRequirementAnalysis = (): RequirementAnalysis => ({
  basic: { ...DEFAULT_REQUIREMENT_ANALYSIS.basic },
  core: { ...DEFAULT_REQUIREMENT_ANALYSIS.core },
  scenarios: DEFAULT_REQUIREMENT_ANALYSIS.scenarios.map((item, index) => cloneScenario(item, index)),
  functions: {
    functionDesc: { ...DEFAULT_REQUIREMENT_ANALYSIS.functions.functionDesc },
    nonFunction: { ...DEFAULT_REQUIREMENT_ANALYSIS.functions.nonFunction },
    constraints: { ...DEFAULT_REQUIREMENT_ANALYSIS.functions.constraints },
  },
  risks: DEFAULT_REQUIREMENT_ANALYSIS.risks.map((item, index) => cloneRisk(item, index)),
  pending: {
    unknownInfo: DEFAULT_REQUIREMENT_ANALYSIS.pending.unknownInfo,
    assumptions: DEFAULT_REQUIREMENT_ANALYSIS.pending.assumptions,
    items: DEFAULT_REQUIREMENT_ANALYSIS.pending.items.map(clonePendingItem),
  },
  attachments: DEFAULT_REQUIREMENT_ANALYSIS.attachments.map(cloneAttachment),
  supplement: {
    notes: DEFAULT_REQUIREMENT_ANALYSIS.supplement.notes,
  },
})

export const normalizeRequirementAnalysis = (
  source?: ProjectConfig['requirementAnalysis'] | ProjectConfig,
): RequirementAnalysis => {
  const defaults = createDefaultRequirementAnalysis()
  const incoming: ProjectConfig['requirementAnalysis'] | undefined = source && 'requirementAnalysis' in source
    ? source.requirementAnalysis
    : source as ProjectConfig['requirementAnalysis'] | undefined
  const normalizedScenarios = Array.isArray(incoming?.scenarios) && incoming.scenarios.length
    ? incoming.scenarios.map((item, index) => cloneScenario(item, index))
    : defaults.scenarios
  const normalizedRisks = Array.isArray(incoming?.risks) && incoming.risks.length
    ? incoming.risks.map((item, index) => cloneRisk(item, index))
    : defaults.risks
  const normalizedPendingItems = Array.isArray(incoming?.pending?.items) && incoming.pending.items.length
    ? incoming.pending.items.map(clonePendingItem)
    : defaults.pending.items
  const normalizedAttachments = Array.isArray(incoming?.attachments) && incoming.attachments.length
    ? incoming.attachments.map(cloneAttachment)
    : defaults.attachments

  return {
    basic: {
      ...defaults.basic,
      ...(incoming?.basic ?? {}),
    },
    core: {
      ...defaults.core,
      ...(incoming?.core ?? {}),
    },
    scenarios: normalizedScenarios,
    functions: {
      functionDesc: {
        ...defaults.functions.functionDesc,
        ...(incoming?.functions?.functionDesc ?? {}),
      },
      nonFunction: {
        ...defaults.functions.nonFunction,
        ...(incoming?.functions?.nonFunction ?? {}),
      },
      constraints: {
        ...defaults.functions.constraints,
        ...(incoming?.functions?.constraints ?? {}),
      },
    },
    risks: normalizedRisks,
    pending: {
      unknownInfo: incoming?.pending?.unknownInfo ?? defaults.pending.unknownInfo,
      assumptions: incoming?.pending?.assumptions ?? defaults.pending.assumptions,
      items: normalizedPendingItems,
    },
    attachments: normalizedAttachments,
    supplement: {
      notes: incoming?.supplement?.notes ?? defaults.supplement.notes,
    },
  }
}

export const renumberScenarioItems = (items: RequirementScenarioItem[]) => {
  items.forEach((item, index) => {
    item.title = `场景${index + 1}`
  })
}

export const renumberRiskItems = (items: RequirementRiskItem[]) => {
  items.forEach((item, index) => {
    item.title = `风险点${index + 1}`
  })
}
