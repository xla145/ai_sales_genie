import { computed, ref } from 'vue'

export type IntelligenceSectionType = 'overview' | 'history'
export type IntelligenceDetailMode = 'material' | 'prototype'

export interface IntelligenceHistoryProject {
  id: string
  name: string
  industry: string
  date: string
  tags: string[]
  client: string
  description: string
}

const INTELLIGENCE_SECTIONS = [
  { id: 'overview' as IntelligenceSectionType, title: '情报概览' },
  { id: 'history' as IntelligenceSectionType, title: '历史参考案例' },
]

const INTELLIGENCE_ANALYSIS_RESULTS = [
  { title: '客户企业信息', summary: '已归纳客户业务背景、核心场景与组织特点，可作为需求输入补充。' },
  { title: '行业政策分析', summary: '已提炼近期监管和政策趋势，适合作为方案合规章节参考。' },
  { title: '竞品情报分析', summary: '已总结典型竞品功能定位与差异点，便于方案突出优势。' },
  { title: '技术趋势洞察', summary: '已形成技术选型与实施方向建议，可为方案设计页提供支撑。' },
]

const INTELLIGENCE_HISTORY_PROJECTS: IntelligenceHistoryProject[] = [
  {
    id: '1',
    name: '智能物流管理平台',
    industry: '物流/仓储',
    date: '2026-03-15',
    tags: ['物流', 'AI', '大数据'],
    client: '某大型物流集团',
    description: '为大型物流企业打造的智能化物流管理平台，实现货物全程追踪、智能调度和数据分析。',
  },
  {
    id: '2',
    name: '供应链协同系统',
    industry: '制造业',
    date: '2026-02-20',
    tags: ['供应链', 'ERP', '协同'],
    client: '某制造企业',
    description: '为制造企业打造的供应链协同管理系统，实现上下游企业的高效协同与数据互通。',
  },
  {
    id: '3',
    name: '仓储自动化解决方案',
    industry: '物流/仓储',
    date: '2026-01-10',
    tags: ['自动化', '物联网', '仓储'],
    client: '某电商仓储公司',
    description: '基于物联网技术的智能仓储自动化系统，实现货物自动分拣、智能存储和精准盘点。',
  },
  {
    id: '4',
    name: '智慧园区管理平台',
    industry: '政府/公共服务',
    date: '2025-12-05',
    tags: ['园区管理', '智慧城市', '物联网'],
    client: '某高新技术产业园',
    description: '为产业园区打造的智慧化管理平台，整合安防、能源、物业、招商等多个系统。',
  },
  {
    id: '5',
    name: '医疗预约挂号系统',
    industry: '医疗健康',
    date: '2025-11-18',
    tags: ['医疗', '预约', '移动应用'],
    client: '市中心医院',
    description: '为医院打造的线上预约挂号系统，支持多渠道预约、智能分诊和电子病历管理。',
  },
]

export const useIntelligenceAnalysis = () => {
  const selectedSection = ref<IntelligenceSectionType>('overview')
  const analysisStarted = ref(false)
  const searchKeyword = ref('')
  const appliedKeyword = ref('')
  const detailDialogVisible = ref(false)
  const detailMode = ref<IntelligenceDetailMode>('material')
  const activeProject = ref<IntelligenceHistoryProject | null>(null)

  const filteredProjects = computed(() => {
    const keyword = appliedKeyword.value.trim().toLowerCase()
    if (!keyword) return INTELLIGENCE_HISTORY_PROJECTS
    return INTELLIGENCE_HISTORY_PROJECTS.filter((project) => {
      const haystack = [project.name, project.industry, project.client, project.description, ...project.tags].join(' ').toLowerCase()
      return haystack.includes(keyword)
    })
  })

  const startAnalysis = () => {
    analysisStarted.value = true
  }

  const applySearch = () => {
    appliedKeyword.value = searchKeyword.value
  }

  const openDetail = (mode: IntelligenceDetailMode, project: IntelligenceHistoryProject) => {
    detailMode.value = mode
    activeProject.value = project
    detailDialogVisible.value = true
  }

  return {
    activeProject,
    analysisResults: INTELLIGENCE_ANALYSIS_RESULTS,
    analysisStarted,
    appliedKeyword,
    detailDialogVisible,
    detailMode,
    filteredProjects,
    searchKeyword,
    sections: INTELLIGENCE_SECTIONS,
    selectedSection,
    applySearch,
    openDetail,
    startAnalysis,
  }
}
