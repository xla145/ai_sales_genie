<template>
  <article
    class="project-card"
    :class="{
      'project-card--new': isNew,
      'project-card--fading': isFading,
    }"
    @click="$emit('open')"
  >
    <div class="project-card__glow" aria-hidden="true"></div>

    <div class="project-card__head">
      <div class="project-card__copy">
        <h3 class="project-card__title">{{ project.name }}</h3>
        <p class="project-card__description">{{ project.description || '暂无描述' }}</p>
        <div class="project-card__chips">
          <div v-if="clientInfo" class="project-card__chip project-card__chip--client">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 6h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M10 10h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M10 14h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M10 18h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>{{ clientInfo }}</span>
          </div>
          <div v-if="locationText" class="project-card__chip project-card__chip--location">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>{{ locationText }}</span>
          </div>
        </div>
      </div>

      <div class="project-card__actions">
        <button class="project-card__icon-button" type="button" aria-label="编辑项目" @click.stop="$emit('edit')">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="m15 5 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="project-card__icon-button project-card__icon-button--danger" type="button" aria-label="删除项目" @click.stop="$emit('delete')">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 6h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="project-card__footer">
      <span class="project-card__date">{{ createdAtText }}</span>
      <button class="project-card__enter" type="button" @click.stop="$emit('open')">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 10h20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        进入项目
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project } from '@/types/api'

const props = withDefaults(
  defineProps<{
    project: Project
    isNew?: boolean
    isFading?: boolean
  }>(),
  {
    isNew: false,
    isFading: false,
  },
)

defineEmits<{ open: []; edit: []; delete: [] }>()

const projectMeta = computed(() => (props.project.config ?? {}) as Record<string, unknown>)
const clientInfo = computed(() => String(projectMeta.value.clientInfo ?? ''))
const province = computed(() => String(projectMeta.value.province ?? ''))
const city = computed(() => String(projectMeta.value.city ?? ''))
const locationText = computed(() => [province.value, city.value].filter(Boolean).join(' · '))
const createdAtText = computed(() =>
  new Date(props.project.created_at).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }),
)
</script>

<style scoped>
.project-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.3s ease;
}

.project-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 20px 25px rgba(37, 99, 235, 0.1);
}

.project-card--new {
  animation: project-card-slide-in 0.4s ease-out;
}

.project-card--fading {
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.project-card__glow {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 0;
  width: 128px;
  height: 128px;
  border-radius: 999px;
  background: linear-gradient(135deg, #eff6ff, transparent);
  filter: blur(32px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.project-card:hover .project-card__glow {
  opacity: 1;
}

.project-card__head,
.project-card__copy,
.project-card__footer {
  position: relative;
  z-index: 1;
}

.project-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.project-card__copy {
  flex: 1;
  min-width: 0;
}

.project-card__title {
  margin: 0 0 8px;
  overflow: hidden;
  color: #0f172a;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.project-card:hover .project-card__title {
  color: #2563eb;
}

.project-card__description {
  display: -webkit-box;
  margin: 0 0 12px;
  overflow: hidden;
  color: #475569;
  font-size: 14px;
  line-height: 1.625;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.project-card__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.project-card__chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
}

.project-card__chip svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.project-card__chip--client {
  border: 1px solid #dbeafe;
  background: linear-gradient(135deg, #eff6ff, rgba(219, 234, 254, 0.5));
  color: #334155;
  font-weight: 500;
}

.project-card__chip--client svg {
  color: #2563eb;
}

.project-card__chip--location {
  border: 1px solid #f1f5f9;
  background: #f8fafc;
  color: #334155;
}

.project-card__chip--location svg {
  color: #64748b;
}

.project-card__actions {
  display: flex;
  gap: 6px;
  margin-left: 12px;
}

.project-card__icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.project-card__icon-button svg {
  width: 16px;
  height: 16px;
}

.project-card__icon-button:hover {
  background: #f1f5f9;
  color: #334155;
}

.project-card__icon-button--danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.project-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.project-card__date {
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
}

.project-card__enter {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #2563eb, #1d4ed8);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  font-weight: 500;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.project-card__enter svg {
  width: 14px;
  height: 14px;
}

.project-card__enter:hover {
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  transform: scale(1.05);
}

@keyframes project-card-slide-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
