<template>
  <div class="risk-editor">
    <section v-for="item in items" :key="item.key" class="risk-editor__card">
      <div class="risk-editor__head">
        <h4 class="risk-editor__title">{{ item.title }}</h4>
        <button class="risk-editor__delete" type="button" @click="$emit('remove', item.key)">删除</button>
      </div>
      <div class="risk-editor__fields">
        <div>
          <label class="risk-editor__label">风险等级</label>
          <el-select v-model="item.level" placeholder="选择风险等级">
            <el-option v-for="level in RISK_LEVEL_OPTIONS" :key="level" :label="level" :value="level" />
          </el-select>
        </div>
        <div>
          <label class="risk-editor__label">风险描述</label>
          <el-input v-model="item.description" type="textarea" :rows="2" placeholder="描述具体的风险" />
        </div>
        <div>
          <label class="risk-editor__label">影响范围</label>
          <el-input v-model="item.impact" placeholder="该风险可能影响的范围" />
        </div>
        <div>
          <label class="risk-editor__label">应对策略</label>
          <el-input v-model="item.strategy" type="textarea" :rows="2" placeholder="如何应对和规避该风险" />
        </div>
      </div>
    </section>
    <button class="risk-editor__add" type="button" @click="$emit('add')">+ 添加风险点</button>
  </div>
</template>

<script setup lang="ts">
import { RISK_LEVEL_OPTIONS } from '@/constants/project'

defineProps<{
  items: Array<{ key: string; title: string; level: string; description: string; impact: string; strategy: string }>
}>()

defineEmits<{
  add: []
  remove: [key: string]
}>()
</script>

<style scoped>
.risk-editor {
  display: grid;
  gap: 16px;
}

.risk-editor__card {
  padding: 18px;
  border: 1px solid #fdba74;
  border-radius: 18px;
  background: #fff7ed;
}

.risk-editor__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.risk-editor__title,
.risk-editor__label {
  color: var(--opc-text);
}

.risk-editor__title {
  margin: 0;
  font-size: 15px;
}

.risk-editor__label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
}

.risk-editor__fields {
  display: grid;
  gap: 14px;
}

.risk-editor__delete {
  border: none;
  background: transparent;
  color: #dc2626;
  cursor: pointer;
}

.risk-editor__add {
  min-height: 44px;
  border: 2px dashed #fdba74;
  border-radius: 16px;
  background: transparent;
  color: #9a3412;
  font-weight: 700;
  cursor: pointer;
}
</style>