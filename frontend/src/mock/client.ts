import { DEFAULT_REQUIREMENT_ANALYSIS } from '@/constants/project'
import { createMockProjects, createMockRuns, createMockSessions, createMockWorkflow, MOCK_SESSION_ID } from '@/mock/data'
import { normalizeRequirementAnalysis } from '@/utils/requirement'
import type {
  CreateProjectRequest,
  Project,
  RunPhase1Request,
  RunPhase1Response,
  UpdateProjectOverviewRequest,
  UpdateProjectRequest,
  UpdateRequirementAnalysisRequest,
} from '@/types/project'
import type { CreateRunRequest, LogsResponse, ProjectRun } from '@/types/run'
import type { ProjectSession } from '@/types/session'
import type { CreateWorkflowRequest, WorkflowRun } from '@/types/workflow'

const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms))

const nextId = (prefix: string) => `${prefix}_${Math.random().toString(16).slice(2, 10)}`

class MockState {
  projects: Project[] = createMockProjects()

  runs = new Map<string, ProjectRun[]>()

  sessions = new Map<string, ProjectSession[]>()

  workflows = new Map<string, WorkflowRun>()

  constructor() {
    for (const project of this.projects) {
      this.runs.set(project.project_id, createMockRuns(project.project_id))
      this.sessions.set(project.project_id, createMockSessions(project.project_id))
    }
  }

  getProject(projectId: string) {
    const project = this.projects.find((item) => item.project_id === projectId)
    if (!project) throw new Error('项目不存在')
    return structuredClone(project)
  }

  saveProject(project: Project) {
    const index = this.projects.findIndex((item) => item.project_id === project.project_id)
    project.updated_at = new Date().toISOString()
    if (index >= 0) this.projects[index] = structuredClone(project)
    else this.projects.unshift(structuredClone(project))
    return this.getProject(project.project_id)
  }
}

export const mockState = new MockState()

const wrap = async <T>(value: T, ms = 300) => {
  await delay(ms)
  return { data: structuredClone(value) }
}

export const mockApi = {
  async listProjects() {
    return wrap(mockState.projects.map((item) => structuredClone(item)))
  },

  async getProject(projectId: string) {
    return wrap(mockState.getProject(projectId))
  },

  async createProject(payload: CreateProjectRequest) {
    const project: Project = {
      project_id: nextId('proj'),
      created_id: 'mock-user',
      update_id: 'mock-user',
      name: payload.name,
      description: payload.description ?? null,
      status: 'created',
      workspace_path: `/mock/projects/${nextId('proj')}`,
      current_session_id: MOCK_SESSION_ID,
      config: payload.config ?? {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    mockState.projects.unshift(project)
    mockState.runs.set(project.project_id, createMockRuns(project.project_id))
    mockState.sessions.set(project.project_id, createMockSessions(project.project_id))
    return wrap(project)
  },

  async updateProject(projectId: string, payload: UpdateProjectRequest) {
    const project = mockState.getProject(projectId)
    return wrap(
      mockState.saveProject({
        ...project,
        name: payload.name,
        description: payload.description ?? null,
        config: payload.config ?? project.config,
      }),
    )
  },

  async updateOverview(projectId: string, payload: UpdateProjectOverviewRequest) {
    const project = mockState.getProject(projectId)
    return wrap(
      mockState.saveProject({
        ...project,
        name: payload.name ?? project.name,
        description: payload.description ?? project.description,
        config: {
          ...project.config,
          clientInfo: payload.clientInfo ?? project.config.clientInfo,
          province: payload.province ?? project.config.province,
          city: payload.city ?? project.config.city,
          stage: payload.stage ?? project.config.stage,
          industry: payload.industry ?? project.config.industry,
        },
      }),
    )
  },

  async updateRequirementAnalysis(projectId: string, payload: UpdateRequirementAnalysisRequest) {
    const project = mockState.getProject(projectId)
    const current = normalizeRequirementAnalysis(project.config)
    return wrap(
      mockState.saveProject({
        ...project,
        config: {
          ...project.config,
          requirementAnalysis: normalizeRequirementAnalysis({
            ...project.config,
            requirementAnalysis: {
              ...current,
              ...payload,
              basic: { ...current.basic, ...payload.basic },
              core: { ...current.core, ...payload.core },
              scenarios: payload.scenarios ?? current.scenarios,
              functions: payload.functions ? { ...current.functions, ...payload.functions } : current.functions,
              risks: payload.risks ?? current.risks,
              pending: { ...current.pending, ...payload.pending, items: payload.pending?.items ?? current.pending.items },
              attachments: payload.attachments ?? current.attachments,
              supplement: { ...current.supplement, ...payload.supplement },
            },
          }),
        },
      }),
    )
  },

  async runPhase1(projectId: string, payload: RunPhase1Request) {
    const project = mockState.getProject(projectId)
    const runId = nextId('run')
    const run: ProjectRun = {
      run_id: runId,
      project_id: projectId,
      session_id: payload.session_id ?? MOCK_SESSION_ID,
      phase_id: 'phase1',
      phase_name: '需求录入与结构化',
      skill_name: 'requirement-intake-structuring',
      input_files: [],
      expected_outputs: ['需求结构化.md'],
      status: 'success',
      started_at: new Date().toISOString(),
      ended_at: new Date().toISOString(),
      error_message: null,
      result_summary: { content_preview: 'Mock 需求结构化完成' },
      log_path: `/mock/logs/${runId}.log`,
    }
    mockState.runs.set(projectId, [run, ...(mockState.runs.get(projectId) ?? [])])
    const response: RunPhase1Response = {
      project: mockState.saveProject({ ...project, status: 'success' }),
      run_id: runId,
      session_id: run.session_id,
      status: 'success',
      result_summary: run.result_summary,
    }
    return wrap(response, 800)
  },

  async deleteProject(projectId: string) {
    mockState.projects = mockState.projects.filter((item) => item.project_id !== projectId)
    mockState.runs.delete(projectId)
    mockState.sessions.delete(projectId)
    await delay(300)
  },

  async listSessions(projectId: string) {
    return wrap(mockState.sessions.get(projectId) ?? createMockSessions(projectId))
  },

  async createSession(projectId: string) {
    const session = createMockSessions(projectId)[0]
    mockState.sessions.set(projectId, [session])
    return wrap(session)
  },

  async resumeSession(projectId: string, sessionId: string) {
    const sessions = mockState.sessions.get(projectId) ?? createMockSessions(projectId)
    const session = sessions.find((item) => item.session_id === sessionId) ?? sessions[0]
    return wrap(session)
  },

  async listRuns(projectId: string) {
    return wrap(mockState.runs.get(projectId) ?? createMockRuns(projectId))
  },

  async createRun(projectId: string, payload: CreateRunRequest) {
    const run: ProjectRun = {
      run_id: nextId('run'),
      project_id: projectId,
      session_id: payload.session_id ?? MOCK_SESSION_ID,
      phase_id: payload.phase_id,
      phase_name: payload.phase_name,
      skill_name: payload.skill_name,
      input_files: payload.input_files ?? [],
      expected_outputs: payload.expected_outputs ?? [],
      status: 'running',
      started_at: new Date().toISOString(),
      ended_at: null,
      error_message: null,
      result_summary: null,
      log_path: '/mock/logs/latest.log',
    }
    mockState.runs.set(projectId, [run, ...(mockState.runs.get(projectId) ?? [])])
    return wrap(run, 500)
  },

  async getRun(projectId: string, runId: string) {
    const runs = mockState.runs.get(projectId) ?? []
    const run = runs.find((item) => item.run_id === runId)
    if (!run) throw new Error('运行记录不存在')
    if (run.status === 'running') {
      run.status = 'success'
      run.ended_at = new Date().toISOString()
      run.result_summary = { content_preview: 'Mock 任务完成' }
    }
    return wrap(run, 400)
  },

  async getRunLogs(_projectId: string, runId: string) {
    const response: LogsResponse = {
      content: `[mock] ${runId} 执行日志\n- 读取输入文件\n- 调用 AI 技能\n- 写入输出文件\n- 完成`,
    }
    return wrap(response)
  },

  async createWorkflow(projectId: string, _payload: CreateWorkflowRequest) {
    const workflow = createMockWorkflow(projectId)
    mockState.workflows.set(projectId, workflow)
    return wrap(workflow, 600)
  },

  async getWorkflow(projectId: string, workflowId: string) {
    const workflow = mockState.workflows.get(projectId) ?? createMockWorkflow(projectId)
    if (workflow.workflow_id !== workflowId) {
      return wrap({ ...workflow, workflow_id: workflowId })
    }
    return wrap(workflow)
  },
}
