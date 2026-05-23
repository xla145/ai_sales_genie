import {
  SearchCheck,
  TrendingUp,
  FileSpreadsheet,
  DollarSign,
  Code,
  BookOpen,
  Settings,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Circle,
  Clock,
  Plus,
  FileText,
  Lightbulb,
  LayoutDashboard,
  Upload,
  Sparkles,
  Building2,
  MapPin,
  ListChecks
} from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { RequirementAnalysis } from './RequirementAnalysis';
import { SolutionDesign } from './SolutionDesign';
import { IntelligenceAnalysis } from './IntelligenceAnalysis';
import { TaskList } from './TaskList';

interface WorkStage {
  id: string;
  name: string;
  description: string;
  status: 'completed' | 'in-progress' | 'pending';
  todoCount: number;
  icon: React.ReactNode;
}

interface Team {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  stages: WorkStage[];
}

interface Project {
  id: string;
  name: string;
  description: string;
  clientInfo: string;
  province: string;
  city: string;
  stage: string;
  industry: string;
  createdAt: string;
}

interface ProjectDashboardProps {
  project: Project;
  onBack: () => void;
}

export function ProjectDashboard({ project, onBack }: ProjectDashboardProps) {
  const [activeTeam, setActiveTeam] = useState('overview');
  const [selectedStage, setSelectedStage] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'workflow' | 'detail'>('workflow');

  const teams: Team[] = [
    {
      id: 'overview',
      name: '项目总览',
      icon: <LayoutDashboard className="w-5 h-5" />,
      color: 'bg-slate-500',
      stages: [
        {
          id: 'dashboard',
          name: '项目总览',
          description: '查看项目整体进度与状态',
          status: 'pending',
          todoCount: 0,
          icon: <LayoutDashboard className="w-5 h-5" />
        },
        {
          id: 'planning',
          name: '待规划',
          description: '需要规划的任务与计划',
          status: 'pending',
          todoCount: 0,
          icon: <FileText className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'input',
      name: '需求录入',
      icon: <FileText className="w-5 h-5" />,
      color: 'bg-indigo-500',
      stages: [
        {
          id: 'input',
          name: '需求录入',
          description: '录入项目需求信息',
          status: 'pending',
          todoCount: 0,
          icon: <FileText className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'intelligence',
      name: '情报支撑团队',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'bg-purple-500',
      stages: [
        {
          id: 'analysis',
          name: '情报分析',
          description: '收集行业情报、竞品分析',
          status: 'pending',
          todoCount: 4,
          icon: <TrendingUp className="w-5 h-5" />
        },
        {
          id: 'ppt',
          name: '售前PPT生成',
          description: '自动生成售前演示材料',
          status: 'pending',
          todoCount: 1,
          icon: <FileText className="w-5 h-5" />
        },
        {
          id: 'recommendation',
          name: '产品推荐',
          description: '推荐同类型解决方案',
          status: 'pending',
          todoCount: 2,
          icon: <Lightbulb className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'requirement',
      name: '需求分析团队',
      icon: <SearchCheck className="w-5 h-5" />,
      color: 'bg-blue-500',
      stages: [
        {
          id: 'analysis',
          name: '需求分析',
          description: '分析显性/隐性需求、识别风险点',
          status: 'in-progress',
          todoCount: 3,
          icon: <Lightbulb className="w-5 h-5" />
        },
        {
          id: 'evaluation',
          name: '需求评估',
          description: '多维度评估需求可行性与成本',
          status: 'pending',
          todoCount: 5,
          icon: <CheckCircle2 className="w-5 h-5" />
        },
        {
          id: 'clarification',
          name: '需求澄清',
          description: 'AI辅助澄清不明确的需求点',
          status: 'pending',
          todoCount: 2,
          icon: <Circle className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'solution',
      name: '方案设计团队',
      icon: <FileSpreadsheet className="w-5 h-5" />,
      color: 'bg-green-500',
      stages: [
        {
          id: 'prd',
          name: 'PRD编写',
          description: '产品需求文档撰写',
          status: 'pending',
          todoCount: 1,
          icon: <FileText className="w-5 h-5" />
        },
        {
          id: 'feature',
          name: '功能设计',
          description: '详细功能规格设计',
          status: 'pending',
          todoCount: 3,
          icon: <Circle className="w-5 h-5" />
        },
        {
          id: 'prototype',
          name: '原型设计',
          description: '交互原型设计',
          status: 'pending',
          todoCount: 2,
          icon: <Circle className="w-5 h-5" />
        },
        {
          id: 'process',
          name: '流程设计',
          description: '业务流程设计',
          status: 'pending',
          todoCount: 1,
          icon: <Circle className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'pricing',
      name: '报价决策团队',
      icon: <DollarSign className="w-5 h-5" />,
      color: 'bg-yellow-500',
      stages: [
        {
          id: 'quote',
          name: '产品报价',
          description: '【占位符】后续更新为报价功能',
          status: 'pending',
          todoCount: 0,
          icon: <DollarSign className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'development',
      name: '研发团队',
      icon: <Code className="w-5 h-5" />,
      color: 'bg-red-500',
      stages: [
        {
          id: 'dev',
          name: '开发任务',
          description: '【占位符】后续可根据原型反向分析功能点清单',
          status: 'pending',
          todoCount: 0,
          icon: <Code className="w-5 h-5" />
        }
      ]
    },
    {
      id: 'config',
      name: '系统管理',
      icon: <Settings className="w-5 h-5" />,
      color: 'bg-gray-500',
      stages: [
        {
          id: 'tasks',
          name: '任务列表',
          description: '查看所有 AI 生成任务与人工待办',
          status: 'in-progress' as const,
          todoCount: 3,
          icon: <ListChecks className="w-5 h-5" />
        },
        {
          id: 'model',
          name: '模型管理',
          description: 'AI模型配置与管理',
          status: 'pending',
          todoCount: 0,
          icon: <Settings className="w-5 h-5" />
        },
        {
          id: 'agent',
          name: '智能体管理',
          description: '智能体团队配置',
          status: 'pending',
          todoCount: 0,
          icon: <Circle className="w-5 h-5" />
        },
        {
          id: 'knowledge',
          name: '知识库',
          description: '行业知识与经验沉淀',
          status: 'pending',
          todoCount: 0,
          icon: <BookOpen className="w-5 h-5" />
        },
        {
          id: 'templates',
          name: '模板库',
          description: 'PPT、方案模板管理',
          status: 'pending',
          todoCount: 0,
          icon: <FileText className="w-5 h-5" />
        },
        {
          id: 'cases',
          name: '案例库',
          description: '历史项目案例沉淀',
          status: 'pending',
          todoCount: 0,
          icon: <Circle className="w-5 h-5" />
        }
      ]
    }
  ];

  const currentTeam = teams.find(t => t.id === activeTeam);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'in-progress':
        return <Clock className="w-5 h-5 text-blue-500" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'in-progress':
        return '进行中';
      default:
        return '未开始';
    }
  };

  const handleStageClick = (stageId: string) => {
    setSelectedStage(stageId);
    if (activeTeam === 'requirement' && stageId === 'analysis') {
      setActiveView('detail');
    }
  };

  return (
    <div className="size-full bg-gradient-to-br from-slate-50 via-blue-50/20 to-slate-50 flex flex-col">
      {/* 顶部导航栏 */}
      <div className="bg-white/95 backdrop-blur-md border-b border-slate-200/50 shadow-sm flex-shrink-0">
        {/* 顶部信息栏 */}
        <div className="px-6 py-3 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onBack}
              className="flex items-center gap-2 px-3 py-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="font-medium">返回</span>
            </motion.button>
            <div className="w-px h-5 bg-slate-300" />
            <div>
              <h1 className="text-lg font-bold text-slate-900">{project.name}</h1>
              <div className="flex items-center gap-3 mt-0.5">
                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                  <Building2 className="w-3 h-3" />
                  <span>{project.clientInfo}</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                  <MapPin className="w-3 h-3" />
                  <span>{project.province} · {project.city}</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-slate-600">{project.stage}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {teams.find(t => t.id === activeTeam)?.stages.reduce((sum, s) => sum + s.todoCount, 0) > 0 && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 border border-orange-200 rounded-lg">
                <Clock className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-semibold text-orange-700">
                  {teams.find(t => t.id === activeTeam)?.stages.reduce((sum, s) => sum + s.todoCount, 0)} 个待办
                </span>
              </div>
            )}
          </div>
        </div>

        {/* 团队Tab导航 */}
        <div className="px-6 flex gap-1 overflow-x-auto scrollbar-hide">
          {teams.map((team, index) => (
            <motion.button
              key={team.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
              whileHover={{ y: -2 }}
              onClick={() => {
                setActiveTeam(team.id);
                setSelectedStage(null);
              }}
              className={`relative flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all whitespace-nowrap ${
                activeTeam === team.id
                  ? 'text-blue-700'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {/* 活动指示器 */}
              {activeTeam === team.id && (
                <motion.div
                  layoutId="activeTabIndicator"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-blue-600"
                />
              )}

              <div className={`p-1 rounded-lg ${
                activeTeam === team.id
                  ? team.color.replace('bg-', 'bg-') + '/20'
                  : 'bg-slate-100'
              }`}>
                <div className={activeTeam === team.id ? 'text-blue-600' : 'text-slate-500'}>
                  {team.icon}
                </div>
              </div>

              <span>{team.name}</span>

              {/* 待办数量徽章 */}
              {team.stages.some(s => s.todoCount > 0) && (
                <span className={`ml-1 px-1.5 py-0.5 rounded-full text-xs font-semibold ${
                  activeTeam === team.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-orange-100 text-orange-700'
                }`}>
                  {team.stages.reduce((sum, s) => sum + s.todoCount, 0)}
                </span>
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeTeam === 'config' && selectedStage === 'tasks' ? (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full"
            >
              <TaskList />
            </motion.div>
          ) : activeTeam === 'intelligence' ? (
            <motion.div
              key="intelligence"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full"
            >
              <IntelligenceAnalysis onBack={onBack} />
            </motion.div>
          ) : activeTeam === 'requirement' ? (
            <motion.div
              key="requirement"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full"
            >
              <RequirementAnalysis onBack={onBack} />
            </motion.div>
          ) : activeTeam === 'solution' ? (
            <motion.div
              key="solution"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full"
            >
              <SolutionDesign onBack={onBack} />
            </motion.div>
          ) : activeTeam === 'input' ? (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full overflow-y-auto p-6"
            >
              <div className="max-w-7xl mx-auto">
                {/* 页面标题 */}
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg shadow-indigo-500/30">
                    <FileText className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900">需求录入</h2>
                    <p className="text-sm text-slate-600 mt-1">详细描述项目需求，为AI分析提供基础信息</p>
                  </div>
                </div>

                {/* 需求录入表单 - 左右分栏布局 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                  {/* 左侧：需求描述 */}
                  <div className="bg-white rounded-2xl border border-slate-200/50 p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <label className="text-base font-semibold text-slate-900">
                        需求描述 <span className="text-red-500">*</span>
                      </label>
                      <span className="text-xs text-slate-500">建议500字以上</span>
                    </div>
                    <p className="text-xs text-slate-600 mb-4">
                      建议包含：业务背景、核心目标、功能需求、特殊要求等
                    </p>
                    <textarea
                      placeholder="请详细描述项目需求...&#10;&#10;示例：&#10;&#10;【业务背景】&#10;当前企业面临的痛点和挑战...&#10;&#10;【核心目标】&#10;期望通过系统解决什么问题...&#10;&#10;【功能需求】&#10;需要实现哪些核心功能...&#10;&#10;【特殊要求】&#10;性能、安全、合规等特殊要求..."
                      className="w-full h-[calc(100vh-320px)] min-h-[400px] px-4 py-3 border-2 border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-sm shadow-sm hover:border-slate-300 transition-colors"
                    />
                  </div>

                  {/* 右侧：附件上传和提示 */}
                  <div className="space-y-6">
                    {/* 附件上传 */}
                    <div className="bg-white rounded-2xl border border-slate-200/50 p-6 shadow-sm h-[calc(100vh-440px)] min-h-[300px] flex flex-col">
                      <div className="flex items-center justify-between mb-4">
                        <label className="text-base font-semibold text-slate-900">
                          附件上传
                        </label>
                        <span className="text-xs text-slate-500">可选</span>
                      </div>
                      <p className="text-xs text-slate-600 mb-4">
                        支持上传需求文档、设计稿、参考资料等文件
                      </p>
                      <motion.div
                        whileHover={{ scale: 1.01 }}
                        className="flex-1 border-2 border-dashed border-slate-300 rounded-xl hover:border-indigo-400 hover:bg-gradient-to-br hover:from-indigo-50/50 hover:to-transparent transition-all cursor-pointer flex items-center justify-center"
                      >
                        <div className="flex flex-col items-center text-center gap-4 p-6">
                          <motion.div
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            className="p-5 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-2xl shadow-md"
                          >
                            <Upload className="w-8 h-8 text-indigo-600" />
                          </motion.div>
                          <div>
                            <p className="text-base text-slate-900 font-semibold mb-2">
                              点击上传或拖拽文件到此处
                            </p>
                            <p className="text-sm text-slate-600 mb-3">
                              支持 PDF、Word、Excel、PPT、图片等格式
                            </p>
                            <div className="flex flex-wrap gap-2 justify-center">
                              <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">.pdf</span>
                              <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">.doc</span>
                              <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">.xls</span>
                              <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">.ppt</span>
                              <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">.jpg</span>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    </div>

                    {/* 填写提示 */}
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5 shadow-sm">
                      <div className="flex gap-3">
                        <Lightbulb className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-indigo-900 mb-2">填写建议</p>
                          <p className="text-xs text-indigo-700 leading-relaxed">
                            建议从<span className="font-semibold">业务背景、核心目标、功能需求、用户角色、特殊要求</span>等维度描述，内容越详细，AI 分析越准确。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 操作按钮 - 独立在底部 */}
                <div className="bg-white rounded-2xl border border-slate-200/50 p-5 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Clock className="w-4 h-4" />
                      <span>填写完成后可保存草稿或直接提交</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="px-5 py-2.5 border-2 border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-all text-sm font-semibold"
                      >
                        保存草稿
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all flex items-center gap-2 text-sm font-semibold shadow-md"
                      >
                        <Sparkles className="w-4 h-4" />
                        提交并开始分析
                      </motion.button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : activeTeam === 'overview' ? (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="size-full overflow-y-auto p-6"
            >
          <div className="max-w-7xl mx-auto space-y-6">
            {/* 顶部数据卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-5 text-white shadow-md"
              >
                <div className="flex items-center justify-between mb-3">
                  <LayoutDashboard className="w-5 h-5" />
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">协作</span>
                </div>
                <div className="text-3xl font-bold mb-1">7</div>
                <div className="text-sm text-blue-100">团队模块</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-5 text-white shadow-md"
              >
                <div className="flex items-center justify-between mb-3">
                  <Clock className="w-5 h-5" />
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">待办</span>
                </div>
                <div className="text-3xl font-bold mb-1">
                  {teams.filter(t => t.id !== 'overview' && t.id !== 'input').reduce((sum, t) => sum + t.stages.reduce((s, stage) => s + stage.todoCount, 0), 0)}
                </div>
                <div className="text-sm text-orange-100">待办任务</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-5 text-white shadow-md"
              >
                <div className="flex items-center justify-between mb-3">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">进度</span>
                </div>
                <div className="text-3xl font-bold mb-1">35%</div>
                <div className="text-sm text-green-100">完成度</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white shadow-md"
              >
                <div className="flex items-center justify-between mb-3">
                  <FileText className="w-5 h-5" />
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">产出</span>
                </div>
                <div className="text-3xl font-bold mb-1">12</div>
                <div className="text-sm text-purple-100">文档</div>
              </motion.div>
            </div>

            {/* 项目信息 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="relative bg-white rounded-xl border border-slate-200/50 overflow-hidden shadow-sm"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100/30 to-transparent rounded-full blur-3xl" />
              <div className="relative p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">{project.name}</h2>
                    <p className="text-sm text-slate-600 leading-relaxed">{project.description}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-blue-700 font-medium mb-1">甲方名称</p>
                    <p className="text-sm font-semibold text-slate-900">{project.clientInfo}</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 font-medium mb-1">项目区域</p>
                    <p className="text-sm font-semibold text-slate-900">{project.province} · {project.city}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-green-700 font-medium mb-1">项目阶段</p>
                    <p className="text-sm font-semibold text-slate-900">{project.stage}</p>
                  </div>
                  <div className="p-3 bg-orange-50 rounded-lg">
                    <p className="text-xs text-orange-700 font-medium mb-1">归属行业</p>
                    <p className="text-sm font-semibold text-slate-900">{project.industry}</p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* 团队工作进度 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-xl border border-slate-200/50 p-6 shadow-sm"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-bold text-slate-900">团队工作进度</h3>
                <span className="text-xs text-slate-500">点击团队卡片查看详情</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {teams.filter(t => t.id !== 'overview' && t.id !== 'input').map((team) => (
                  <motion.div
                    key={team.id}
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="p-4 bg-gradient-to-br from-slate-50 to-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => setActiveTeam(team.id)}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`p-2 ${team.color} rounded-lg text-white shadow-sm`}>
                        {team.icon}
                      </div>
                      <span className="text-sm font-semibold text-slate-900">{team.name}</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-600">任务完成</span>
                        <span className="font-semibold text-slate-900">
                          {team.stages.filter(s => s.status === 'completed').length}/{team.stages.length}
                        </span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className={`${team.color} h-2 rounded-full transition-all`}
                          style={{ width: `${(team.stages.filter(s => s.status === 'completed').length / team.stages.length) * 100}%` }}
                        ></div>
                      </div>
                      {team.stages.reduce((sum, s) => sum + s.todoCount, 0) > 0 && (
                        <div className="flex items-center gap-1 text-xs text-orange-600 font-medium">
                          <Clock className="w-3 h-3" />
                          {team.stages.reduce((sum, s) => sum + s.todoCount, 0)} 个待办
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* 最近活动 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-xl border border-slate-200/50 p-6 shadow-sm"
            >
              <h3 className="text-lg font-bold text-slate-900 mb-4">最近活动</h3>
              <div className="space-y-3">
                {[
                  { time: '2小时前', action: '需求分析阶段已更新', user: '张三', team: '需求分析团队' },
                  { time: '5小时前', action: '情报分析报告已生成', user: '李四', team: '情报支撑团队' },
                  { time: '昨天 15:30', action: 'PRD文档已创建', user: '王五', team: '方案设计团队' },
                  { time: '昨天 10:20', action: '项目需求已录入', user: '赵六', team: '需求分析团队' },
                ].map((activity, index) => (
                  <div key={index} className="flex items-start gap-4 p-3 hover:bg-slate-50 rounded-lg transition-colors">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-900 font-medium mb-1">{activity.action}</p>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span>{activity.user}</span>
                        <span>·</span>
                        <span>{activity.team}</span>
                        <span>·</span>
                        <span>{activity.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
            </motion.div>
          ) : (
            <motion.div
              key={activeTeam}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex-1 overflow-y-auto p-4"
            >
        <div className="max-w-7xl mx-auto">
          {/* 工作流程卡片 */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className={`p-2 ${currentTeam?.color} rounded-lg text-white`}>
                {currentTeam?.icon}
              </div>
              <div>
                <h3 className="text-lg font-medium text-slate-900">{currentTeam?.name}</h3>
                <p className="text-xs text-slate-600">
                  按照流程完成各阶段工作，推进项目进展
                </p>
              </div>
            </div>

            {/* 流程阶段 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {currentTeam?.stages.map((stage, index) => (
                <div key={stage.id} className="relative">
                  {/* 连接线 */}
                  {index < (currentTeam?.stages.length || 0) - 1 && (
                    <div className="hidden lg:block absolute top-1/2 left-full w-3 -translate-y-1/2 z-0">
                      <ArrowRight className="w-4 h-4 text-slate-300" />
                    </div>
                  )}

                  {/* 阶段卡片 */}
                  <div
                    onClick={() => handleStageClick(stage.id)}
                    className={`relative w-full p-4 rounded-lg transition-all cursor-pointer ${
                      selectedStage === stage.id
                        ? 'ring-2 ring-blue-500'
                        : ''
                    } ${
                      stage.status === 'completed'
                        ? 'bg-green-50 border border-green-200'
                        : stage.status === 'in-progress'
                        ? 'bg-blue-50 border border-blue-200'
                        : 'bg-white border border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {/* 状态指示器 */}
                    <div className="flex items-center justify-between mb-3">
                      {getStatusIcon(stage.status)}
                      {stage.todoCount > 0 && (
                        <span className="px-2 py-0.5 bg-orange-500 text-white rounded-full text-xs font-medium">
                          {stage.todoCount} 待办
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 mb-2">
                      <div className={`${
                        stage.status === 'in-progress' ? 'text-blue-600' :
                        stage.status === 'completed' ? 'text-green-600' :
                        'text-slate-600'
                      }`}>
                        {stage.icon}
                      </div>
                      <h4 className={`text-sm font-medium ${
                        stage.status === 'in-progress' ? 'text-blue-900' :
                        stage.status === 'completed' ? 'text-green-900' :
                        'text-slate-900'
                      }`}>
                        {stage.name}
                      </h4>
                    </div>

                    <p className="text-xs text-slate-600 mb-3 line-clamp-2">
                      {stage.description}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className={`text-xs ${
                        stage.status === 'completed' ? 'text-green-600' :
                        stage.status === 'in-progress' ? 'text-blue-600' :
                        'text-slate-500'
                      }`}>
                        {getStatusText(stage.status)}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                        }}
                        className="p-1 hover:bg-slate-100 rounded transition-colors"
                      >
                        <Plus className="w-3.5 h-3.5 text-slate-600" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 详细操作区 */}
          {selectedStage && (
            <div className="bg-white rounded-lg border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                  {currentTeam?.stages.find(s => s.id === selectedStage)?.icon}
                </div>
                <h3 className="text-base font-medium text-slate-900">
                  {currentTeam?.stages.find(s => s.id === selectedStage)?.name}
                </h3>
              </div>
              <div className="text-center py-12 text-slate-500">
                <div className="w-16 h-16 mx-auto mb-3 bg-slate-100 rounded-lg flex items-center justify-center">
                  {activeTeam === 'pricing' ? (
                    <DollarSign className="w-8 h-8 text-yellow-600" />
                  ) : activeTeam === 'development' ? (
                    <Code className="w-8 h-8 text-red-600" />
                  ) : (
                    <FileText className="w-8 h-8 text-blue-600" />
                  )}
                </div>
                {activeTeam === 'pricing' ? (
                  <>
                    <p className="text-base mb-1 font-medium text-slate-900">报价功能开发中</p>
                    <p className="text-xs text-slate-600">后续将提供智能成本核算与报价生成功能</p>
                  </>
                ) : activeTeam === 'development' ? (
                  <>
                    <p className="text-base mb-1 font-medium text-slate-900">原型分析功能开发中</p>
                    <p className="text-xs text-slate-600 mb-3">后续可根据原型反向分析功能点清单</p>
                    <div className="max-w-md mx-auto text-left">
                      <div className="p-3 bg-blue-50 border-l-2 border-blue-500 rounded">
                        <p className="text-xs text-slate-700">
                          <strong>预计功能：</strong>上传原型文件后，AI将自动识别页面结构、交互流程和功能模块，生成详细的功能点清单，帮助快速评估开发工作量。
                        </p>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="text-base mb-1 text-slate-900">此功能正在开发中</p>
                    <p className="text-xs text-slate-600">点击上方"+"按钮可以创建新任务</p>
                  </>
                )}
              </div>
            </div>
          )}

          {/* 智能推荐 */}
          {!selectedStage && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-amber-500 rounded-lg">
                  <Lightbulb className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-slate-900 mb-2">
                    智能建议
                  </h4>
                  <p className="text-xs text-slate-600 mb-3">
                    根据当前项目进度，建议您：
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2 text-xs text-slate-700 bg-white p-2 rounded">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span>优先完成"需求分析"阶段的 3 个待办任务</span>
                    </li>
                    <li className="flex items-start gap-2 text-xs text-slate-700 bg-white p-2 rounded">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span>可以提前准备情报分析所需的行业资料</span>
                    </li>
                    <li className="flex items-start gap-2 text-xs text-slate-700 bg-white p-2 rounded">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span>查看知识库中的相关案例作为参考</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            )}
          </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
