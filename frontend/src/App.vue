<template>
  <div class="app-root">
    <div v-if="useMock" class="app-root__mock-banner">Mock 模式 · 当前使用本地演示数据，无需后端</div>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { useMock } from '@/config/env'
</script>

<style scoped>
.app-root__mock-banner {
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 8px 16px;
  background: #fef3c7;
  border-bottom: 1px solid #fcd34d;
  color: #92400e;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}
</style>
