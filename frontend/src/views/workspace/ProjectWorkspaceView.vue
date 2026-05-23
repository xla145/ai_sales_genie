<template>
  <ProjectLayout>
    <div class="workspace-dashboard">
      <section class="workspace-dashboard__overview">
        <article class="workspace-dashboard__project-card">
          <div class="workspace-dashboard__project-header">
            <h3 class="workspace-dashboard__project-name">项目概览</h3>
            <button class="workspace-dashboard__edit-link" type="button" @click="goToRequirement">编辑需求</button>
          </div>

          <div class="workspace-dashboard__field">
            <div class="workspace-dashboard__field-head">
              <span>项目名称</span>
            </div>
            <el-input v-model="overviewForm.name" placeholder="请输入项目名称" />
          </div>

          <div class="workspace-dashboard__field">
            <div class="workspace-dashboard__field-head">
              <span>项目描述</span>
            </div>
            <el-input
              v-model="overviewForm.description"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="描述客户背景、核心目标、阶段任务或预期输出"
            />
          </div>

          <div class="workspace-dashboard__info-list">
            <div class="workspace-dashboard__info-item">
              <div class="workspace-dashboard__info-icon workspace-dashboard__info-icon--blue">甲</div>
              <div class="workspace-dashboard__info-copy workspace-dashboard__info-copy--form">
                <div class="workspace-dashboard__info-label">甲方名称</div>
                <el-input v-model="overviewForm.clientInfo" placeholder="请输入客户信息" />
              </div>
            </div>
            <div class="workspace-dashboard__info-item">
              <div class="workspace-dashboard__info-icon workspace-dashboard__info-icon--slate">地</div>
              <div class="workspace-dashboard__info-copy workspace-dashboard__info-copy--form workspace-dashboard__info-copy--grid">
                <div>
                  <div class="workspace-dashboard__info-label">所属省份</div>
                  <el-select v-model="overviewForm.province" placeholder="请选择所属省份">
                    <el-option v-for="province in Object.keys(PROVINCE_CITY_MAP)" :key="province" :label="province" :value="province" />
                  </el-select>
                </div>
                <div>
                  <div class="workspace-dashboard__info-label">所属城市</div>
                  <el-select v-model="overviewForm.city" placeholder="请选择所属城市" filterable allow-create default-first-option>
                    <el-option v-for="cityOption in cityOptions" :key="cityOption" :label="cityOption" :value="cityOption" />
                  </el-select>
                </div>
              </div>
            </div>
            <div class="workspace-dashboard__info-item">
              <div class="workspace-dashboard__info-icon workspace-dashboard__info-icon--green">阶</div>
              <div class="workspace-dashboard__info-copy workspace-dashboard__info-copy--form">
                <div class="workspace-dashboard__info-label">项目阶段</div>
                <el-select v-model="overviewForm.stage" placeholder="请选择项目阶段">
                  <el-option v-for="stage in STAGE_OPTIONS" :key="stage" :label="stage" :value="stage" />
                </el-select>
              </div>
            </div>
            <div class="workspace-dashboard__info-item">
              <div class="workspace-dashboard__info-icon workspace-dashboard__info-icon--orange">行</div>
              <div class="workspace-dashboard__info-copy workspace-dashboard__info-copy--form">
                <div class="workspace-dashboard__info-label">归属行业</div>
                <el-select v-model="overviewForm.industry" placeholder="请选择所属行业" filterable allow-create default-first-option>
                  <el-option v-for="industry in INDUSTRY_OPTIONS" :key="industry" :label="industry" :value="industry" />
                </el-select>
              </div>
            </div>
          </div>

          <div class="workspace-dashboard__field-actions workspace-dashboard__field-actions--start">
            <button class="workspace-dashboard__primary-button" type="button" :disabled="saving" @click="saveOverviewInfo">
              {{ saving ? '保存中...' : '保存项目信息' }}
            </button>
          </div>
        </article>

        <article class="workspace-dashboard__requirement-card">
          <div class="workspace-dashboard__requirement-head">
            <div class="workspace-dashboard__requirement-mark">需</div>
            <div>
              <h3 class="workspace-dashboard__requirement-title">需求录入</h3>
              <p class="workspace-dashboard__requirement-subtitle">详细描述项目需求，为AI分析提供基础信息</p>
            </div>
            <button class="workspace-dashboard__analysis-button" type="button" @click="goToRequirement">
              开始分析
            </button>
          </div>

          <div class="workspace-dashboard__field">
            <div class="workspace-dashboard__field-head">
              <span>需求描述</span>
              <span class="workspace-dashboard__field-required">*</span>
              <span class="workspace-dashboard__field-tip">建议包含：业务背景、核心目标、功能需求等</span>
            </div>
            <el-input
              v-model="projectSummary"
              type="textarea"
              :rows="8"
              resize="none"
              placeholder="请详细描述项目需求...

1. 业务背景：当前面临的痛点和挑战
2. 核心目标：期望通过系统解决什么问题
3. 功能需求：需要实现哪些核心功能
4. 特殊要求：性能、安全、合规等特殊要求"
            />
            <div class="workspace-dashboard__field-actions">
              <button class="workspace-dashboard__ghost-button" type="button" @click="goToRequirement">前往完整需求分析</button>
              <button class="workspace-dashboard__ghost-button" type="button" :disabled="saving || !projectSummary.trim()" @click="runPhase1Structuring">
                {{ saving ? '处理中...' : '执行第一阶段结构化' }}
              </button>
              <button class="workspace-dashboard__primary-button" type="button" :disabled="saving" @click="saveOverviewRequirement">
                {{ saving ? '保存中...' : '保存需求描述' }}
              </button>
            </div>
          </div>

          <div class="workspace-dashboard__field">
            <div class="workspace-dashboard__field-head">
              <span>附件上传</span>
              <span class="workspace-dashboard__field-optional">（可选）</span>
            </div>
            <button class="workspace-dashboard__upload" type="button" @click="handleAttachmentUpload">
              <div class="workspace-dashboard__upload-icon">↑</div>
              <div class="workspace-dashboard__upload-title">点击新增附件记录</div>
              <div class="workspace-dashboard__upload-text">当前先保存附件元信息到项目配置</div>
              <div class="workspace-dashboard__upload-text">后续可再接入真实文件上传</div>
              <div class="workspace-dashboard__file-tags">
                <span>.pdf</span>
                <span>.doc</span>
                <span>.docx</span>
                <span>.xls</span>
                <span>.xlsx</span>
                <span>.txt</span>
              </div>
            </button>
            <div v-if="attachmentItems.length" class="workspace-dashboard__attachment-list">
              <div v-for="item in attachmentItems" :key="`${item.name}-${item.meta}`" class="workspace-dashboard__attachment-item">
                <div class="workspace-dashboard__attachment-content">
                  <div>
                    <div class="workspace-dashboard__attachment-name">{{ item.name }}</div>
                    <div class="workspace-dashboard__attachment-meta">{{ item.meta }}</div>
                  </div>
                  <button class="workspace-dashboard__attachment-remove" type="button" :disabled="saving" @click="removeAttachment(item)">
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import { INDUSTRY_OPTIONS, PROVINCE_CITY_MAP, STAGE_OPTIONS } from '@/constants/project'
import { useProjectStore } from '@/stores/project'
import { normalizeRequirementAnalysis } from '@/utils/requirement'
import type { ProjectConfig } from '@/types/project'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const saving = ref(false)
const projectSummary = ref('')
const attachmentItems = ref<Array<{ name: string; meta: string }>>([])
const overviewForm = reactive({
  name: '',
  description: '',
  clientInfo: '',
  province: '',
  city: '',
  stage: '',
  industry: '',
})

const goToRequirement = () => {
  router.push(`/projects/${route.params.projectId}/requirement`)
}

const project = computed(() => projectStore.current)
const projectMeta = computed(() => (project.value?.config ?? {}) as ProjectConfig)
const requirementAnalysis = computed(() => normalizeRequirementAnalysis(projectMeta.value))
const cityOptions = computed(() => PROVINCE_CITY_MAP[overviewForm.province] ?? [])

const hydrateOverview = () => {
  overviewForm.name = project.value?.name ?? ''
  overviewForm.description = project.value?.description ?? ''
  overviewForm.clientInfo = String(projectMeta.value.clientInfo ?? '')
  overviewForm.province = String(projectMeta.value.province ?? '')
  overviewForm.city = String(projectMeta.value.city ?? '')
  overviewForm.stage = String(projectMeta.value.stage ?? '')
  overviewForm.industry = String(projectMeta.value.industry ?? '')
  projectSummary.value = requirementAnalysis.value.basic.projectSummary
  attachmentItems.value = [...requirementAnalysis.value.attachments]
}

const saveRequirementAnalysis = async (
  payload: { basic?: { projectSummary?: string }; attachments?: Array<{ name: string; meta: string }>; supplement?: { notes?: string } },
  successMessage: string,
) => {
  if (!project.value) return
  saving.value = true
  try {
    await projectStore.updateRequirementAnalysis(String(route.params.projectId), payload)
    hydrateOverview()
    ElMessage.success(successMessage)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

const saveOverviewInfo = async () => {
  if (!project.value) return
  saving.value = true
  try {
    await projectStore.updateProjectOverview(String(route.params.projectId), {
      name: overviewForm.name,
      description: overviewForm.description.trim() || null,
      clientInfo: overviewForm.clientInfo,
      province: overviewForm.province,
      city: overviewForm.city,
      stage: overviewForm.stage,
      industry: overviewForm.industry,
    })
    hydrateOverview()
    ElMessage.success('项目信息已保存')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

const saveOverviewRequirement = async () => {
  await saveRequirementAnalysis({
    basic: {
      projectSummary: projectSummary.value,
    },
  }, '需求描述已保存')
}

const runPhase1Structuring = async () => {
  if (!project.value || !projectSummary.value.trim()) return
  saving.value = true
  try {
    await projectStore.runPhase1(String(route.params.projectId), {
      prompt: projectSummary.value.trim(),
      session_id: project.value.current_session_id,
    })
    hydrateOverview()
    ElMessage.success('第一阶段结构化已完成，已同步到需求分析')
    router.push(`/projects/${route.params.projectId}/requirement`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '第一阶段执行失败')
  } finally {
    saving.value = false
  }
}

const handleAttachmentUpload = async () => {
  const nextRequirement = normalizeRequirementAnalysis(projectMeta.value)
  const nextAttachments = [
    {
      name: `附件_${nextRequirement.attachments.length + 1}.txt`,
      meta: new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-'),
    },
    ...nextRequirement.attachments,
  ]
  await saveRequirementAnalysis({
    attachments: nextAttachments,
  }, '附件记录已保存')
}

const removeAttachment = async (target: { name: string; meta: string }) => {
  const nextRequirement = normalizeRequirementAnalysis(projectMeta.value)
  const nextAttachments = nextRequirement.attachments.filter((item) => !(item.name === target.name && item.meta === target.meta))
  await saveRequirementAnalysis({
    attachments: nextAttachments,
  }, '附件记录已删除')
}

onMounted(async () => {
  await projectStore.fetchProject(String(route.params.projectId))
  hydrateOverview()
})
</script>

<style scoped>
.workspace-dashboard {
  min-height: 100%;
  padding: 16px;
}

.workspace-dashboard__overview {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 16px;
}

.workspace-dashboard__project-card,
.workspace-dashboard__requirement-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.workspace-dashboard__project-card {
  padding: 16px;
}

.workspace-dashboard__project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.workspace-dashboard__project-name {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
  line-height: 1.4;
  font-weight: 500;
}

.workspace-dashboard__edit-link {
  border: none;
  background: transparent;
  color: #2563eb;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.workspace-dashboard__summary {
  margin: 0 0 16px;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.workspace-dashboard__info-list {
  display: grid;
  gap: 10px;
}

.workspace-dashboard__info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  background: #f8fafc;
}

.workspace-dashboard__info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}

.workspace-dashboard__info-icon--blue {
  background: #dbeafe;
  color: #2563eb;
}

.workspace-dashboard__info-icon--slate {
  background: #e2e8f0;
  color: #475569;
}

.workspace-dashboard__info-icon--green {
  background: #dcfce7;
  color: #16a34a;
}

.workspace-dashboard__info-icon--orange {
  background: #ffedd5;
  color: #ea580c;
}

.workspace-dashboard__info-copy {
  min-width: 0;
  flex: 1;
}

.workspace-dashboard__info-copy--form {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.workspace-dashboard__info-copy--grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.workspace-dashboard__info-label {
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

.workspace-dashboard__info-value {
  color: #0f172a;
  font-size: 14px;
  line-height: 1.6;
  font-weight: 500;
  word-break: break-word;
}

.workspace-dashboard__requirement-card {
  padding: 16px;
}

.workspace-dashboard__requirement-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.workspace-dashboard__requirement-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #dbeafe;
  color: #2563eb;
  font-size: 16px;
  font-weight: 700;
}

.workspace-dashboard__requirement-title {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  line-height: 1.5;
  font-weight: 500;
}

.workspace-dashboard__requirement-subtitle {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.workspace-dashboard__analysis-button,
.workspace-dashboard__primary-button,
.workspace-dashboard__ghost-button {
  min-height: 36px;
  padding: 0 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.workspace-dashboard__analysis-button,
.workspace-dashboard__primary-button {
  border: none;
  background: #2563eb;
  color: #fff;
}

.workspace-dashboard__analysis-button {
  margin-left: auto;
}

.workspace-dashboard__primary-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.workspace-dashboard__ghost-button {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #334155;
}

.workspace-dashboard__field + .workspace-dashboard__field {
  margin-top: 16px;
}

.workspace-dashboard__field-head {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  flex-wrap: wrap;
}

.workspace-dashboard__field-required {
  color: #ef4444;
}

.workspace-dashboard__field-tip,
.workspace-dashboard__field-optional {
  color: #64748b;
  font-size: 12px;
  font-weight: 400;
}

.workspace-dashboard__field-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
}

.workspace-dashboard__field-actions--start {
  justify-content: flex-start;
}

.workspace-dashboard__upload {
  display: flex;
  width: 100%;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 24px 16px;
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  background: #fff;
  text-align: center;
  cursor: pointer;
}

.workspace-dashboard__upload-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f1f5f9;
  color: #94a3b8;
  font-size: 20px;
}

.workspace-dashboard__upload-title {
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
}

.workspace-dashboard__upload-text {
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

.workspace-dashboard__file-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-top: 4px;
}

.workspace-dashboard__file-tags span {
  padding: 2px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
}

.workspace-dashboard__attachment-list {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.workspace-dashboard__attachment-item {
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

.workspace-dashboard__attachment-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.workspace-dashboard__attachment-name {
  color: #0f172a;
  font-size: 13px;
  font-weight: 600;
}

.workspace-dashboard__attachment-meta {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.workspace-dashboard__attachment-remove {
  border: none;
  background: transparent;
  color: #dc2626;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  flex: none;
}

.workspace-dashboard__attachment-remove:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 1100px) {
  .workspace-dashboard__overview {
    grid-template-columns: 1fr;
  }

  .workspace-dashboard__info-copy--grid {
    grid-template-columns: 1fr;
  }
}
</style>
