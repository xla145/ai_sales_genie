<template>
  <div v-if="floating" class="assistant-panel assistant-panel--floating">
    <div class="assistant-panel__head">
      <div class="assistant-panel__head-left">
        <span class="assistant-panel__avatar">AI</span>
        <div>
          <h3>AI需求专家</h3>
          <p>在线为您服务</p>
        </div>
      </div>
      <button type="button" class="assistant-panel__close" @click="$emit('close')">×</button>
    </div>
    <div class="assistant-panel__messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="assistant-panel__message"
        :class="`assistant-panel__message--${message.role ?? 'assistant'}`"
      >
        {{ message.text }}
      </div>
    </div>
    <div class="assistant-panel__input">
      <input v-model="inputValue" type="text" placeholder="输入您的问题..." @keydown.enter="sendMessage" />
      <button type="button" @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  floating?: boolean
  messages: Array<{ title?: string; text: string; role?: 'assistant' | 'user' }>
}>()

const emit = defineEmits<{ close: []; send: [string] }>()

const inputValue = ref('')

const sendMessage = () => {
  if (!inputValue.value.trim()) return
  emit('send', inputValue.value)
  inputValue.value = ''
}
</script>

<style scoped>
.assistant-panel--floating {
  position: fixed;
  right: 32px;
  bottom: 96px;
  z-index: 50;
  display: flex;
  width: 384px;
  height: 500px;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
}

.assistant-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #9333ea;
  color: #fff;
}

.assistant-panel__head-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.assistant-panel__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #7e22ce;
  font-size: 12px;
  font-weight: 700;
}

.assistant-panel__head h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.assistant-panel__head p {
  margin: 0;
  color: #e9d5ff;
  font-size: 12px;
}

.assistant-panel__close {
  border: none;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 18px;
}

.assistant-panel__messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assistant-panel__message {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.assistant-panel__message--assistant {
  background: #fff;
  color: #1e293b;
  border: 1px solid #e2e8f0;
}

.assistant-panel__message--user {
  align-self: flex-end;
  background: #9333ea;
  color: #fff;
}

.assistant-panel__input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

.assistant-panel__input input {
  flex: 1;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
}

.assistant-panel__input button {
  padding: 0 16px;
  border: none;
  border-radius: 8px;
  background: #9333ea;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}
</style>
