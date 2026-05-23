<template>
  <div class="workspace-version-section">
    <button type="button" class="workspace-version-section__back" @click="$emit('back')">{{ backLabel }}</button>

    <div class="workspace-version-section__bar">
      <div class="workspace-version-section__label">{{ label }}</div>
      <div class="workspace-version-section__actions">
        <button
          v-for="version in versions"
          :key="version.id"
          type="button"
          class="workspace-version-section__pill"
          :class="{ 'workspace-version-section__pill--active': modelValue === version.id }"
          @click="$emit('update:modelValue', version.id)"
        >
          {{ version.name }}
        </button>
      </div>
      <div class="workspace-version-section__meta">{{ meta }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface WorkspaceVersionOption {
  id: string
  name: string
}

defineProps<{
  backLabel?: string
  label: string
  meta: string
  modelValue: string
  versions: WorkspaceVersionOption[]
}>()

defineEmits<{
  (e: 'back'): void
  (e: 'update:modelValue', value: string): void
}>()
</script>

<style scoped>
.workspace-version-section {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
}

.workspace-version-section__back,
.workspace-version-section__pill {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.workspace-version-section__back,
.workspace-version-section__pill {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #334155;
}

.workspace-version-section__back {
  justify-self: flex-start;
}

.workspace-version-section__bar {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.workspace-version-section__label {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 600;
}

.workspace-version-section__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 8px;
}

.workspace-version-section__pill--active {
  border: none;
  background: #2563eb;
  color: #fff;
}

.workspace-version-section__meta {
  color: #64748b;
  font-size: 12px;
}
</style>
