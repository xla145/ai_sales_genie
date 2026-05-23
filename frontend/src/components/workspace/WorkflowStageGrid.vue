<template>
  <section class="workflow-page">
    <article v-for="stage in stages" :key="stage.name" class="workflow-card">
      <div class="workflow-card__status"></div>
      <h3 class="workflow-card__title">{{ stage.name }}</h3>
      <p class="workflow-card__desc">{{ stage.description }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { WorkflowStageItem } from '@/constants/workspace'

defineProps<{
  stages: WorkflowStageItem[]
}>()
</script>

<style scoped>
.workflow-page {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px;
}

.workflow-card {
  min-height: 168px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.workflow-card__status {
  width: 18px;
  height: 18px;
  margin-bottom: 14px;
  border: 2px solid #cbd5e1;
  border-radius: 999px;
}

.workflow-card__title {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 15px;
  line-height: 1.5;
  font-weight: 500;
}

.workflow-card__desc {
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

@media (max-width: 1100px) {
  .workflow-page {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .workflow-page {
    grid-template-columns: 1fr;
  }
}
</style>
