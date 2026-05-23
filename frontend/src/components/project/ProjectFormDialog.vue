<template>
  <el-dialog
    class="project-form-dialog"
    :model-value="modelValue"
    :show-close="false"
    width="512px"
    destroy-on-close
    align-center
    @close="handleClose"
  >
    <template #header>
      <div class="project-form-dialog__header">
        <h2 class="project-form-dialog__title">{{ title }}</h2>
        <button class="project-form-dialog__close" type="button" aria-label="关闭" @click="handleClose">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="m6 6 12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </template>

    <el-form class="project-form-dialog__form" label-position="top" :model="form">
      <el-form-item>
        <template #label>项目名称 <span class="project-form-dialog__required">*</span></template>
        <el-input v-model="form.name" placeholder="输入项目名称" />
      </el-form-item>

      <el-form-item>
        <template #label>客户信息 <span class="project-form-dialog__required">*</span></template>
        <el-input v-model="form.clientInfo" placeholder="输入客户名称或公司" />
      </el-form-item>

      <el-form-item label="项目描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="输入项目描述（可选）"
        />
      </el-form-item>

      <el-form-item>
        <template #label>项目区域 <span class="project-form-dialog__required">*</span></template>
        <div class="project-form-dialog__region">
          <el-select v-model="form.province" placeholder="请选择省份" @change="handleProvinceChange">
            <el-option v-for="province in provinceOptions" :key="province" :label="province" :value="province" />
          </el-select>
          <el-select v-model="form.city" placeholder="请选择城市" :disabled="!form.province">
            <el-option v-for="cityOption in cityOptions" :key="cityOption" :label="cityOption" :value="cityOption" />
          </el-select>
        </div>
      </el-form-item>

      <el-form-item>
        <template #label>项目阶段 <span class="project-form-dialog__required">*</span></template>
        <el-select v-model="form.stage" placeholder="请选择项目阶段">
          <el-option v-for="stage in STAGE_OPTIONS" :key="stage" :label="stage" :value="stage" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <template #label>项目归属行业 <span class="project-form-dialog__required">*</span></template>
        <el-select v-model="form.industry" placeholder="请选择归属行业">
          <el-option v-for="industry in INDUSTRY_OPTIONS" :key="industry" :label="industry" :value="industry" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="project-form-dialog__footer">
        <button class="project-form-dialog__cancel" type="button" @click="handleClose">取消</button>
        <button class="project-form-dialog__submit" type="button" :disabled="!canSubmit" @click="handleSubmit">保存项目</button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { INDUSTRY_OPTIONS, PROVINCE_CITY_MAP, STAGE_OPTIONS } from '@/constants/project'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    initialName?: string
    initialDescription?: string | null
    initialClientInfo?: string
    initialProvince?: string
    initialCity?: string
    initialStage?: string
    initialIndustry?: string
  }>(),
  {
    title: '创建新项目',
    initialName: '',
    initialDescription: '',
    initialClientInfo: '',
    initialProvince: '',
    initialCity: '',
    initialStage: '',
    initialIndustry: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [boolean]
  submit: [{ name: string; description: string | null; clientInfo: string; province: string; city: string; stage: string; industry: string }]
}>()

const form = reactive({
  name: '',
  description: '',
  clientInfo: '',
  province: '',
  city: '',
  stage: '',
  industry: '',
})

watch(
  () => [props.modelValue, props.initialName, props.initialDescription, props.initialClientInfo, props.initialProvince, props.initialCity, props.initialStage, props.initialIndustry],
  () => {
    form.name = props.initialName
    form.description = props.initialDescription ?? ''
    form.clientInfo = props.initialClientInfo
    form.province = props.initialProvince
    form.city = props.initialCity
    form.stage = props.initialStage
    form.industry = props.initialIndustry
  },
  { immediate: true },
)

const provinceOptions = Object.keys(PROVINCE_CITY_MAP)
const cityOptions = computed(() => PROVINCE_CITY_MAP[form.province] ?? [])
const canSubmit = computed(
  () =>
    Boolean(
      form.name.trim() &&
        form.clientInfo.trim() &&
        form.province &&
        form.city &&
        form.stage &&
        form.industry,
    ),
)

const handleProvinceChange = () => {
  form.city = ''
}

const handleClose = () => emit('update:modelValue', false)

const handleSubmit = () => {
  if (!canSubmit.value) return

  emit('submit', {
    name: form.name.trim(),
    description: form.description.trim() || null,
    clientInfo: form.clientInfo.trim(),
    province: form.province.trim(),
    city: form.city.trim(),
    stage: form.stage.trim(),
    industry: form.industry.trim(),
  })
}
</script>

<style scoped>
.project-form-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.project-form-dialog__title {
  margin: 0;
  color: #0f172a;
  font-size: 24px;
  font-weight: 600;
}

.project-form-dialog__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.project-form-dialog__close svg {
  width: 20px;
  height: 20px;
}

.project-form-dialog__close:hover {
  background: #f1f5f9;
}

.project-form-dialog__required {
  color: #ef4444;
}

.project-form-dialog__region {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
}

.project-form-dialog__form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.project-form-dialog__form :deep(.el-form-item__label) {
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.project-form-dialog__form :deep(.el-select) {
  width: 100%;
}

.project-form-dialog__form :deep(.el-input__wrapper),
.project-form-dialog__form :deep(.el-textarea__inner) {
  min-height: 48px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #cbd5e1 inset;
}

.project-form-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.project-form-dialog__cancel,
.project-form-dialog__submit {
  padding: 10px 24px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 500;
}

.project-form-dialog__cancel {
  background: #f1f5f9;
  color: #334155;
}

.project-form-dialog__cancel:hover {
  background: #e2e8f0;
}

.project-form-dialog__submit {
  background: linear-gradient(90deg, #2563eb, #9333ea);
  box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
  color: #fff;
}

.project-form-dialog__submit:hover:not(:disabled) {
  background: linear-gradient(90deg, #1d4ed8, #7e22ce);
}

.project-form-dialog__submit:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>

<style>
.project-form-dialog.el-dialog {
  padding: 0;
  border-radius: 16px;
  overflow: hidden;
}

.project-form-dialog .el-dialog__header {
  margin: 0;
  padding: 32px 32px 0;
}

.project-form-dialog .el-dialog__body {
  padding: 24px 32px 0;
}

.project-form-dialog .el-dialog__footer {
  padding: 0 32px 32px;
}
</style>
