<template>
  <ProjectLayout>
    <div class="solution-page">
      <!-- 悬浮任务面板 -->
      <div class="solution-page__task-fab">
        <Transition name="task-panel">
          <div v-if="taskPanelOpen" class="task-panel">
            <div class="task-panel__head">
              <div class="task-panel__head-left">
                <span class="task-panel__head-icon">☰</span>
                <span class="task-panel__head-title">生成任务</span>
                <span v-if="runningCount > 0" class="task-panel__head-badge">{{ runningCount }} 进行中</span>
              </div>
              <button type="button" class="task-panel__close" @click="taskPanelOpen = false">⌄</button>
            </div>
            <div class="task-panel__list">
              <div v-for="task in tasks" :key="task.id" class="task-panel__item">
                <span class="task-panel__item-icon">{{ task.icon }}</span>
                <div class="task-panel__item-body">
                  <div class="task-panel__item-row">
                    <span class="task-panel__item-name">{{ task.name }}</span>
                    <span class="task-panel__status" :class="`task-panel__status--${task.status}`">
                      {{ getTaskStatusLabel(task.status) }}
                    </span>
                  </div>
                  <p class="task-panel__item-desc">{{ task.description }}</p>
                  <div v-if="task.status === 'running'" class="task-panel__progress">
                    <div class="task-panel__progress-bar" :style="{ animationDuration: `${getTaskDuration(task.id)}ms` }"></div>
                  </div>
                  <p v-if="task.status === 'done' && task.durationMs" class="task-panel__duration">
                    耗时 {{ (task.durationMs / 1000).toFixed(1) }}s
                  </p>
                </div>
                <button v-if="task.status === 'done'" type="button" class="task-panel__retry" @click="regenerateTask(task.id)">重试</button>
              </div>
            </div>
            <div class="task-panel__footer">
              <div class="task-panel__footer-row">
                <span>总进度</span>
                <span>{{ doneCount }} / {{ tasks.length }} 已完成</span>
              </div>
              <div class="task-panel__footer-bar">
                <div class="task-panel__footer-fill" :style="{ width: `${(doneCount / tasks.length) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </Transition>

        <button type="button" class="task-panel__trigger" @click="taskPanelOpen = !taskPanelOpen">
          <span v-if="isGenerating" class="task-panel__trigger-spinner"></span>
          <span v-else>☰</span>
          任务
          <span v-if="runningCount > 0" class="task-panel__trigger-count task-panel__trigger-count--running">{{ runningCount }}</span>
          <span v-else-if="doneCount > 0" class="task-panel__trigger-count task-panel__trigger-count--done">{{ doneCount }}</span>
        </button>
      </div>

      <!-- 总览 -->
      <section v-if="viewMode === 'overview'" class="solution-page__section">
        <div class="solution-page__container">
          <div class="solution-page__header">
            <div>
              <h1 class="solution-page__title">方案设计</h1>
              <p class="solution-page__subtitle">AI 智能生成 PRD 文档和功能清单，支持原型预览和 PPT 演示两种呈现方式</p>
            </div>
            <button
              v-if="doneCount === 0 && !isGenerating"
              type="button"
              class="solution-page__generate"
              :disabled="generating"
              @click="handleGenerateSolution"
            >
              ✦ AI 生成方案
            </button>
            <button v-else-if="isGenerating" type="button" class="solution-page__generating" @click="taskPanelOpen = true">
              <span class="task-panel__trigger-spinner"></span>
              {{ runningCount }} 个任务进行中 · 点击查看
            </button>
          </div>

          <div class="solution-page__progress-head">
            <h2 class="solution-page__section-title">生成进度</h2>
            <button v-if="doneCount > 0" type="button" class="solution-page__progress-link" @click="taskPanelOpen = true">☰ 任务详情</button>
          </div>

          <div class="solution-page__task-grid">
            <article
              v-for="(task, index) in tasks"
              :key="task.id"
              class="task-card"
              :class="{
                'task-card--running': task.status === 'running',
                'task-card--done': task.status === 'done',
                'task-card--locked': isTaskLocked(index),
                [`task-card--${index}`]: true,
              }"
            >
              <div class="task-card__head">
                <div class="task-card__head-left">
                  <div class="task-card__icon" :class="{ 'task-card__icon--active': task.status === 'running' || task.status === 'done' }">
                    <span v-if="task.status === 'running'" class="task-panel__trigger-spinner task-panel__trigger-spinner--white"></span>
                    <span v-else>{{ task.icon }}</span>
                  </div>
                  <h3 class="task-card__name">{{ task.name }}</h3>
                </div>
                <span v-if="task.status === 'done'" class="task-card__check">✓</span>
                <span v-else-if="task.status === 'pending' && !isTaskLocked(index)" class="task-card__clock">◷</span>
              </div>
              <p class="task-card__desc">{{ task.description }}</p>

              <div v-if="task.status === 'running'" class="task-card__progress">
                <div class="task-card__progress-bar" :style="{ animationDuration: `${getTaskDuration(task.id)}ms` }"></div>
              </div>

              <div v-if="task.status === 'running'" class="task-card__status-bar">生成中，可切换到其他页面...</div>
              <div v-else-if="task.status === 'done'" class="task-card__actions">
                <button type="button" class="task-card__view" @click="viewMode = taskStepColors[index].viewMode">查看结果</button>
                <button type="button" class="task-card__regen" :disabled="isGenerating" @click="regenerateTask(task.id)">重新生成</button>
              </div>
              <div v-else-if="isTaskLocked(index)" class="task-card__waiting">等待上一步完成</div>
              <div v-else class="task-card__waiting">点击"AI 生成方案"开始</div>
            </article>
          </div>

          <div class="solution-page__guide">
            <span class="solution-page__guide-icon">✦</span>
            <div>
              <p class="solution-page__guide-title">使用说明</p>
              <p class="solution-page__guide-text">点击右上角"AI 生成方案"按钮，系统将自动完成以下步骤：</p>
              <ul class="solution-page__guide-list">
                <li><strong>步骤1：</strong>生成 PRD 产品需求文档（包含执行摘要、核心目标、功能模块）</li>
                <li><strong>步骤2：</strong>基于 PRD 生成详细的功能清单（包含模块、字段、约束条件）</li>
                <li><strong>步骤3：</strong>选择原型预览或 PPT 演示两种方式呈现方案</li>
              </ul>
              <p class="solution-page__guide-foot">生成后可随时查看详情、编辑内容或重新生成</p>
            </div>
          </div>
        </div>
      </section>

      <!-- PRD -->
      <section v-else-if="viewMode === 'prd'" class="solution-page__section">
        <div class="solution-page__container solution-page__container--narrow">
          <button type="button" class="solution-page__back" @click="viewMode = 'overview'">← 返回总览</button>

          <article class="content-card">
            <div class="content-card__head">
              <h2>PRD 产品需求文档</h2>
              <div class="content-card__actions">
                <button type="button" class="content-card__primary" @click="showAIChat = !showAIChat">AI 助手</button>
                <button type="button" class="content-card__ghost">↓ 导出</button>
              </div>
            </div>

            <div class="prd-content">
              <h3>一、执行摘要</h3>
              <p>本产品旨在通过智能化客服系统，解决传统人工客服成本高、响应慢、服务质量不稳定等问题。系统基于大语言模型技术，支持自然语言理解、多轮对话、知识库管理等核心功能。</p>
              <h3>二、核心目标</h3>
              <ul>
                <li>降低人工客服成本 35% 以上</li>
                <li>提升客户问题首次解决率至 85%</li>
                <li>实现 24/7 全天候智能服务</li>
                <li>提升用户满意度 NPS 15 个点</li>
              </ul>
              <h3>三、功能模块</h3>
              <p><strong>3.1 智能对话引擎</strong></p>
              <p>基于 Transformer 架构的自然语言处理引擎，支持意图识别、实体提取、多轮对话管理等功能。</p>
              <p><strong>3.2 知识库管理</strong></p>
              <p>支持结构化和非结构化知识的存储、检索和更新，提供可视化的知识图谱展示。</p>
              <p><strong>3.3 多端同步</strong></p>
              <p>支持 Web、移动端、微信小程序等多终端访问，数据实时同步。</p>
            </div>
          </article>
        </div>

        <div v-if="showAIChat" class="ai-chat">
          <div class="ai-chat__head">
            <span>AI 智能助手</span>
            <button type="button" @click="showAIChat = false">×</button>
          </div>
          <div class="ai-chat__body">
            <div v-for="(item, index) in chatHistory" :key="index" class="ai-chat__message" :class="`ai-chat__message--${item.role}`">
              {{ item.content }}
            </div>
          </div>
          <div class="ai-chat__input">
            <input v-model="chatMessage" type="text" placeholder="输入您的问题..." @keydown.enter="sendChatMessage" />
            <button type="button" @click="sendChatMessage">发送</button>
          </div>
        </div>
      </section>

      <!-- 功能清单 -->
      <section v-else-if="viewMode === 'functions'" class="solution-page__section">
        <div class="solution-page__container">
          <button type="button" class="solution-page__back" @click="viewMode = 'overview'">← 返回总览</button>

          <article class="content-card">
            <div class="content-card__head">
              <h2>功能清单</h2>
              <button type="button" class="content-card__ghost">↓ 导出</button>
            </div>

            <div class="table-wrap">
              <table class="function-table">
                <thead>
                  <tr>
                    <th>功能模块</th>
                    <th>一级功能</th>
                    <th>二级功能</th>
                    <th>功能点</th>
                    <th>功能描述</th>
                    <th>字段定义</th>
                    <th>交互流程</th>
                    <th>约束条件</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in functionList" :key="index">
                    <td>{{ item.module }}</td>
                    <td>{{ item.level1 }}</td>
                    <td>{{ item.level2 }}</td>
                    <td>{{ item.point }}</td>
                    <td>{{ item.description }}</td>
                    <td class="function-table__mono">{{ item.fields }}</td>
                    <td class="function-table__small">{{ item.interaction }}</td>
                    <td class="function-table__small">{{ item.constraints }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </div>
      </section>

      <!-- 方案呈现 -->
      <section v-else-if="viewMode === 'presentation'" class="solution-page__section">
        <div v-if="presentationMode === 'ppt'" class="solution-page__container">
          <button type="button" class="solution-page__back" @click="viewMode = 'overview'">← 返回总览</button>

          <div class="presentation-head">
            <div>
              <h2 class="solution-page__section-title">方案呈现</h2>
              <p class="solution-page__subtitle">选择您希望的呈现方式</p>
            </div>
          </div>

          <div class="presentation-tabs">
            <button type="button" class="presentation-tabs__item" @click="presentationMode = 'prototype'">👁 原型预览</button>
            <button type="button" class="presentation-tabs__item presentation-tabs__item--active">🖥 PPT 演示</button>
          </div>

          <article class="content-card">
            <div class="content-card__head">
              <h2>PPT 演示大纲</h2>
              <button type="button" class="content-card__ghost">↓ 导出 PPT</button>
            </div>
            <div class="ppt-list">
              <article v-for="(slide, index) in pptSlides" :key="slide.id" class="ppt-card">
                <div class="ppt-card__head">
                  <span class="ppt-card__index">{{ index + 1 }}</span>
                  <h3>{{ slide.title }}</h3>
                </div>
                <ul>
                  <li v-for="point in slide.points" :key="point">{{ point }}</li>
                </ul>
              </article>
            </div>
          </article>
        </div>

        <!-- 原型工作室 -->
        <div v-else class="prototype-studio">
          <aside class="prototype-studio__chat">
            <div class="prototype-studio__chat-head">
              <span>AI 修改助手</span>
              <p>通过对话实时调整原型设计</p>
            </div>
            <div class="prototype-studio__chat-body">
              <div
                v-for="(item, index) in prototypeChatHistory"
                :key="index"
                class="ai-chat__message"
                :class="`ai-chat__message--${item.role} ai-chat__message--dark-${item.role}`"
              >
                {{ item.content }}
              </div>
            </div>
            <div class="prototype-studio__chat-foot">
              <p class="prototype-studio__quick-label">快捷指令</p>
              <div class="prototype-studio__quick-list">
                <button
                  v-for="cmd in quickCommands"
                  :key="cmd.label"
                  type="button"
                  @click="applyQuickCommand(cmd.msg, cmd.reply)"
                >
                  {{ cmd.label }}
                </button>
              </div>
              <div class="ai-chat__input ai-chat__input--dark">
                <input v-model="prototypeChat" type="text" placeholder="描述您的修改需求..." @keydown.enter="sendPrototypeChat" />
                <button type="button" @click="sendPrototypeChat">发送</button>
              </div>
            </div>
          </aside>

          <section class="prototype-studio__main">
            <div class="prototype-studio__toolbar">
              <div class="prototype-studio__toolbar-left">
                <button type="button" class="prototype-studio__back" @click="viewMode = 'overview'">←</button>
                <span class="prototype-studio__divider"></span>
                <span class="prototype-studio__title">智能客服助手</span>
              </div>
              <div class="prototype-studio__toolbar-right">
                <div class="prototype-studio__mode-tabs">
                  <button
                    type="button"
                    :class="{ 'prototype-studio__mode-tabs--active': prototypeViewMode === 'preview' }"
                    @click="prototypeViewMode = 'preview'"
                  >
                    预览
                  </button>
                  <button
                    type="button"
                    :class="{ 'prototype-studio__mode-tabs--active': prototypeViewMode === 'code' }"
                    @click="prototypeViewMode = 'code'"
                  >
                    源码
                  </button>
                </div>
                <span class="prototype-studio__divider"></span>
                <div v-if="prototypeViewMode === 'preview'" class="prototype-studio__zoom">
                  <button type="button" @click="prototypeZoom = Math.max(50, prototypeZoom - 10)">−</button>
                  <span>{{ prototypeZoom }}%</span>
                  <button type="button" @click="prototypeZoom = Math.min(200, prototypeZoom + 10)">+</button>
                </div>
                <span v-if="prototypeViewMode === 'preview'" class="prototype-studio__divider"></span>
                <button type="button" class="prototype-studio__ghost-btn">部署</button>
                <button type="button" class="prototype-studio__ghost-btn">导出</button>
              </div>
            </div>

            <div v-if="prototypeViewMode === 'preview'" class="prototype-studio__canvas">
              <div class="prototype-studio__preview-wrap">
                <div class="prototype-studio__preview" :style="{ transform: `scale(${prototypeZoom / 100})` }">
                  <div class="prototype-studio__mock-header">
                    <h2>智能客服助手</h2>
                    <p>● 在线服务中</p>
                  </div>
                  <div class="prototype-studio__mock-body">
                    <div class="prototype-studio__mock-row">
                      <div class="prototype-studio__avatar prototype-studio__avatar--bot"></div>
                      <div class="prototype-studio__bubble prototype-studio__bubble--bot">您好！我是智能客服助手，有什么可以帮到您的吗？</div>
                    </div>
                    <div class="prototype-studio__mock-row prototype-studio__mock-row--reverse">
                      <div class="prototype-studio__avatar prototype-studio__avatar--user"></div>
                      <div class="prototype-studio__bubble prototype-studio__bubble--user">我想了解产品的功能特性</div>
                    </div>
                    <div class="prototype-studio__mock-row">
                      <div class="prototype-studio__avatar prototype-studio__avatar--bot"></div>
                      <div class="prototype-studio__bubble prototype-studio__bubble--bot">
                        当然！我们的产品具有以下核心功能：<br />1. 智能对话理解<br />2. 多轮对话支持<br />3. 知识库管理<br />4. 多终端同步
                      </div>
                    </div>
                    <div class="prototype-studio__mock-input">
                      <input type="text" placeholder="输入您的问题..." readonly />
                      <button type="button">发送</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="prototype-studio__code-layout">
              <aside class="prototype-studio__file-tree">
                <div class="prototype-studio__file-tree-head">项目文件</div>
                <button
                  v-for="fileName in Object.keys(prototypeFiles)"
                  :key="fileName"
                  type="button"
                  class="prototype-studio__file-item"
                  :class="{ 'prototype-studio__file-item--active': activeCodeFile === fileName }"
                  @click="activeCodeFile = fileName"
                >
                  {{ fileName }}
                </button>
              </aside>
              <div class="prototype-studio__code-main">
                <div class="prototype-studio__code-tabs">
                  <button
                    v-for="fileName in Object.keys(prototypeFiles)"
                    :key="fileName"
                    type="button"
                    class="prototype-studio__code-tab"
                    :class="{ 'prototype-studio__code-tab--active': activeCodeFile === fileName }"
                    @click="activeCodeFile = fileName"
                  >
                    {{ fileName }}
                  </button>
                  <button type="button" class="prototype-studio__copy-btn" @click="copyCodeFile(activeCodeFile)">
                    {{ copiedFile === activeCodeFile ? '已复制' : '复制' }}
                  </button>
                </div>
                <div class="prototype-studio__code-body">
                  <div class="prototype-studio__line-numbers">
                    <div v-for="(_, lineIndex) in activeCodeLines" :key="lineIndex">{{ lineIndex + 1 }}</div>
                  </div>
                  <pre class="prototype-studio__code-content"><code>{{ activeCodeContent }}</code></pre>
                </div>
                <div class="prototype-studio__code-status">
                  <span>{{ activeCodeLanguage.toUpperCase() }}</span>
                  <span>{{ activeCodeLines.length }} 行 · UTF-8</span>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- PPT 模式切换入口（原型模式下可切到 PPT） -->
        <div v-if="presentationMode === 'prototype'" class="prototype-studio__mode-switch">
          <button type="button" @click="presentationMode = 'ppt'">切换到 PPT 演示</button>
        </div>
      </section>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { TASK_STEP_COLORS } from '@/constants/solution'
import { useSolutionDesign } from '@/composables/useSolutionDesign'
import { useAgentRuns } from '@/composables/useAgentRuns'
import { useProjectStore } from '@/stores/project'
import { useMock } from '@/config/env'
import ProjectLayout from '@/layouts/ProjectLayout.vue'

const route = useRoute()
const projectStore = useProjectStore()
const { triggerPhaseRun, pollRun } = useAgentRuns(() => String(route.params.projectId))
const generating = ref(false)

const {
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
  pptSlides,
  functionList,
  prototypeFiles,
  quickCommands,
  startGeneration,
  regenerateTask,
  sendChatMessage,
  sendPrototypeChat,
  applyQuickCommand,
  copyCodeFile,
  getTaskDuration,
  isTaskLocked,
  getTaskStatusLabel,
} = useSolutionDesign()

const taskStepColors = TASK_STEP_COLORS

const activeCodeContent = computed(() => prototypeFiles[activeCodeFile.value]?.content ?? '')
const activeCodeLanguage = computed(() => prototypeFiles[activeCodeFile.value]?.language ?? 'text')
const activeCodeLines = computed(() => activeCodeContent.value.split('\n'))

const handleGenerateSolution = async () => {
  generating.value = true
  startGeneration()

  if (useMock) {
    generating.value = false
    ElMessage.success('已启动方案生成任务')
    return
  }

  try {
    const phase2Run = await triggerPhaseRun('phase2')
    const phase2Result = await pollRun(phase2Run.run_id, phase2Run.session_id)
    if (phase2Result?.status === 'failed') {
      throw new Error(phase2Result.error_message ?? '第二阶段执行失败')
    }
    const phase3Run = await triggerPhaseRun('phase3')
    await pollRun(phase3Run.run_id, phase3Run.session_id)
    await projectStore.fetchProject(String(route.params.projectId))
    ElMessage.success('方案设计生成任务已完成')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '方案生成失败')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.solution-page {
  position: relative;
  min-height: 100%;
  background: #f8fafc;
}

.solution-page__section {
  min-height: 100%;
  overflow-y: auto;
}

.solution-page__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

.solution-page__container--narrow {
  max-width: 960px;
}

.solution-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 32px;
}

.solution-page__title {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 24px;
  font-weight: 700;
}

.solution-page__subtitle,
.solution-page__guide-text,
.solution-page__guide-list,
.solution-page__guide-foot,
.task-card__desc,
.prd-content p,
.prd-content li {
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.solution-page__subtitle {
  margin: 0;
}

.solution-page__generate,
.task-panel__trigger,
.content-card__primary,
.ai-chat__input button,
.task-card__view,
.prototype-studio__mock-input button {
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

.solution-page__generate {
  padding: 16px 32px;
  font-size: 16px;
  white-space: nowrap;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
}

.solution-page__generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.solution-page__generating {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border: 1px solid #c7d2fe;
  border-radius: 12px;
  background: #eef2ff;
  color: #4338ca;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.solution-page__progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.solution-page__section-title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.solution-page__progress-link {
  border: none;
  background: transparent;
  color: #4f46e5;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
}

.solution-page__task-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.task-card {
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.task-card--running.task-card--0 { border-color: #60a5fa; background: #eff6ff; }
.task-card--running.task-card--1 { border-color: #4ade80; background: #f0fdf4; }
.task-card--running.task-card--2 { border-color: #c084fc; background: #faf5ff; }
.task-card--done.task-card--0 { border-color: #bfdbfe; }
.task-card--done.task-card--1 { border-color: #bbf7d0; }
.task-card--done.task-card--2 { border-color: #e9d5ff; }
.task-card--locked { opacity: 0.6; }

.task-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.task-card__head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-card__icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #94a3b8;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.task-card--0 .task-card__icon--active { background: #2563eb; }
.task-card--1 .task-card__icon--active { background: #16a34a; }
.task-card--2 .task-card__icon--active { background: #9333ea; }

.task-card__name {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 700;
}

.task-card__check { color: #22c55e; font-size: 18px; }
.task-card__clock { color: #94a3b8; font-size: 18px; }

.task-card__desc { margin: 0 0 16px; }

.task-card__progress,
.task-panel__progress {
  height: 6px;
  margin-bottom: 12px;
  border-radius: 999px;
  background: #f1f5f9;
  overflow: hidden;
}

.task-card__progress-bar,
.task-panel__progress-bar {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  animation: progress-fill linear forwards;
  width: 88%;
}

@keyframes progress-fill {
  from { width: 3%; }
  to { width: 88%; }
}

.task-card__status-bar,
.task-card__waiting {
  padding: 8px 16px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.task-card__actions {
  display: flex;
  gap: 8px;
}

.task-card__view,
.task-card__regen {
  flex: 1;
  min-height: 38px;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.task-card--0 .task-card__view { background: #2563eb; color: #fff; border: none; }
.task-card--1 .task-card__view { background: #16a34a; color: #fff; border: none; }
.task-card--2 .task-card__view { background: #9333ea; color: #fff; border: none; }

.task-card__regen {
  border: 1px solid currentColor;
  background: #fff;
}

.task-card--0 .task-card__regen { color: #2563eb; }
.task-card--1 .task-card__regen { color: #16a34a; }
.task-card--2 .task-card__regen { color: #9333ea; }

.task-card__regen:disabled { opacity: 0.5; cursor: not-allowed; }

.solution-page__guide {
  display: flex;
  gap: 12px;
  padding: 20px;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff, #eef2ff);
}

.solution-page__guide-icon {
  color: #4f46e5;
  font-size: 18px;
}

.solution-page__guide-title {
  margin: 0 0 8px;
  color: #312e81;
  font-size: 14px;
  font-weight: 700;
}

.solution-page__guide-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.solution-page__guide-foot {
  margin: 12px 0 0;
  color: #4338ca;
  font-size: 12px;
}

.solution-page__back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #475569;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.solution-page__back:hover {
  background: #fff;
  color: #0f172a;
}

.content-card {
  padding: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.content-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.content-card__head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
  font-weight: 700;
}

.content-card__actions {
  display: flex;
  gap: 8px;
}

.content-card__primary,
.content-card__ghost,
.ai-chat__input button {
  min-height: 38px;
  padding: 0 16px;
  font-size: 14px;
}

.content-card__ghost,
.ai-chat__input button {
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #334155;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

.prd-content h3 {
  margin: 24px 0 12px;
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.prd-content h3:first-child { margin-top: 0; }

.prd-content ul {
  margin: 0;
  padding-left: 20px;
}

.table-wrap {
  overflow-x: auto;
}

.function-table {
  width: 100%;
  min-width: 1100px;
  border-collapse: collapse;
}

.function-table th,
.function-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  vertical-align: top;
  font-size: 14px;
}

.function-table th {
  background: #f8fafc;
  color: #0f172a;
  font-weight: 600;
}

.function-table td { color: #475569; }

.function-table__mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}

.function-table__small { font-size: 12px; }

.presentation-head { margin-bottom: 16px; }

.presentation-tabs {
  display: inline-flex;
  gap: 4px;
  margin-bottom: 24px;
  padding: 4px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.presentation-tabs__item {
  padding: 8px 24px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #334155;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.presentation-tabs__item--active {
  background: #9333ea;
  color: #fff;
}

.ppt-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ppt-card {
  padding: 20px;
  border: 1px solid #e9d5ff;
  border-radius: 12px;
  background: linear-gradient(135deg, #faf5ff, #fff);
}

.ppt-card__head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.ppt-card__index {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #9333ea;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.ppt-card h3 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.ppt-card ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.ppt-card li {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  color: #475569;
  font-size: 14px;
}

.ppt-card li::before {
  content: '•';
  color: #9333ea;
}

/* 任务悬浮 */
.solution-page__task-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.task-panel {
  width: 320px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
  overflow: hidden;
}

.task-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  color: #fff;
}

.task-panel__head-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-panel__head-title {
  font-size: 14px;
  font-weight: 600;
}

.task-panel__head-badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 12px;
}

.task-panel__close {
  border: none;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
}

.task-panel__list {
  border-bottom: 1px solid #f1f5f9;
}

.task-panel__item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.task-panel__item-icon { font-size: 18px; }

.task-panel__item-body { flex: 1; min-width: 0; }

.task-panel__item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-panel__item-name {
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}

.task-panel__item-desc {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}

.task-panel__status {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.task-panel__status--running { background: #eef2ff; color: #4f46e5; }
.task-panel__status--done { background: #f0fdf4; color: #16a34a; }
.task-panel__status--pending { background: #f1f5f9; color: #64748b; }

.task-panel__duration {
  margin: 4px 0 0;
  color: #16a34a;
  font-size: 12px;
}

.task-panel__retry {
  border: none;
  background: transparent;
  color: #4f46e5;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.task-panel__footer {
  padding: 10px 16px;
  background: #f8fafc;
}

.task-panel__footer-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  color: #64748b;
  font-size: 12px;
}

.task-panel__footer-bar {
  height: 6px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.task-panel__footer-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  transition: width 0.5s ease;
}

.task-panel__trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 999px;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);
  font-size: 14px;
}

.task-panel__trigger-count {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

.task-panel__trigger { position: relative; }
.task-panel__trigger-count--running { background: #f97316; }
.task-panel__trigger-count--done { background: #22c55e; }

.task-panel__trigger-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.task-panel__trigger-spinner--white {
  width: 14px;
  height: 14px;
  border-color: rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.task-panel-enter-active,
.task-panel-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.task-panel-enter-from,
.task-panel-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

/* AI 聊天 */
.ai-chat {
  position: fixed;
  right: 24px;
  bottom: 96px;
  width: 384px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
  overflow: hidden;
  z-index: 40;
}

.ai-chat__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(90deg, #4f46e5, #4338ca);
  color: #fff;
  font-weight: 600;
}

.ai-chat__head button {
  border: none;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 18px;
}

.ai-chat__body {
  max-height: 384px;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-chat__message {
  max-width: 85%;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
}

.ai-chat__message--assistant {
  background: #fff;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.ai-chat__message--user {
  align-self: flex-end;
  background: #4f46e5;
  color: #fff;
}

.ai-chat__message--dark-assistant {
  background: #334155;
  color: #f1f5f9;
  border: none;
}

.ai-chat__message--dark-user {
  background: #4f46e5;
  color: #fff;
}

.ai-chat__input {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid #e2e8f0;
}

.ai-chat__input input {
  flex: 1;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 14px;
}

.ai-chat__input--dark {
  background: #1e293b;
  border-top-color: #334155;
}

.ai-chat__input--dark input {
  border-color: #475569;
  background: #334155;
  color: #fff;
}

/* 原型工作室 */
.prototype-studio {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  min-height: calc(100vh - 140px);
  background: #0f172a;
}

.prototype-studio__chat {
  display: flex;
  flex-direction: column;
  border-right: 1px solid #334155;
  background: #1e293b;
}

.prototype-studio__chat-head {
  padding: 16px;
  border-bottom: 1px solid #334155;
  color: #fff;
}

.prototype-studio__chat-head p {
  margin: 8px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.prototype-studio__chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prototype-studio__chat-foot {
  padding: 16px;
  border-top: 1px solid #334155;
}

.prototype-studio__quick-label {
  margin: 0 0 8px;
  color: #94a3b8;
  font-size: 12px;
}

.prototype-studio__quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.prototype-studio__quick-list button {
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  background: #334155;
  color: #e2e8f0;
  cursor: pointer;
  font-size: 12px;
}

.prototype-studio__main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.prototype-studio__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 48px;
  padding: 0 16px;
  border-bottom: 1px solid #334155;
  background: #1e293b;
}

.prototype-studio__toolbar-left,
.prototype-studio__toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prototype-studio__back,
.prototype-studio__ghost-btn {
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}

.prototype-studio__ghost-btn {
  padding: 6px 12px;
  border-radius: 8px;
  background: #334155;
  color: #e2e8f0;
  font-size: 12px;
}

.prototype-studio__divider {
  width: 1px;
  height: 24px;
  background: #334155;
}

.prototype-studio__title {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
}

.prototype-studio__mode-tabs {
  display: inline-flex;
  padding: 2px;
  border-radius: 8px;
  background: #334155;
}

.prototype-studio__mode-tabs button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.prototype-studio__mode-tabs--active {
  background: #475569 !important;
  color: #fff !important;
}

.prototype-studio__zoom {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 8px;
  background: #334155;
}

.prototype-studio__zoom button {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
}

.prototype-studio__zoom span {
  width: 48px;
  color: #cbd5e1;
  font-size: 12px;
  text-align: center;
}

.prototype-studio__canvas {
  flex: 1;
  overflow: auto;
  background: #0f172a;
}

.prototype-studio__preview-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 32px;
}

.prototype-studio__preview {
  width: 900px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  transform-origin: center center;
  transition: transform 0.2s ease;
}

.prototype-studio__mock-header {
  padding: 32px;
  background: linear-gradient(90deg, #4f46e5, #9333ea);
  color: #fff;
}

.prototype-studio__mock-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
}

.prototype-studio__mock-header p {
  margin: 0;
  color: #e0e7ff;
  font-size: 14px;
}

.prototype-studio__mock-body {
  padding: 32px;
  min-height: 500px;
}

.prototype-studio__mock-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.prototype-studio__mock-row--reverse {
  flex-direction: row-reverse;
}

.prototype-studio__avatar {
  width: 48px;
  height: 48px;
  border-radius: 999px;
  flex-shrink: 0;
}

.prototype-studio__avatar--bot { background: #4f46e5; }
.prototype-studio__avatar--user { background: #cbd5e1; }

.prototype-studio__bubble {
  max-width: 360px;
  padding: 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.prototype-studio__bubble--bot {
  background: #f1f5f9;
  color: #0f172a;
}

.prototype-studio__bubble--user {
  background: #4f46e5;
  color: #fff;
}

.prototype-studio__mock-input {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.prototype-studio__mock-input input {
  flex: 1;
  padding: 16px 20px;
  border: 2px solid #cbd5e1;
  border-radius: 12px;
  font-size: 14px;
}

.prototype-studio__mock-input button {
  padding: 16px 32px;
  border-radius: 12px;
}

.prototype-studio__code-layout {
  display: grid;
  grid-template-columns: 192px minmax(0, 1fr);
  flex: 1;
  min-height: 0;
}

.prototype-studio__file-tree {
  border-right: 1px solid #1e293b;
  background: #020617;
}

.prototype-studio__file-tree-head {
  padding: 10px 12px;
  border-bottom: 1px solid #1e293b;
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.prototype-studio__file-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
  text-align: left;
}

.prototype-studio__file-item--active {
  background: #334155;
  color: #fff;
}

.prototype-studio__code-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.prototype-studio__code-tabs {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #1e293b;
  background: #0f172a;
  overflow-x: auto;
}

.prototype-studio__code-tab {
  padding: 10px 16px;
  border: none;
  border-right: 1px solid #1e293b;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.prototype-studio__code-tab--active {
  background: #1e293b;
  color: #fff;
  box-shadow: inset 0 -2px 0 #6366f1;
}

.prototype-studio__copy-btn {
  margin-left: auto;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.prototype-studio__code-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: #020617;
}

.prototype-studio__line-numbers {
  padding: 16px 12px;
  border-right: 1px solid #1e293b;
  color: #475569;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  line-height: 1.5;
  text-align: right;
  user-select: none;
}

.prototype-studio__code-content {
  flex: 1;
  margin: 0;
  padding: 16px;
  color: #cbd5e1;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre;
}

.prototype-studio__code-status {
  display: flex;
  justify-content: space-between;
  padding: 6px 16px;
  background: #4f46e5;
  color: #fff;
  font-size: 12px;
}

.prototype-studio__mode-switch {
  position: fixed;
  left: 50%;
  bottom: 16px;
  transform: translateX(-50%);
  z-index: 30;
}

.prototype-studio__mode-switch button {
  padding: 8px 16px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  cursor: pointer;
  font-size: 12px;
}

@media (max-width: 1024px) {
  .solution-page__task-grid {
    grid-template-columns: 1fr;
  }

  .solution-page__header {
    flex-direction: column;
  }

  .prototype-studio {
    grid-template-columns: 1fr;
  }

  .prototype-studio__code-layout {
    grid-template-columns: 1fr;
  }

  .ai-chat {
    left: 16px;
    right: 16px;
    width: auto;
  }
}
</style>
