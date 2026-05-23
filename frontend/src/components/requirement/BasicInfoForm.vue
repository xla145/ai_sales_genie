<template>
  <div class="editable-form">
    <div v-for="item in items" :key="item.key" class="editable-form__field">
      <div class="editable-form__label-row">
        <label class="editable-form__label">{{ item.label }}</label>
        <span v-if="getStatus(item.key) === 'confirmed'" class="editable-form__status editable-form__status--confirmed">✓ 已确认</span>
        <span v-else-if="getStatus(item.key) === 'pending'" class="editable-form__status editable-form__status--pending">? 待确认</span>
      </div>
      <div class="editable-form__input-row">
        <template v-if="item.type === 'textarea'">
          <el-input
            v-model="item.value"
            type="textarea"
            :rows="item.rows ?? 3"
            :placeholder="item.placeholder"
            @input="handleChange(item.key)"
          />
        </template>
        <template v-else-if="item.type === 'radio'">
          <el-radio-group v-model="item.value" class="editable-form__radio-group" @change="handleChange(item.key)">
            <el-radio v-for="option in item.options ?? []" :key="option" :label="option">{{ option }}</el-radio>
          </el-radio-group>
        </template>
        <template v-else>
          <el-input v-model="item.value" :placeholder="item.placeholder" @input="handleChange(item.key)" />
        </template>
        <button
          v-if="getStatus(item.key) === 'pending'"
          type="button"
          class="editable-form__confirm"
          @click="confirmField(item.key)"
        >
          ✓ 确认
        </button>
      </div>
      <p v-if="item.hint" class="editable-form__hint">{{ item.hint }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

defineProps<{
  items: Array<{
    key: string
    label: string
    value: string
    placeholder?: string
    hint?: string
    type?: 'text' | 'textarea' | 'radio'
    rows?: number
    options?: string[]
  }>
}>()

const emit = defineEmits<{ change: [] }>()

type FieldStatus = 'confirmed' | 'pending' | null

const fieldStatus = reactive<Record<string, FieldStatus>>({
  projectName: 'confirmed',
  projectSummary: 'pending',
  industry: 'confirmed',
  projectType: null,
  keywords: 'pending',
})

const getStatus = (key: string) => fieldStatus[key] ?? null

const handleChange = (key: string) => {
  if (fieldStatus[key] === 'confirmed') {
    fieldStatus[key] = 'pending'
  }
  emit('change')
}

const confirmField = (key: string) => {
  fieldStatus[key] = 'confirmed'
  emit('change')
}
</script>

<style scoped>
.editable-form {
  display: grid;
  gap: 12px;
}

.editable-form__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editable-form__label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.editable-form__label {
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.editable-form__status {
  font-size: 12px;
  font-weight: 500;
}

.editable-form__status--confirmed { color: #16a34a; }
.editable-form__status--pending { color: #ea580c; }

.editable-form__input-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.editable-form__input-row :deep(.el-input),
.editable-form__input-row :deep(.el-textarea) {
  flex: 1;
}

.editable-form__confirm {
  flex-shrink: 0;
  height: 38px;
  padding: 0 16px;
  border: none;
  border-radius: 8px;
  background: #16a34a;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.editable-form__hint {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.7;
}

.editable-form__radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  flex: 1;
}
</style>
