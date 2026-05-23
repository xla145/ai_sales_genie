<template>
  <aside class="readiness-panel">
    <div class="readiness-panel__head">
      <h3 class="readiness-panel__title">需求评估</h3>
      <span class="readiness-panel__grade" :class="gradeClass">{{ level }} - {{ levelLabel }}</span>
    </div>

    <div class="readiness-panel__overall">
      <div class="readiness-panel__overall-row">
        <span>整体就绪度</span>
        <span class="readiness-panel__overall-score">{{ score }}%</span>
      </div>
      <div class="readiness-panel__bar">
        <div class="readiness-panel__bar-fill readiness-panel__bar-fill--blue" :style="{ width: `${score}%` }"></div>
      </div>
    </div>

    <div class="readiness-panel__divider"></div>

    <div class="readiness-panel__metrics">
      <div v-for="item in metrics" :key="item.label" class="readiness-panel__metric">
        <div class="readiness-panel__metric-row">
          <span>{{ item.label }}</span>
          <span class="readiness-panel__metric-score" :class="item.scoreClass">{{ item.value }}</span>
        </div>
        <div class="readiness-panel__bar">
          <div
            class="readiness-panel__bar-fill"
            :class="item.barClass"
            :style="{ width: item.barWidth }"
          ></div>
        </div>
        <p v-if="item.hint" class="readiness-panel__metric-hint">{{ item.hint }}</p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  level: string
  levelLabel: string
  metrics: Array<{
    label: string
    value: string
    barWidth: string
    barClass: string
    scoreClass?: string
    hint?: string
  }>
}>()

const gradeClass = computed(() => {
  if (props.level === 'A') return 'readiness-panel__grade--green'
  if (props.level === 'B') return 'readiness-panel__grade--blue'
  if (props.level === 'C') return 'readiness-panel__grade--yellow'
  return 'readiness-panel__grade--red'
})
</script>

<style scoped>
.readiness-panel {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.readiness-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.readiness-panel__title {
  margin: 0;
  color: #1e293b;
  font-size: 14px;
  font-weight: 500;
}

.readiness-panel__grade {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.readiness-panel__grade--green { background: #dcfce7; color: #16a34a; }
.readiness-panel__grade--blue { background: #dbeafe; color: #2563eb; }
.readiness-panel__grade--yellow { background: #fef9c3; color: #ca8a04; }
.readiness-panel__grade--red { background: #fee2e2; color: #dc2626; }

.readiness-panel__overall-row,
.readiness-panel__metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #334155;
  font-size: 14px;
}

.readiness-panel__overall-score {
  color: #2563eb;
  font-weight: 500;
}

.readiness-panel__bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #f1f5f9;
}

.readiness-panel__bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.readiness-panel__bar-fill--blue { background: #3b82f6; }
.readiness-panel__bar-fill--green { background: #22c55e; }
.readiness-panel__bar-fill--yellow { background: #eab308; }
.readiness-panel__bar-fill--red { background: #ef4444; }

.readiness-panel__divider {
  height: 1px;
  margin: 12px 0;
  background: #e2e8f0;
}

.readiness-panel__metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.readiness-panel__metric-score {
  font-weight: 500;
}

.readiness-panel__metric-score.is-green { color: #16a34a; }
.readiness-panel__metric-score.is-yellow { color: #ca8a04; }
.readiness-panel__metric-score.is-red { color: #dc2626; }

.readiness-panel__metric-hint {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}
</style>
