<template>
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" class="tab-icon">
    <template v-if="name === 'layout-dashboard'">
      <rect x="3" y="3" width="7" height="9" rx="1" stroke="currentColor" stroke-width="2" />
      <rect x="14" y="3" width="7" height="5" rx="1" stroke="currentColor" stroke-width="2" />
      <rect x="14" y="12" width="7" height="9" rx="1" stroke="currentColor" stroke-width="2" />
      <rect x="3" y="16" width="7" height="5" rx="1" stroke="currentColor" stroke-width="2" />
    </template>
    <template v-else-if="name === 'file-text'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" stroke="currentColor" stroke-width="2" />
      <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </template>
    <template v-else-if="name === 'trending-up'">
      <path d="m22 7-8.5 8.5-5-5L2 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M16 7h6v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </template>
    <template v-else-if="name === 'search-check'">
      <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" />
      <path d="m21 21-4.3-4.3M11 8v6M8 11h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </template>
    <template v-else-if="name === 'file-spreadsheet'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" stroke="currentColor" stroke-width="2" />
      <path d="M14 2v6h6M8 13h8M8 17h8M8 9h2" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </template>
    <template v-else-if="name === 'dollar-sign'">
      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </template>
    <template v-else-if="name === 'code'">
      <path d="m16 18 6-6-6-6M8 6l-6 6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </template>
    <template v-else-if="name === 'settings'">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </template>
  </svg>
</template>

<script setup lang="ts">
defineProps<{ name: string }>()
</script>

<style scoped>
.tab-icon {
  width: 20px;
  height: 20px;
}
</style>
