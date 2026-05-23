<template>
  <aside class="attachment-panel">
    <h4 class="attachment-panel__title">附件管理</h4>
    <div class="attachment-list">
      <div v-for="item in items" :key="`${item.name}-${item.meta}`" class="attachment-list__item">
        <span class="attachment-list__icon">📎</span>
        <div class="attachment-list__body">
          <div class="attachment-list__row">
            <span class="attachment-list__name">{{ item.name }}</span>
            <div class="attachment-list__actions">
              <button type="button" title="下载">↓</button>
              <button type="button" title="删除" @click="$emit('remove', item)">×</button>
            </div>
          </div>
          <div class="attachment-list__meta">
            <span>{{ item.size || '—' }}</span>
            <span>{{ item.meta }}</span>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{ items: Array<{ name: string; meta: string; size?: string }> }>()

defineEmits<{
  upload: []
  remove: [item: { name: string; meta: string; size?: string }]
}>()
</script>

<style scoped>
.attachment-panel {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.attachment-panel__title {
  margin: 0 0 12px;
  color: #1e293b;
  font-size: 14px;
  font-weight: 500;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-list__item {
  display: flex;
  gap: 8px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.attachment-list__icon {
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 14px;
}

.attachment-list__body {
  flex: 1;
  min-width: 0;
}

.attachment-list__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.attachment-list__name {
  overflow: hidden;
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-list__actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.attachment-list__actions button {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
}

.attachment-list__actions button:last-child {
  color: #dc2626;
}

.attachment-list__meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}
</style>
