<template>
  <ProjectLayout>
    <div class="requirement-input-page">
      <!-- <header class="requirement-input-page__head">
        <div class="requirement-input-page__icon">录</div>
        <div>
          <h2>需求录入</h2>
          <p>详细描述项目需求，为AI分析提供基础信息</p>
        </div>
      </header> -->

      <div class="requirement-input-page__grid">
        <section class="requirement-input-page__panel">
          <div class="requirement-input-page__panel-head">
            <span>需求描述 <em>*</em></span>
            <small>建议500字以上</small>
          </div>
          <p class="requirement-input-page__hint">建议包含：业务背景、核心目标、功能需求、特殊要求等</p>
          <el-input
            v-model="projectSummary"
            type="textarea"
            :rows="16"
            resize="none"
            placeholder="请详细描述项目需求..."
          />
        </section>

        <section class="requirement-input-page__side">
          <article class="requirement-input-page__panel requirement-input-page__upload">
            <div class="requirement-input-page__panel-head">
              <span>附件上传</span>
              <small>可选</small>
            </div>
            <p class="requirement-input-page__hint">支持上传需求文档、设计稿、参考资料等文件</p>
            <input ref="fileInputRef" class="requirement-input-page__file" type="file" :accept="acceptedUploadTypes" @change="handleFileChange" />
            <button
              class="requirement-input-page__dropzone"
              type="button"
              :disabled="uploading"
              @click="openFilePicker"
              @dragover.prevent
              @drop.prevent="handleFileDrop"
            >
              <div class="requirement-input-page__dropzone-icon">↑</div>
              <strong>{{ uploading ? '正在上传...' : '点击上传或拖拽文件到此处' }}</strong>
              <span>支持 PDF、Word、Excel、PPT、图片等格式，单个文件不超过 20MB</span>
              <div class="requirement-input-page__tags">
                <span>.pdf</span><span>.doc</span><span>.xls</span><span>.ppt</span><span>.jpg</span>
              </div>
            </button>
            <div v-if="attachmentItems.length" class="requirement-input-page__attachments">
              <button
                v-if="attachmentItems.length > 1"
                type="button"
                class="requirement-input-page__attachments-toggle"
                @click="attachmentsExpanded = !attachmentsExpanded"
              >
                <span class="requirement-input-page__attachments-summary">
                  已上传 {{ attachmentItems.length }} 个文件
                </span>
                <span class="requirement-input-page__attachments-chevron" :class="{ 'requirement-input-page__attachments-chevron--open': attachmentsExpanded }">
                  ⌄
                </span>
              </button>

              <div
                class="requirement-input-page__attachments-list"
                :class="{ 'requirement-input-page__attachments-list--collapsed': attachmentItems.length > 1 && !attachmentsExpanded }"
              >
                <div
                  v-for="item in visibleAttachmentItems"
                  :key="item.id ?? `${item.name}-${item.meta}`"
                  class="requirement-input-page__attachment"
                >
                  <div>
                    <strong>{{ item.name }}</strong>
                    <span>{{ item.meta }}</span>
                  </div>
                  <button type="button" :disabled="deletingAttachmentId === item.id" @click="removeAttachment(item)">
                    {{ deletingAttachmentId === item.id ? '删除中...' : '删除' }}
                  </button>
                </div>
              </div>
            </div>
          </article>

          <article class="requirement-input-page__tips">
            <strong>填写建议</strong>
            <p>建议从<strong>业务背景、核心目标、功能需求、用户角色、特殊要求</strong>等维度描述，内容越详细，AI 分析越准确。</p>
          </article>
        </section>
      </div>

      <footer class="requirement-input-page__footer">
        <span>填写完成后可保存草稿或直接提交</span>
        <div class="requirement-input-page__footer-actions">
          <button type="button" :disabled="saving" @click="saveDraft">保存草稿</button>
          <button type="button" class="requirement-input-page__submit" :disabled="saving || !projectSummary.trim()" @click="submitAnalysis">
            {{ saving ? '处理中...' : '提交并开始分析' }}
          </button>
        </div>
      </footer>
    </div>
  </ProjectLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import { useProjectStore } from '@/stores/project'
import { normalizeRequirementAnalysis } from '@/utils/requirement'
import type { ProjectConfig, RequirementAttachmentItem } from '@/types/project'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const saving = ref(false)
const uploading = ref(false)
const deletingAttachmentId = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const projectSummary = ref('')
const attachmentItems = ref<RequirementAttachmentItem[]>([])
const attachmentsExpanded = ref(false)
const acceptedUploadTypes = '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.md,.png,.jpg,.jpeg'

const visibleAttachmentItems = computed(() => {
  if (attachmentItems.value.length <= 1 || attachmentsExpanded.value) {
    return attachmentItems.value
  }
  return []
})

const project = computed(() => projectStore.current)
const projectMeta = computed(() => (project.value?.config ?? {}) as ProjectConfig)

const hydrate = () => {
  const analysis = normalizeRequirementAnalysis(projectMeta.value)
  projectSummary.value = analysis.basic.projectSummary
  attachmentItems.value = [...analysis.attachments]
}

watch(projectMeta, hydrate, { immediate: true, deep: true })

const saveRequirementAnalysis = async (
  payload: { basic?: { projectSummary?: string }; attachments?: RequirementAttachmentItem[] },
  successMessage: string,
) => {
  if (!project.value) return
  saving.value = true
  try {
    await projectStore.updateRequirementAnalysis(String(route.params.projectId), payload)
    hydrate()
    ElMessage.success(successMessage)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

const saveDraft = async () => {
  await saveRequirementAnalysis({ basic: { projectSummary: projectSummary.value } }, '草稿已保存')
}

const submitAnalysis = async () => {
  if (!project.value || !projectSummary.value.trim()) return
  saving.value = true
  try {
    await projectStore.updateRequirementAnalysis(String(route.params.projectId), {
      basic: { projectSummary: projectSummary.value },
    })
    await projectStore.runPhase1(String(route.params.projectId), {
      prompt: projectSummary.value.trim(),
      session_id: project.value.current_session_id,
    })
    ElMessage.success('已提交并开始第一阶段分析')
    router.push(`/projects/${route.params.projectId}/requirement`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '提交失败')
  } finally {
    saving.value = false
  }
}

const openFilePicker = () => {
  if (!uploading.value) {
    fileInputRef.value?.click()
  }
}

const uploadFile = async (file: File) => {
  if (!project.value) return
  uploading.value = true
  try {
    await projectStore.uploadRequirementFile(String(route.params.projectId), file)
    hydrate()
    if (attachmentItems.value.length > 1) {
      attachmentsExpanded.value = false
    }
    ElMessage.success('附件上传成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '上传失败')
  } finally {
    uploading.value = false
  }
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    await uploadFile(file)
    input.value = ''
  }
}

const handleFileDrop = async (event: DragEvent) => {
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    await uploadFile(file)
  }
}

const removeAttachment = async (target: RequirementAttachmentItem) => {
  if (!project.value) return
  if (!target.id) {
    const nextRequirement = normalizeRequirementAnalysis(projectMeta.value)
    const nextAttachments = nextRequirement.attachments.filter((item) => !(item.name === target.name && item.meta === target.meta))
    await saveRequirementAnalysis({ attachments: nextAttachments }, '附件记录已删除')
    return
  }

  deletingAttachmentId.value = target.id
  try {
    await projectStore.deleteRequirementUpload(String(route.params.projectId), target.id)
    hydrate()
    if (attachmentItems.value.length <= 1) {
      attachmentsExpanded.value = false
    }
    ElMessage.success('附件已删除')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '删除失败')
  } finally {
    deletingAttachmentId.value = null
  }
}
</script>

<style scoped>
.requirement-input-page {
  padding: 24px;
}

.requirement-input-page__head {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.requirement-input-page__icon {
  display: inline-flex;
  width: 48px;
  height: 48px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  box-shadow: 0 10px 15px rgba(79, 70, 229, 0.3);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.requirement-input-page__head h2 {
  margin: 0;
  font-size: 24px;
}

.requirement-input-page__head p {
  margin: 4px 0 0;
  color: #475569;
  font-size: 14px;
}

.requirement-input-page__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.requirement-input-page__panel {
  padding: 24px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.requirement-input-page__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
}

.requirement-input-page__panel-head em {
  color: #ef4444;
  font-style: normal;
}

.requirement-input-page__panel-head small,
.requirement-input-page__hint {
  color: #64748b;
  font-size: 12px;
}

.requirement-input-page__hint {
  margin: 0 0 16px;
}

.requirement-input-page__side {
  display: grid;
  gap: 24px;
}

.requirement-input-page__file {
  display: none;
}

.requirement-input-page__dropzone {
  display: grid;
  gap: 12px;
  justify-items: center;
  width: 100%;
  min-height: 280px;
  padding: 24px;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  text-align: center;
}

.requirement-input-page__dropzone-icon {
  display: inline-flex;
  width: 64px;
  height: 64px;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  color: #4f46e5;
  font-size: 28px;
}

.requirement-input-page__dropzone strong {
  color: #0f172a;
}

.requirement-input-page__dropzone span {
  color: #475569;
  font-size: 14px;
}

.requirement-input-page__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.requirement-input-page__tags span {
  padding: 4px 10px;
  border-radius: 8px;
  background: #e0e7ff;
  color: #4338ca;
  font-size: 12px;
  font-weight: 500;
}

.requirement-input-page__attachments {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.requirement-input-page__attachments-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  font: inherit;
}

.requirement-input-page__attachments-summary {
  color: #334155;
  font-size: 13px;
  font-weight: 600;
}

.requirement-input-page__attachments-chevron {
  color: #64748b;
  font-size: 14px;
  line-height: 1;
  transition: transform 0.2s ease;
}

.requirement-input-page__attachments-chevron--open {
  transform: rotate(180deg);
}

.requirement-input-page__attachments-list {
  display: grid;
  gap: 8px;
}

.requirement-input-page__attachments-list--collapsed .requirement-input-page__attachment:last-child {
  margin-bottom: 0;
}

.requirement-input-page__attachment {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.requirement-input-page__attachment strong {
  display: block;
  font-size: 13px;
}

.requirement-input-page__attachment span {
  color: #64748b;
  font-size: 12px;
}

.requirement-input-page__attachment button {
  border: none;
  background: transparent;
  color: #dc2626;
  cursor: pointer;
  font-size: 12px;
}

.requirement-input-page__tips {
  padding: 20px;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff, #eef2ff);
}

.requirement-input-page__tips strong {
  display: block;
  margin-bottom: 8px;
  color: #312e81;
}

.requirement-input-page__tips p {
  margin: 0;
  color: #4338ca;
  font-size: 12px;
  line-height: 1.625;
}

.requirement-input-page__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 16px;
  background: #fff;
}

.requirement-input-page__footer span {
  color: #475569;
  font-size: 14px;
}

.requirement-input-page__footer-actions {
  display: flex;
  gap: 12px;
}

.requirement-input-page__footer-actions button {
  padding: 10px 20px;
  border: 2px solid #cbd5e1;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
}

.requirement-input-page__submit {
  border: none !important;
  background: linear-gradient(90deg, #4f46e5, #4338ca) !important;
  color: #fff !important;
}

@media (max-width: 1024px) {
  .requirement-input-page__grid {
    grid-template-columns: 1fr;
  }
}
</style>
