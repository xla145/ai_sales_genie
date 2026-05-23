<template>
  <AppLayout>
    <div class="project-list-page">
      <section class="project-list-page__header">
        <div class="project-list-page__header-main">
          <div class="project-list-page__title-row">
            <div class="project-list-page__logo">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M20 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M22 5h-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4 17v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5 18H3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h1 class="project-list-page__title">OPC 规范支持中心</h1>
          </div>
          <p class="project-list-page__subtitle">三坨理想泥 · 智能售前协作平台</p>
        </div>

        <div class="project-list-page__header-actions">
          <div class="project-list-page__user">
            <div class="project-list-page__user-icon">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="project-list-page__user-name">{{ displayUserName }}</span>
          </div>
          <button class="project-list-page__logout" type="button" title="登出" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="21" x2="9" y1="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="project-list-page__create" type="button" @click="openCreate">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 5v14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            创建项目
          </button>
        </div>
      </section>

      <section class="project-list-page__intro">
        <div class="project-list-page__intro-glow" aria-hidden="true"></div>
        <p class="project-list-page__intro-text">
          OPC 规范支持中心旨在支撑售前团队快速响应客户需求、梳理业务场景、形成初步技术方案与实施思路，并沉淀标准化、结构化的项目信息。通过提升售前需求理解、方案输出与信息流转效率，为软件定制化团队提供完整、有效的前置信息支撑，促进售前与交付环节的高效衔接。
        </p>
      </section>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

      <section v-loading="projectStore.loading" class="project-list-page__content">
        <div v-if="projectStore.items.length" class="project-list-page__grid">
          <ProjectCard
            v-for="project in projectStore.items"
            :key="project.project_id"
            :project="project"
            :is-new="project.project_id === newProjectId"
            :is-fading="project.project_id === fadingProjectId"
            @open="goToProject(project.project_id)"
            @edit="openEdit(project.project_id)"
            @delete="openDelete(project.project_id, project.name)"
          />
        </div>

        <article v-else-if="!projectStore.loading" class="project-list-page__empty">
          <div class="project-list-page__empty-icon">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <rect width="20" height="14" x="2" y="6" rx="2" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3 class="project-list-page__empty-title">还没有项目</h3>
          <p class="project-list-page__empty-text">创建您的第一个项目，开始使用 OPC 规范支持中心管理您的售前项目</p>
          <button class="project-list-page__empty-create" type="button" @click="openCreate">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 5v14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            创建第一个项目
          </button>
        </article>
      </section>

      <ProjectFormDialog
        v-model="dialogVisible"
        :title="editingProjectId ? '编辑项目' : '创建新项目'"
        :initial-name="formName"
        :initial-description="formDescription"
        :initial-client-info="formClientInfo"
        :initial-province="formProvince"
        :initial-city="formCity"
        :initial-stage="formStage"
        :initial-industry="formIndustry"
        @submit="handleSubmit"
      />
      <DeleteProjectDialog v-model="deleteVisible" :project-name="deleteName" @confirm="handleDelete" />
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectCard from '@/components/project/ProjectCard.vue'
import ProjectFormDialog from '@/components/project/ProjectFormDialog.vue'
import DeleteProjectDialog from '@/components/project/DeleteProjectDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const dialogVisible = ref(false)
const deleteVisible = ref(false)
const deleteId = ref('')
const deleteName = ref('')
const editingProjectId = ref('')
const errorMessage = ref('')
const newProjectId = ref<string | null>(null)
const fadingProjectId = ref<string | null>(null)
const displayUserName = computed(() => authStore.displayName)

const editingProject = computed(() => projectStore.items.find((item) => item.project_id === editingProjectId.value) ?? null)
const editingConfig = computed(() => (editingProject.value?.config ?? {}) as Record<string, unknown>)
const formName = computed(() => editingProject.value?.name ?? '')
const formDescription = computed(() => editingProject.value?.description ?? '')
const formClientInfo = computed(() => String(editingConfig.value.clientInfo ?? ''))
const formProvince = computed(() => String(editingConfig.value.province ?? ''))
const formCity = computed(() => String(editingConfig.value.city ?? ''))
const formStage = computed(() => String(editingConfig.value.stage ?? ''))
const formIndustry = computed(() => String(editingConfig.value.industry ?? ''))

onMounted(async () => {
  try {
    await projectStore.fetchProjects()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '加载项目失败'
  }
})

const goToProject = (projectId: string) => {
  router.push(`/projects/${projectId}/overview`)
}

const resetDialogState = () => {
  dialogVisible.value = false
  editingProjectId.value = ''
}

const openCreate = () => {
  editingProjectId.value = ''
  dialogVisible.value = true
}

const openEdit = (projectId: string) => {
  editingProjectId.value = projectId
  dialogVisible.value = true
}

const handleSubmit = async (payload: {
  name: string
  description: string | null
  clientInfo: string
  province: string
  city: string
  stage: string
  industry: string
}) => {
  errorMessage.value = ''
  try {
    if (editingProjectId.value) {
      await projectStore.updateProjectOverview(editingProjectId.value, {
        name: payload.name,
        description: payload.description,
        clientInfo: payload.clientInfo,
        province: payload.province,
        city: payload.city,
        stage: payload.stage,
        industry: payload.industry,
      })
      ElMessage.success('项目修改成功')
    } else {
      const project = await projectStore.createProject({
        name: payload.name,
        description: payload.description,
        config: {
          clientInfo: payload.clientInfo,
          province: payload.province,
          city: payload.city,
          stage: payload.stage,
          industry: payload.industry,
        },
      })
      ElMessage.success('项目创建成功')
      resetDialogState()
      newProjectId.value = project.project_id
      setTimeout(() => {
        newProjectId.value = null
      }, 400)
      goToProject(project.project_id)
      return
    }
    resetDialogState()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : editingProjectId.value ? '修改项目失败' : '创建项目失败')
  }
}

const openDelete = (projectId: string, projectName: string) => {
  deleteId.value = projectId
  deleteName.value = projectName
  deleteVisible.value = true
}

const handleDelete = async () => {
  try {
    fadingProjectId.value = deleteId.value
    deleteVisible.value = false
    await new Promise((resolve) => setTimeout(resolve, 300))
    await projectStore.deleteProject(deleteId.value)
    deleteId.value = ''
    deleteName.value = ''
    fadingProjectId.value = null
    ElMessage.success('项目删除成功')
  } catch (error) {
    fadingProjectId.value = null
    ElMessage.error(error instanceof Error ? error.message : '删除项目失败')
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.project-list-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

.project-list-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 32px;
}

.project-list-page__header-main {
  min-width: 0;
}

.project-list-page__title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.project-list-page__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
  color: #fff;
}

.project-list-page__logo svg {
  width: 24px;
  height: 24px;
}

.project-list-page__title {
  margin: 0;
  background: linear-gradient(90deg, #0f172a, #1e3a8a, #0f172a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 30px;
  font-weight: 700;
  line-height: 1.2;
}

.project-list-page__subtitle {
  margin: 0 0 0 56px;
  color: #475569;
  font-size: 14px;
}

.project-list-page__header-actions {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 12px;
}

.project-list-page__user {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 12px;
  background: #f1f5f9;
}

.project-list-page__user-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 8px;
  background: #3b82f6;
  color: #fff;
}

.project-list-page__user-icon svg {
  width: 16px;
  height: 16px;
}

.project-list-page__user-name {
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.project-list-page__logout,
.project-list-page__create,
.project-list-page__empty-create {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: none;
  cursor: pointer;
  font: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.project-list-page__logout {
  padding: 8px 12px;
  border-radius: 12px;
  background: #f1f5f9;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.project-list-page__logout svg {
  width: 16px;
  height: 16px;
}

.project-list-page__logout:hover {
  background: #e2e8f0;
}

.project-list-page__create,
.project-list-page__empty-create {
  padding: 10px 20px;
  border-radius: 12px;
  background: linear-gradient(90deg, #2563eb, #1d4ed8);
  box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.project-list-page__create svg,
.project-list-page__empty-create svg {
  width: 16px;
  height: 16px;
}

.project-list-page__create:hover,
.project-list-page__empty-create:hover {
  box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
  transform: scale(1.05);
}

.project-list-page__intro {
  position: relative;
  margin-bottom: 32px;
  padding: 20px;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.project-list-page__intro-glow {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 0;
  width: 256px;
  height: 256px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.4), transparent);
  filter: blur(48px);
}

.project-list-page__intro-text {
  position: relative;
  z-index: 1;
  margin: 0;
  color: #334155;
  font-size: 14px;
  line-height: 1.625;
}

.project-list-page__content {
  min-height: 320px;
}

.project-list-page__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.project-list-page__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}

.project-list-page__empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin-bottom: 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, #f1f5f9, #dbeafe);
  box-shadow: 0 10px 15px rgba(15, 23, 42, 0.08);
  color: #94a3b8;
  animation: project-empty-float 3s ease-in-out infinite;
}

.project-list-page__empty-icon svg {
  width: 48px;
  height: 48px;
}

.project-list-page__empty-title {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 20px;
  font-weight: 600;
}

.project-list-page__empty-text {
  max-width: 448px;
  margin: 0 0 32px;
  color: #475569;
  font-size: 14px;
  line-height: 1.625;
}

@keyframes project-empty-float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-10px);
  }
}

@media (max-width: 1280px) {
  .project-list-page__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .project-list-page__header {
    flex-direction: column;
  }

  .project-list-page__subtitle {
    margin-left: 0;
  }

  .project-list-page__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
