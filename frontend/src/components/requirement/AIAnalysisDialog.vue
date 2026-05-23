<template>
  <el-dialog class="opc-dialog" :model-value="modelValue" title="AI 分析结果" width="620px" @close="$emit('update:modelValue', false)">
    <div class="dialog-copy">
      <div v-for="item in items" :key="item.title" class="dialog-copy__item">
        <h4>{{ item.title }}</h4>
        <p>{{ item.text }}</p>
      </div>
    </div>
    <template #footer>
      <el-button class="opc-secondary-button" @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps<{ modelValue: boolean; items: Array<{ title: string; text: string }> }>()
defineEmits<{ 'update:modelValue': [boolean] }>()
</script>

<style scoped>
.dialog-copy {
  display: grid;
  gap: 14px;
}

.dialog-copy__item {
  padding: 14px;
  border-radius: 16px;
  background: var(--opc-surface-soft);
}

.dialog-copy__item h4 {
  margin: 0 0 8px;
  color: var(--opc-text);
}

.dialog-copy__item p {
  margin: 0;
  color: var(--opc-text-secondary);
  font-size: 14px;
  line-height: 1.8;
}
</style>