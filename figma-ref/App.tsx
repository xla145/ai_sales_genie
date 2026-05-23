import { useState, useEffect } from 'react';
import { Plus, FolderKanban, Sparkles, LogOut, User } from 'lucide-react';
import { motion } from 'motion/react';
import { ProjectCard } from './components/ProjectCard';
import { ProjectModal } from './components/ProjectModal';
import { DeleteConfirmModal } from './components/DeleteConfirmModal';
import { ProjectDashboard } from './components/ProjectDashboard';
import { Login } from './components/Login';


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

// 示例项目数据
const demoProjects: Project[] = [
  {
    id: 'demo-1',
    name: '智能仓储管理系统',
    description: '为大型物流企业打造智能化仓储管理平台，实现货物自动化管理、智能分拣和实时库存监控，提升仓储运营效率',
    clientInfo: 'XX物流集团有限公司',
    province: '上海',
    city: '浦东新区',
    stage: '需求阶段',
    industry: '物流/仓储',
    createdAt: '2026-04-15T08:30:00.000Z'
  },
  {
    id: 'demo-2',
    name: '智慧校园综合管理平台',
    description: '构建集教务管理、学生服务、校园安防于一体的智慧校园综合平台，提升校园信息化管理水平',
    clientInfo: '某重点大学',
    province: '北京',
    city: '海淀区',
    stage: '方案设计',
    industry: '教育',
    createdAt: '2026-04-10T10:15:00.000Z'
  },
  {
    id: 'demo-3',
    name: '医疗影像AI辅助诊断系统',
    description: '基于深度学习的医疗影像智能分析系统，辅助医生快速准确诊断，提高医疗服务质量和效率',
    clientInfo: '市人民医院',
    province: '广东',
    city: '深圳市',
    stage: '需求分析',
    industry: '医疗健康',
    createdAt: '2026-04-05T14:20:00.000Z'
  },
  {
    id: 'demo-4',
    name: '供应链金融服务平台',
    description: '为中小企业提供供应链金融服务，通过数字化手段降低融资成本，提升资金流转效率',
    clientInfo: '某商业银行',
    province: '浙江',
    city: '杭州市',
    stage: '情报收集',
    industry: '金融',
    createdAt: '2026-03-28T09:45:00.000Z'
  }
];

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<string>('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [deletingProject, setDeletingProject] = useState<Project | null>(null);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [newProjectId, setNewProjectId] = useState<string | null>(null);
  const [fadingProjectId, setFadingProjectId] = useState<string | null>(null);


  useEffect(() => {
    // 检查登录状态
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setIsLoggedIn(true);
      setCurrentUser(savedUser);
    }

    const savedProjects = localStorage.getItem('projects');
    if (savedProjects) {
      setProjects(JSON.parse(savedProjects));
    } else {
      // 如果没有保存的项目，使用示例项目
      setProjects(demoProjects);
      localStorage.setItem('projects', JSON.stringify(demoProjects));
    }
  }, []);

  const handleLogin = (email: string, password: string) => {
    // 简单的演示登录逻辑
    setIsLoggedIn(true);
    setCurrentUser(email);
    localStorage.setItem('currentUser', email);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser('');
    setCurrentProject(null);
    localStorage.removeItem('currentUser');
  };

  const saveProjects = (newProjects: Project[]) => {
    setProjects(newProjects);
    localStorage.setItem('projects', JSON.stringify(newProjects));
  };

  const handleCreateProject = (name: string, description: string, clientInfo: string, province: string, city: string, stage: string, industry: string) => {
    const newProject: Project = {
      id: Date.now().toString(),
      name,
      description,
      clientInfo,
      province,
      city,
      stage,
      industry,
      createdAt: new Date().toISOString(),
    };
    saveProjects([...projects, newProject]);
    setIsCreateModalOpen(false);
    setNewProjectId(newProject.id);
    setTimeout(() => setNewProjectId(null), 400);
  };

  const handleEditProject = (name: string, description: string, clientInfo: string, province: string, city: string, stage: string, industry: string) => {
    if (!editingProject) return;
    const updatedProjects = projects.map(p =>
      p.id === editingProject.id ? { ...p, name, description, clientInfo, province, city, stage, industry } : p
    );
    saveProjects(updatedProjects);
    setEditingProject(null);
  };

  const handleDeleteProject = () => {
    if (!deletingProject) return;
    setFadingProjectId(deletingProject.id);
    setTimeout(() => {
      const updatedProjects = projects.filter(p => p.id !== deletingProject.id);
      saveProjects(updatedProjects);
      setDeletingProject(null);
      setFadingProjectId(null);
    }, 300);
  };

  const handleEnterProject = (project: Project) => {
    setCurrentProject(project);
  };

  const handleBackToProjects = () => {
    setCurrentProject(null);
  };

  // 如果未登录，显示登录页面
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  if (currentProject) {
    return (
      <ProjectDashboard
        project={currentProject}
        onBack={handleBackToProjects}
      />
    );
  }

  return (
    <div className="size-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-50 overflow-auto">
      <div className="max-w-7xl mx-auto p-6">
        {/* 顶部头部 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg shadow-blue-500/30">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 bg-clip-text text-transparent">
                  OPC 规范支持中心
                </h1>
              </div>
              <p className="text-sm text-slate-600 ml-14">
                三坨理想泥 · 智能售前协作平台
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* 用户信息 */}
              <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-xl">
                <div className="p-1 bg-blue-500 rounded-lg">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="text-sm font-medium text-slate-700">{currentUser.split('@')[0]}</span>
              </div>
              {/* 登出按钮 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all text-sm font-medium text-slate-700"
                title="登出"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
              {/* 创建项目按钮 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsCreateModalOpen(true)}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 transition-all text-sm font-medium shadow-md"
              >
                <Plus className="w-4 h-4" />
                创建项目
              </motion.button>
            </div>
          </div>

          {/* 介绍卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative p-5 bg-white/80 backdrop-blur-sm border border-slate-200/50 rounded-2xl shadow-sm overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100/40 to-transparent rounded-full blur-3xl -z-10" />
            <p className="text-sm text-slate-700 leading-relaxed">
              OPC 规范支持中心旨在支撑售前团队快速响应客户需求、梳理业务场景、形成初步技术方案与实施思路，并沉淀标准化、结构化的项目信息。通过提升售前需求理解、方案输出与信息流转效率，为软件定制化团队提供完整、有效的前置信息支撑，促进售前与交付环节的高效衔接。
            </p>
          </motion.div>
        </motion.div>


        {projects.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-20"
          >
            <motion.div
              animate={{
                y: [0, -10, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-slate-100 to-blue-100 rounded-3xl flex items-center justify-center shadow-lg"
            >
              <FolderKanban className="w-12 h-12 text-slate-400" />
            </motion.div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">还没有项目</h3>
            <p className="text-sm text-slate-600 mb-8 max-w-md mx-auto">
              创建您的第一个项目，开始使用 OPC 规范支持中心管理您的售前项目
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsCreateModalOpen(true)}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 transition-all text-sm font-medium inline-flex items-center gap-2 shadow-md"
            >
              <Plus className="w-4 h-4" />
              创建第一个项目
            </motion.button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {projects.map((project, index) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
              >
                <ProjectCard
                  {...project}
                  onEdit={() => setEditingProject(project)}
                  onDelete={() => setDeletingProject(project)}
                  onEnter={() => handleEnterProject(project)}
                  isNew={project.id === newProjectId}
                  isFading={project.id === fadingProjectId}
                />
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <ProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSave={handleCreateProject}
        title="创建新项目"
      />

      <ProjectModal
        isOpen={!!editingProject}
        onClose={() => setEditingProject(null)}
        onSave={handleEditProject}
        initialName={editingProject?.name}
        initialDescription={editingProject?.description}
        initialClientInfo={editingProject?.clientInfo}
        initialProvince={editingProject?.province}
        initialCity={editingProject?.city}
        initialStage={editingProject?.stage}
        initialIndustry={editingProject?.industry}
        title="编辑项目"
      />

      <DeleteConfirmModal
        isOpen={!!deletingProject}
        onClose={() => setDeletingProject(null)}
        onConfirm={handleDeleteProject}
        projectName={deletingProject?.name || ''}
      />
    </div>
  );
}
