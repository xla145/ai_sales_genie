<template>
  <el-dialog
    class="delete-project-dialog"
    :model-value="modelValue"
    :show-close="false"
    width="448px"
    destroy-on-close
    align-center
    @close="close"
  >
    <template #header>
      <div class="delete-project-dialog__header">
        <div class="delete-project-dialog__title-wrap">
          <div class="delete-project-dialog__icon">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 9v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h2 class="delete-project-dialog__title">确认删除</h2>
        </div>
        <button class="delete-project-dialog__close" type="button" aria-label="关闭" @click="close">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="m6 6 12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </template>

    <p class="delete-project-dialog__message">
      确定要删除项目 <span class="delete-project-dialog__name">"{{ projectName }}"</span> 吗？
      <br />
      <span class="delete-project-dialog__warning">此操作无法撤销。</span>
    </p>

    <template #footer>
      <div class="delete-project-dialog__footer">
        <button class="delete-project-dialog__cancel" type="button" @click="close">取消</button>
        <button class="delete-project-dialog__confirm" type="button" @click="$emit('confirm')">确认删除</button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps<{ modelValue: boolean; projectName: string }>()
const emit = defineEmits<{ 'update:modelValue': [boolean]; confirm: [] }>()
const close = () => emit('update:modelValue', false)
</script>

<style scoped>
.delete-project-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.delete-project-dialog__title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.delete-project-dialog__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border-radius: 12px;
  background: #fee2e2;
  color: #dc2626;
}

.delete-project-dialog__icon svg {
  width: 24px;
  height: 24px;
}

.delete-project-dialog__title {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
  font-weight: 600;
}

.delete-project-dialog__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.delete-project-dialog__close svg {
  width: 20px;
  height: 20px;
}

.delete-project-dialog__close:hover {
  background: #f1f5f9;
}

.delete-project-dialog__message {
  margin: 0;
  color: #334155;
  font-size: 16px;
  line-height: 1.625;
}

.delete-project-dialog__name {
  color: #0f172a;
  font-weight: 600;
}

.delete-project-dialog__warning {
  color: #dc2626;
  font-size: 14px;
  font-weight: 500;
}

.delete-project-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.delete-project-dialog__cancel,
.delete-project-dialog__confirm {
  padding: 10px 24px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 500;
}

.delete-project-dialog__cancel {
  background: #f1f5f9;
  color: #334155;
}

.delete-project-dialog__cancel:hover {
  background: #e2e8f0;
}

.delete-project-dialog__confirm {
  background: linear-gradient(90deg, #dc2626, #b91c1c);
  box-shadow: 0 10px 15px rgba(220, 38, 38, 0.3);
  color: #fff;
}

.delete-project-dialog__confirm:hover {
  background: linear-gradient(90deg, #b91c1c, #991b1b);
}
</style>

<style>
.delete-project-dialog.el-dialog {
  padding: 0;
  border-radius: 16px;
  overflow: hidden;
}

.delete-project-dialog .el-dialog__header {
  margin: 0;
  padding: 32px 32px 0;
}

.delete-project-dialog .el-dialog__body {
  padding: 24px 32px 0;
}

.delete-project-dialog .el-dialog__footer {
  padding: 0 32px 32px;
}
</style>
