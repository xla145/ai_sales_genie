<template>
  <div class="function-sections">
    <section v-for="item in items" :key="item.key" class="function-sections__card">
      <h4 class="function-sections__title">{{ item.title }}</h4>
      <div class="function-sections__fields">
        <div v-for="field in item.fields" :key="field.label">
          <label class="function-sections__label">{{ field.label }}</label>
          <template v-if="field.type === 'textarea'">
            <el-input v-model="field.value" type="textarea" :rows="field.rows ?? 3" :placeholder="field.placeholder" />
          </template>
          <template v-else>
            <el-input v-model="field.value" :placeholder="field.placeholder" />
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{
    key: string
    title: string
    fields: Array<{ label: string; value: string; placeholder?: string; type?: 'text' | 'textarea'; rows?: number }>
  }>
}>()
</script>

<style scoped>
.function-sections {
  display: grid;
  gap: 16px;
}

.function-sections__card {
  padding: 18px;
  border: 1px solid var(--opc-border);
  border-radius: 18px;
  background: #fff;
}

.function-sections__title {
  margin: 0 0 14px;
  color: var(--opc-text);
  font-size: 15px;
}

.function-sections__fields {
  display: grid;
  gap: 14px;
}

.function-sections__label {
  display: block;
  margin-bottom: 8px;
  color: var(--opc-text);
  font-size: 13px;
  font-weight: 700;
}
</style>