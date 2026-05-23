import { computed, onBeforeUnmount, ref } from 'vue'
import {
  INIT_GENERATION_TASKS,
  PROTOTYPE_FILES,
  PROTOTYPE_QUICK_COMMANDS,
  SOLUTION_FUNCTION_LIST,
  SOLUTION_PPT_SLIDES,
  type GenerationTask,
  type PresentationMode,
  type SolutionViewMode,
  type TaskStatus,
} from '@/constants/solution'

interface ChatMessageItem {
  role: 'assistant' | 'user'
  content: string
}

const cloneTasks = () => INIT_GENERATION_TASKS.map((task) => ({ ...task }))

const createAssistantReply = (message: string): ChatMessageItem => ({ role: 'assistant', content: message })
const createUserReply = (message: string): ChatMessageItem => ({ role: 'user', content: message })

export const useSolutionDesign = () => {
  const viewMode = ref<SolutionViewMode>('overview')
  const presentationMode = ref<PresentationMode>('prototype')
  const tasks = ref<GenerationTask[]>(cloneTasks())
  const taskPanelOpen = ref(false)
  const showAIChat = ref(false)
  const chatMessage = ref('')
  const chatHistory = ref<ChatMessageItem[]>([
    createAssistantReply('您好！我是 AI 智能助手，可以帮您优化文档内容、补充功能点、调整结构等。请问需要什么帮助？'),
  ])

  const prototypeChat = ref('')
  const prototypeChatHistory = ref<ChatMessageItem[]>([
    createAssistantReply('您好！我是原型修改助手，可以帮您调整界面布局、优化交互设计、修改样式配色等。请告诉我您想修改什么？'),
  ])

  const prototypeViewMode = ref<'preview' | 'code'>('preview')
  const activeCodeFile = ref('index.html')
  const copiedFile = ref<string | null>(null)
  const prototypeZoom = ref(100)

  const timerRefs = ref<Record<string, ReturnType<typeof setTimeout>>>({})

  const isGenerating = computed(() => tasks.value.some((task) => task.status === 'running'))
  const runningCount = computed(() => tasks.value.filter((task) => task.status === 'running').length)
  const doneCount = computed(() => tasks.value.filter((task) => task.status === 'done').length)

  const updateTask = (id: string, patch: Partial<GenerationTask>) => {
    tasks.value = tasks.value.map((task) => (task.id === id ? { ...task, ...patch } : task))
  }

  const runTask = (id: string, durationMs: number, onDone?: () => void) => {
    const startedAt = Date.now()
    updateTask(id, { status: 'running', startedAt })
    timerRefs.value[id] = setTimeout(() => {
      const elapsed = Date.now() - startedAt
      updateTask(id, { status: 'done', finishedAt: Date.now(), durationMs: elapsed })
      onDone?.()
    }, durationMs)
  }

  const resetTasks = () => {
    Object.values(timerRefs.value).forEach(clearTimeout)
    timerRefs.value = {}
    tasks.value = cloneTasks()
  }

  const startGeneration = () => {
    resetTasks()
    taskPanelOpen.value = true
    runTask('prd', 4000, () => {
      runTask('functions', 5000, () => {
        runTask('prototype', 7000)
      })
    })
  }

  const regenerateTask = (id: string) => {
    updateTask(id, { status: 'pending', finishedAt: undefined, durationMs: undefined })
    setTimeout(() => runTask(id, 3000 + Math.random() * 2000), 100)
  }

  const sendChatMessage = () => {
    if (!chatMessage.value.trim()) return
    chatHistory.value.push(createUserReply(chatMessage.value))
    chatMessage.value = ''
    setTimeout(() => {
      chatHistory.value.push(
        createAssistantReply('我已经理解您的需求。我可以帮您优化文档结构、补充技术细节、完善功能描述等。您可以告诉我具体想修改哪个部分。'),
      )
    }, 800)
  }

  const sendPrototypeChat = () => {
    if (!prototypeChat.value.trim()) return
    prototypeChatHistory.value.push(createUserReply(prototypeChat.value))
    prototypeChat.value = ''
    setTimeout(() => {
      prototypeChatHistory.value.push(
        createAssistantReply('好的，我已经理解您的需求。我可以帮您修改界面布局、调整配色方案、优化交互细节等。具体想怎么调整呢？'),
      )
    }, 800)
  }

  const applyQuickCommand = (msg: string, reply: string) => {
    prototypeChatHistory.value.push(createUserReply(msg))
    setTimeout(() => {
      prototypeChatHistory.value.push(createAssistantReply(`好的，${reply}`))
    }, 800)
  }

  const copyCodeFile = async (fileName: string) => {
    const content = PROTOTYPE_FILES[fileName]?.content ?? ''
    await navigator.clipboard.writeText(content)
    copiedFile.value = fileName
    setTimeout(() => {
      copiedFile.value = null
    }, 2000)
  }

  const getTaskDuration = (taskId: string) => {
    if (taskId === 'prototype') return 6500
    if (taskId === 'functions') return 4500
    return 3500
  }

  const isTaskLocked = (index: number) => index > 0 && tasks.value[index - 1]?.status !== 'done'

  const getTaskStatusLabel = (status: TaskStatus) => {
    if (status === 'running') return '生成中'
    if (status === 'done') return '完成'
    if (status === 'error') return '失败'
    return '等待中'
  }

  onBeforeUnmount(() => {
    Object.values(timerRefs.value).forEach(clearTimeout)
  })

  return {
    viewMode,
    presentationMode,
    tasks,
    taskPanelOpen,
    showAIChat,
    chatMessage,
    chatHistory,
    prototypeChat,
    prototypeChatHistory,
    prototypeViewMode,
    activeCodeFile,
    copiedFile,
    prototypeZoom,
    isGenerating,
    runningCount,
    doneCount,
    pptSlides: SOLUTION_PPT_SLIDES,
    functionList: SOLUTION_FUNCTION_LIST,
    prototypeFiles: PROTOTYPE_FILES,
    quickCommands: PROTOTYPE_QUICK_COMMANDS,
    startGeneration,
    regenerateTask,
    sendChatMessage,
    sendPrototypeChat,
    applyQuickCommand,
    copyCodeFile,
    getTaskDuration,
    isTaskLocked,
    getTaskStatusLabel,
  }
}

export type { SolutionViewMode, PresentationMode, GenerationTask, TaskStatus }
