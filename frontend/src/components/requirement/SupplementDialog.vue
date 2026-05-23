<template>
  <el-dialog class="opc-dialog" :model-value="modelValue" title="需求补充" width="560px" @close="$emit('update:modelValue', false)">
    <div class="dialog-copy">
      <p>建议继续补充业务目标、实施边界、关键接口与异常场景，以提升需求完整度与后续方案质量。</p>
      <el-input
        :model-value="notes"
        type="textarea"
        :rows="6"
        placeholder="请输入本次补充说明、补充背景或新增约束"
        @update:model-value="$emit('update:notes', $event)"
      />
    </div>
    <template #footer>
      <el-button class="opc-secondary-button" @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button class="opc-primary-button" type="primary" @click="$emit('confirm')">保存补充</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps<{ modelValue: boolean; notes: string }>()
defineEmits<{
  'update:modelValue': [boolean]
  'update:notes': [string]
  confirm: []
}>()
</script>

<style scoped>
.dialog-copy {
  display: grid;
  gap: 14px;
}

.dialog-copy p {
  margin: 0;
  color: var(--opc-text-secondary);
  font-size: 14px;
  line-height: 1.85;
}
</style>
