<template>
  <div class="editable-sections">
    <section v-for="item in items" :key="item.key" class="editable-sections__card">
      <h4 class="editable-sections__title">{{ item.title }}</h4>
      <el-input v-model="item.value" type="textarea" :rows="item.rows ?? 3" :placeholder="item.placeholder" />
    </section>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ key: string; title: string; value: string; placeholder?: string; rows?: number }>
}>()
</script>

<style scoped>
.editable-sections {
  display: grid;
  gap: 16px;
}

.editable-sections__card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--opc-border);
  background: #fff;
}

.editable-sections__title {
  margin: 0 0 12px;
  color: var(--opc-text);
  font-size: 15px;
}
</style>