export interface WorkflowStageItem {
  name: string
  description: string
}

export const PRICING_WORKFLOW_STAGES: WorkflowStageItem[] = [
  {
    name: '产品报价',
    description: '【占位符】后续更新为报价功能',
  },
]

export const DEVELOPMENT_WORKFLOW_STAGES: WorkflowStageItem[] = [
  {
    name: '开发任务',
    description: '【占位符】后续可根据原型反向分析功能点清单',
  },
]

export const KNOWLEDGE_WORKFLOW_STAGES: WorkflowStageItem[] = [
  {
    name: '知识库',
    description: '行业知识与经验沉淀',
  },
  {
    name: '模板库',
    description: 'PPT、方案模板管理',
  },
  {
    name: '案例库',
    description: '历史项目案例沉淀',
  },
]

export const SYSTEM_CONFIG_WORKFLOW_STAGES: WorkflowStageItem[] = [
  {
    name: '模型管理',
    description: 'AI模型配置与管理',
  },
  {
    name: '智能体管理',
    description: '智能体团队配置',
  },
]
