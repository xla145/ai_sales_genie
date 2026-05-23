<template>
  <aside class="section-nav">
    <div class="section-nav__head">
      <h3 class="section-nav__title">
        <span class="section-nav__title-bar"></span>
        需求分析与评估
      </h3>
    </div>
    <div class="section-nav__list">
      <button
        v-for="item in items"
        :key="item.key"
        type="button"
        class="section-nav__item"
        :class="{ 'section-nav__item--active': item.key === activeKey }"
        @click="$emit('select', item.key)"
      >
        <span v-if="item.key === activeKey" class="section-nav__active-bar"></span>
        <span class="section-nav__icon" :class="{ 'section-nav__icon--active': item.key === activeKey }">
          <SectionIcon :name="item.iconName" />
        </span>
        <span class="section-nav__content">
          <span class="section-nav__item-title">{{ item.title }}</span>
          <span v-if="item.badge" class="section-nav__badge" :class="`section-nav__badge--${item.badge.type}`">
            {{ item.badge.text }}
          </span>
        </span>
        <span v-if="item.key === activeKey" class="section-nav__check">
          <SectionIcon name="check-circle" />
        </span>
        <span v-else-if="item.badge" class="section-nav__dot" :class="`section-nav__dot--${item.badge.type}`"></span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import SectionIcon from '@/components/icons/SectionIcon.vue'

defineProps<{
  activeKey: string
  items: Array<{
    key: string
    title: string
    iconName: string
    badge?: { text: string; type: 'warning' | 'error' | 'info' }
  }>
}>()

defineEmits<{ select: [string] }>()
</script>

<style scoped>
.section-nav {
  display: flex;
  width: 288px;
  flex-shrink: 0;
  flex-direction: column;
  border-right: 1px solid #e2e8f0;
  background: #fff;
}

.section-nav__head {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.section-nav__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 500;
}

.section-nav__title-bar {
  width: 4px;
  height: 20px;
  border-radius: 999px;
  background: #2563eb;
}

.section-nav__list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.section-nav__item {
  position: relative;
  display: flex;
  width: 100%;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.section-nav__item:hover {
  background: #f8fafc;
}

.section-nav__item--active {
  border-color: #dbeafe;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 500;
}

.section-nav__active-bar {
  position: absolute;
  left: 0;
  top: 50%;
  width: 4px;
  height: 32px;
  border-radius: 0 999px 999px 0;
  background: #2563eb;
  transform: translateY(-50%);
}

.section-nav__icon {
  flex-shrink: 0;
  color: #94a3b8;
}

.section-nav__icon--active {
  color: #2563eb;
}

.section-nav__content {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 2px;
}

.section-nav__item-title {
  color: inherit;
  font-size: 14px;
}

.section-nav__badge {
  font-size: 12px;
  line-height: 1.4;
}

.section-nav__badge--warning { color: #ea580c; }
.section-nav__badge--error { color: #dc2626; }
.section-nav__badge--info { color: #2563eb; }

.section-nav__check {
  flex-shrink: 0;
  color: #22c55e;
}

.section-nav__dot {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  border-radius: 999px;
}

.section-nav__dot--warning { background: #f97316; }
.section-nav__dot--error { background: #ef4444; }
.section-nav__dot--info { background: #3b82f6; }
</style>
