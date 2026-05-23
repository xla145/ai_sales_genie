<template>
  <div class="pending-editor">
    <section class="pending-editor__card">
      <label class="pending-editor__label">未明确信息</label>
      <el-input :model-value="unknownInfo" type="textarea" :rows="4" placeholder="列出需要进一步明确的信息点" @update:model-value="$emit('update:unknownInfo', $event)" />
    </section>
    <section class="pending-editor__card">
      <label class="pending-editor__label">关键假设</label>
      <el-input :model-value="assumptions" type="textarea" :rows="4" placeholder="当前基于哪些假设进行设计？这些假设需要验证" @update:model-value="$emit('update:assumptions', $event)" />
    </section>
    <section class="pending-editor__checklist">
      <label v-for="item in items" :key="item.title" class="pending-editor__item">
        <el-checkbox v-model="item.checked" />
        <div>
          <h4 class="pending-editor__title">{{ item.title }}</h4>
          <p class="pending-editor__text">{{ item.text }}</p>
        </div>
      </label>
    </section>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ title: string; text: string; checked: boolean }>
  unknownInfo: string
  assumptions: string
}>()

defineEmits<{
  'update:unknownInfo': [value: string]
  'update:assumptions': [value: string]
}>()
</script>

<style scoped>
.pending-editor {
  display: grid;
  gap: 16px;
}

.pending-editor__card,
.pending-editor__item {
  padding: 18px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid var(--opc-border);
}

.pending-editor__label {
  display: block;
  margin-bottom: 10px;
  color: var(--opc-text);
  font-size: 14px;
  font-weight: 700;
}

.pending-editor__checklist {
  display: grid;
  gap: 12px;
}

.pending-editor__item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.pending-editor__title {
  margin: 0 0 6px;
  color: var(--opc-text);
  font-size: 15px;
}

.pending-editor__text {
  margin: 0;
  color: var(--opc-text-secondary);
  font-size: 13px;
  line-height: 1.8;
}
</style>
