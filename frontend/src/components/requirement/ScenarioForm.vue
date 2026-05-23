<template>
  <div class="scenario-list">
    <section v-for="item in items" :key="item.key" class="scenario-list__card">
      <div class="scenario-list__head">
        <h4 class="scenario-list__title">{{ item.title }}</h4>
        <button class="scenario-list__delete" type="button" @click="$emit('remove', item.key)">删除</button>
      </div>
      <div class="scenario-list__fields">
        <div>
          <label class="scenario-list__label">场景描述</label>
          <el-input v-model="item.description" type="textarea" :rows="2" placeholder="描述该场景的具体情况" />
        </div>
        <div>
          <label class="scenario-list__label">场景流程</label>
          <el-input v-model="item.flow" type="textarea" :rows="3" placeholder="该场景的业务流程步骤" />
        </div>
      </div>
    </section>
    <button class="scenario-list__add" type="button" @click="$emit('add')">+ 添加场景</button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ key: string; title: string; description: string; flow: string }>
}>()

defineEmits<{
  add: []
  remove: [key: string]
}>()
</script>

<style scoped>
.scenario-list {
  display: grid;
  gap: 16px;
}

.scenario-list__card {
  padding: 18px;
  border: 1px solid var(--opc-border);
  border-radius: 18px;
  background: #fff;
}

.scenario-list__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.scenario-list__title,
.scenario-list__label {
  color: var(--opc-text);
}

.scenario-list__title {
  margin: 0;
  font-size: 15px;
}

.scenario-list__label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
}

.scenario-list__fields {
  display: grid;
  gap: 14px;
}

.scenario-list__delete {
  border: none;
  background: transparent;
  color: #dc2626;
  cursor: pointer;
}

.scenario-list__add {
  min-height: 44px;
  border: 2px dashed var(--opc-border-strong);
  border-radius: 16px;
  background: transparent;
  color: var(--opc-text-secondary);
  font-weight: 700;
  cursor: pointer;
}
</style>