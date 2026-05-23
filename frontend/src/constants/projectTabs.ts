export interface ProjectTabItem {
  name: string
  label: string
  icon: string
  color: 'slate' | 'indigo' | 'purple' | 'blue' | 'green' | 'yellow' | 'red' | 'gray'
  badge?: number
}

export const PROJECT_TABS: ProjectTabItem[] = [
  { name: 'overview', label: '项目总览', icon: 'layout-dashboard', color: 'slate' },
  { name: 'input', label: '需求录入', icon: 'file-text', color: 'indigo' },
  { name: 'intelligence', label: '情报支撑团队', icon: 'trending-up', color: 'purple', badge: 7 },
  { name: 'requirement', label: '需求分析团队', icon: 'search-check', color: 'blue', badge: 10 },
  { name: 'solution', label: '方案设计团队', icon: 'file-spreadsheet', color: 'green', badge: 7 },
  { name: 'pricing', label: '报价决策团队', icon: 'dollar-sign', color: 'yellow' },
  { name: 'development', label: '研发团队', icon: 'code', color: 'red' },
  { name: 'config', label: '系统管理', icon: 'settings', color: 'gray', badge: 3 },
]
