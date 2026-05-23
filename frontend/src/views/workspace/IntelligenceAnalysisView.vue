<template>
  <ProjectLayout>
    <div class="intelligence-page">
      <aside class="intelligence-page__sidebar">
        <div class="intelligence-page__sidebar-head">
          <h3 class="intelligence-page__sidebar-title">情报分析</h3>
        </div>

        <div class="intelligence-page__nav">
          <button
            v-for="section in sections"
            :key="section.id"
            type="button"
            class="intelligence-page__nav-item"
            :class="{ 'intelligence-page__nav-item--active': selectedSection === section.id }"
            @click="selectedSection = section.id"
          >
            <span>{{ section.title }}</span>
          </button>
        </div>
      </aside>

      <main class="intelligence-page__main">
        <div class="intelligence-page__container">
          <section v-if="selectedSection === 'overview'" class="panel-card">
            <WorkspacePanelHeader title="情报概览" subtitle="基于项目信息智能检索生成">
              <template #actions>
                <button type="button" class="panel-card__primary" :disabled="analyzing" @click="handleStartAnalysis">
                  {{ analyzing ? '分析中...' : '开始智能分析' }}
                </button>
              </template>
            </WorkspacePanelHeader>

            <div v-if="analysisStarted" class="analysis-result">
              <div class="analysis-result__head">
                <div>
                  <h3 class="analysis-result__title">最新分析结果</h3>
                  <p class="analysis-result__desc">已生成四类情报摘要，可切换到历史案例继续查看参考资料。</p>
                </div>
                <button type="button" class="analysis-result__link" @click="selectedSection = 'history'">查看历史案例</button>
              </div>
              <div class="analysis-result__grid">
                <article v-for="item in analysisResults" :key="item.title" class="analysis-result__item">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.summary }}</p>
                </article>
              </div>
            </div>

            <div class="analysis-intro">
              <div class="analysis-intro__icon">智</div>
              <h3 class="analysis-intro__title">智能情报分析</h3>
              <p class="analysis-intro__desc">点击“开始智能分析”，智能体团队将根据项目信息自动检索：</p>
              <div class="analysis-intro__grid">
                <article class="analysis-intro__item analysis-intro__item--blue">
                  <h4>客户企业信息</h4>
                  <p>企业背景、业务范围</p>
                </article>
                <article class="analysis-intro__item analysis-intro__item--purple">
                  <h4>行业政策分析</h4>
                  <p>政策趋势、监管要求</p>
                </article>
                <article class="analysis-intro__item analysis-intro__item--green">
                  <h4>竞品情报分析</h4>
                  <p>竞品功能、市场定位</p>
                </article>
                <article class="analysis-intro__item analysis-intro__item--orange">
                  <h4>技术趋势洞察</h4>
                  <p>相关技术方案推荐</p>
                </article>
              </div>
            </div>
          </section>

          <section v-else-if="selectedSection === 'history'" class="panel-card">
            <WorkspacePanelHeader
              title="历史参考案例"
              subtitle="查询历史项目资料与原型，为当前项目提供参考"
              :meta="`共 ${filteredProjects.length} 个案例`"
            />

            <div class="history-search">
              <input v-model="searchKeyword" class="history-search__input" type="text" placeholder="搜索项目名称、行业、标签..." @keydown.enter="applySearch" />
              <button type="button" class="history-search__button" @click="applySearch">筛选</button>
            </div>

            <div class="history-list">
              <article v-for="project in filteredProjects" :key="project.id" class="history-card">
                <div class="history-card__content">
                  <div class="history-card__title-row">
                    <h4 class="history-card__title">{{ project.name }}</h4>
                    <span class="history-card__badge">已完成</span>
                  </div>
                  <p class="history-card__desc">{{ project.description }}</p>
                  <div class="history-card__meta-row">
                    <span>{{ project.client }}</span>
                    <span>{{ project.industry }}</span>
                    <span>{{ project.date }}</span>
                  </div>
                  <div class="history-card__tags">
                    <span v-for="tag in project.tags" :key="tag">{{ tag }}</span>
                  </div>
                </div>
                <div class="history-card__actions">
                  <button type="button" class="history-card__action history-card__action--indigo" @click="openDetail('material', project)">查看资料</button>
                  <button type="button" class="history-card__action history-card__action--purple" @click="openDetail('prototype', project)">查看原型</button>
                </div>
              </article>
            </div>

            <div v-if="!filteredProjects.length" class="history-empty">
              未找到匹配案例，请调整搜索关键词。
            </div>
          </section>
        </div>
      </main>

      <div v-if="detailDialogVisible && activeProject" class="detail-modal" @click.self="detailDialogVisible = false">
        <div class="detail-modal__card">
          <WorkspaceModalHeader
            :title="detailMode === 'material' ? '项目资料' : '项目原型'"
            :subtitle="activeProject.name"
            align="start"
            closable
            @close="detailDialogVisible = false"
          />

          <div class="detail-modal__body">
            <template v-if="detailMode === 'material'">
              <div class="detail-modal__section">
                <h4>项目简介</h4>
                <p>{{ activeProject.description }}</p>
              </div>
              <div class="detail-modal__section">
                <h4>客户与行业</h4>
                <p>{{ activeProject.client }} · {{ activeProject.industry }}</p>
              </div>
              <div class="detail-modal__section">
                <h4>参考标签</h4>
                <div class="detail-modal__tags">
                  <span v-for="tag in activeProject.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="detail-modal__prototype">
                <div class="detail-modal__screen"></div>
                <div class="detail-modal__caption">原型摘要：{{ activeProject.name }} 的核心界面布局与交互流程参考。</div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useIntelligenceAnalysis } from '@/composables/useIntelligenceAnalysis'
import { useAgentRuns } from '@/composables/useAgentRuns'
import { useProjectStore } from '@/stores/project'
import { normalizeRequirementAnalysis } from '@/utils/requirement'
import WorkspaceModalHeader from '@/components/workspace/WorkspaceModalHeader.vue'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import WorkspacePanelHeader from '@/components/workspace/WorkspacePanelHeader.vue'

const route = useRoute()
const projectStore = useProjectStore()
const { triggerPhaseRun, pollRun } = useAgentRuns(() => String(route.params.projectId))
const analyzing = ref(false)

const {
  activeProject,
  analysisResults,
  analysisStarted,
  detailDialogVisible,
  detailMode,
  filteredProjects,
  searchKeyword,
  sections,
  selectedSection,
  applySearch,
  openDetail,
  startAnalysis,
} = useIntelligenceAnalysis()

const handleStartAnalysis = async () => {
  analyzing.value = true
  try {
    startAnalysis()
    const summary = normalizeRequirementAnalysis(projectStore.current?.config).basic.projectSummary
    const prompt = summary || projectStore.current?.description || '请基于项目信息进行情报分析'
    const run = await triggerPhaseRun('phase1', prompt)
    await pollRun(run.run_id, run.session_id)
    await projectStore.fetchProject(String(route.params.projectId))
    ElMessage.success('智能分析任务已完成')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '智能分析失败')
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.intelligence-page {
  display: flex;
  min-height: 100%;
  background: #f8fafc;
}

.intelligence-page__sidebar {
  width: 272px;
  flex: none;
  border-right: 1px solid #e2e8f0;
  background: #fff;
}

.intelligence-page__sidebar-head {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.intelligence-page__sidebar-title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  line-height: 1.5;
  font-weight: 500;
}

.intelligence-page__nav {
  padding: 16px;
  display: grid;
  gap: 8px;
}

.intelligence-page__nav-item {
  min-height: 48px;
  padding: 0 16px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: #334155;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.intelligence-page__nav-item--active {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

.intelligence-page__main {
  flex: 1;
  overflow: auto;
}

.intelligence-page__container {
  max-width: 1120px;
  padding: 32px;
}

.panel-card {
  padding: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.panel-card__primary {
  min-height: 40px;
  padding: 0 16px;
  border: none;
  border-radius: 10px;
  background: #2563eb;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.analysis-result {
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  background: #f8fbff;
}

.analysis-result__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.analysis-result__title {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 600;
}

.analysis-result__desc {
  margin: 6px 0 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.7;
}

.analysis-result__link {
  border: none;
  background: transparent;
  color: #2563eb;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.analysis-result__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.analysis-result__item {
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
}

.analysis-result__item h4 {
  margin: 0 0 6px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}

.analysis-result__item p {
  margin: 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.7;
}


.analysis-intro__icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 12px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
}

.analysis-intro__title {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 16px;
  font-weight: 500;
}

.analysis-intro__desc {
  margin: 0 0 20px;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.analysis-intro__grid {
  max-width: 680px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  text-align: left;
}

.analysis-intro__item {
  padding: 16px;
  border-radius: 10px;
  border: 1px solid;
}

.analysis-intro__item h4 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
}

.analysis-intro__item p {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
}

.analysis-intro__item--blue {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1e3a8a;
}

.analysis-intro__item--purple {
  background: #faf5ff;
  border-color: #e9d5ff;
  color: #6b21a8;
}

.analysis-intro__item--green {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}

.analysis-intro__item--orange {
  background: #fff7ed;
  border-color: #fed7aa;
  color: #9a3412;
}

.history-search {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.history-search__input {
  flex: 1;
  height: 42px;
  padding: 0 14px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  font-size: 14px;
}

.history-search__button {
  flex: none;
  min-width: 88px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.history-list {
  display: grid;
  gap: 12px;
}

.history-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.history-card__content {
  flex: 1;
  min-width: 0;
}

.history-card__title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.history-card__title {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 500;
}

.history-card__badge {
  padding: 4px 8px;
  border-radius: 999px;
  background: #f0fdf4;
  color: #15803d;
  font-size: 12px;
  font-weight: 600;
}

.history-card__desc {
  margin: 0 0 12px;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.history-card__meta-row,
.history-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-card__meta-row {
  margin-bottom: 10px;
}

.history-card__meta-row span,
.history-card__tags span {
  padding: 4px 8px;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
}

.history-card__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card__action {
  min-width: 96px;
  min-height: 38px;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.history-card__action--indigo {
  background: #4f46e5;
}

.history-card__action--purple {
  background: #7c3aed;
}

.history-empty {
  padding: 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: #64748b;
  font-size: 14px;
  text-align: center;
}

.detail-modal {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.55);
}

.detail-modal__card {
  width: min(720px, 100%);
  max-height: calc(100vh - 48px);
  overflow: auto;
  padding: 24px;
  border-radius: 16px;
  background: #fff;
}

.detail-modal__body {
  display: grid;
  gap: 16px;
}

.detail-modal__section h4 {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}

.detail-modal__section p {
  margin: 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.8;
}

.detail-modal__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-modal__tags span {
  padding: 4px 8px;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
}

.detail-modal__prototype {
  display: grid;
  gap: 14px;
}

.detail-modal__screen {
  min-height: 280px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
}

.detail-modal__caption {
  color: #475569;
  font-size: 14px;
  line-height: 1.8;
}

@media (max-width: 960px) {
  .intelligence-page {
    flex-direction: column;
  }

  .intelligence-page__sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .analysis-result__grid,
  .analysis-intro__grid {
    grid-template-columns: 1fr;
  }

  .analysis-result__head,
  .history-card {
    flex-direction: column;
  }

  .history-card__actions {
    flex-direction: row;
  }
}
</style>