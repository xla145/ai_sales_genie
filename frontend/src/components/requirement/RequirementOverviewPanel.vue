<template>
  <article class="content-panel">
    <div class="content-panel__head">
      <div class="content-panel__head-left">
        <div class="content-panel__icon" :class="`content-panel__icon--${iconColor}`">
          <slot name="icon" />
        </div>
        <div>
          <h2 class="content-panel__title">{{ title }}</h2>
          <p v-if="subtitle" class="content-panel__subtitle">{{ subtitle }}</p>
        </div>
      </div>
      <slot name="actions" />
    </div>
    <slot />
  </article>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    iconColor?: 'blue' | 'purple' | 'green' | 'indigo' | 'orange' | 'yellow'
  }>(),
  { iconColor: 'blue' },
)
</script>

<style scoped>
.content-panel {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.content-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.content-panel__head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content-panel__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: #fff;
}

.content-panel__icon--blue { background: #2563eb; }
.content-panel__icon--purple { background: #9333ea; }
.content-panel__icon--green { background: #16a34a; }
.content-panel__icon--indigo { background: #4f46e5; }
.content-panel__icon--orange { background: #ea580c; }
.content-panel__icon--yellow { background: #ca8a04; }

.content-panel__title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 500;
}

.content-panel__subtitle {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 12px;
}
</style>
