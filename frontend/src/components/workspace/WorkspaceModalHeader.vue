<template>
  <div class="workspace-modal-header" :class="{ 'workspace-modal-header--align-start': align === 'start' }">
    <div class="workspace-modal-header__content">
      <slot>
        <h3 v-if="title" class="workspace-modal-header__title">{{ title }}</h3>
        <p v-if="subtitle" class="workspace-modal-header__subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    <div class="workspace-modal-header__actions">
      <slot name="actions">
        <button v-if="closable" type="button" class="workspace-modal-header__close" @click="$emit('close')">×</button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  closable?: boolean
  align?: 'center' | 'start'
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>

<style scoped>
.workspace-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.workspace-modal-header--align-start {
  align-items: flex-start;
}

.workspace-modal-header__content {
  min-width: 0;
}

.workspace-modal-header__title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 600;
}

.workspace-modal-header__subtitle {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}

.workspace-modal-header__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.workspace-modal-header__close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .workspace-modal-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
