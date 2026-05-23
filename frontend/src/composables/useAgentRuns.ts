import { useProjectStore } from '@/stores/project'
import { useRunStore } from '@/stores/run'
import { useMock } from '@/config/env'
import type { PhaseId } from '@/types/run'

const PHASE_RUN_CONFIG: Record<
  PhaseId,
  {
    phase_name: string
    skill_name: string
    input_files: string[]
    expected_outputs: string[]
  }
> = {
  phase1: {
    phase_name: '需求录入与结构化',
    skill_name: 'requirement-intake-structuring',
    input_files: [],
    expected_outputs: ['需求结构化.md'],
  },
  phase2: {
    phase_name: '系统功能设计与页面规划',
    skill_name: 'system-function-design-planning',
    input_files: ['需求结构化.md'],
    expected_outputs: [
      '系统全局功能描述与设计.md',
      '系统的功能点设计.md',
      '页面详细设计/',
      '第二阶段设计检查报告.md',
    ],
  },
  phase3: {
    phase_name: '原型生成',
    skill_name: 'prototype-generator',
    input_files: [
      '系统全局功能描述与设计.md',
      '系统的功能点设计.md',
      '页面详细设计/',
      '第二阶段设计检查报告.md',
    ],
    expected_outputs: [
      'prototype/index.html',
      'prototype/README.md',
      'generation-report.md',
      'validation-report.md',
    ],
  },
}

export function useAgentRuns(projectId: () => string) {
  const projectStore = useProjectStore()
  const runStore = useRunStore()

  const triggerPhaseRun = async (phaseId: PhaseId, prompt?: string) => {
    const config = PHASE_RUN_CONFIG[phaseId]
    const project = projectStore.current
    const run = await runStore.createRun(projectId(), {
      session_id: project?.current_session_id,
      phase_id: phaseId,
      phase_name: config.phase_name,
      skill_name: config.skill_name,
      input_files: config.input_files,
      expected_outputs: config.expected_outputs,
      prompt: prompt ?? null,
    })
    return run
  }

  const pollRun = async (runId: string, sessionId?: string, attempts = useMock ? 2 : 30, intervalMs = useMock ? 500 : 2000) => {
    for (let index = 0; index < attempts; index += 1) {
      const run = await runStore.fetchRun(projectId(), runId, sessionId)
      if (run.status === 'success' || run.status === 'failed') {
        await runStore.fetchRuns(projectId(), sessionId)
        return run
      }
      await new Promise((resolve) => setTimeout(resolve, intervalMs))
    }
    return runStore.current
  }

  return {
    triggerPhaseRun,
    pollRun,
  }
}
