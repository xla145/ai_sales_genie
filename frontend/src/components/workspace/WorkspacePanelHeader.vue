<template>
  <div class="workspace-panel-header">
    <div class="workspace-panel-header__content">
      <slot>
        <h2 v-if="title" class="workspace-panel-header__title">{{ title }}</h2>
        <p v-if="subtitle" class="workspace-panel-header__subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    <div v-if="$slots.actions" class="workspace-panel-header__actions">
      <slot name="actions" />
    </div>
    <div v-else-if="meta" class="workspace-panel-header__meta">{{ meta }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  meta?: string
}>()
</script>

<style scoped>
.workspace-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.workspace-panel-header__title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  line-height: 1.5;
  font-weight: 500;
}

.workspace-panel-header__subtitle,
.workspace-panel-header__meta {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

.workspace-panel-header__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

@media (max-width: 1024px) {
  .workspace-panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
