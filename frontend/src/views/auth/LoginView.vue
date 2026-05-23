<template>
  <div class="login-page">
    <div class="login-page__bg" aria-hidden="true">
      <span class="login-page__blob login-page__blob--blue"></span>
      <span class="login-page__blob login-page__blob--purple"></span>
      <span class="login-page__blob login-page__blob--pink"></span>
    </div>

    <div class="login-page__grid">
      <section class="login-page__brand">
        <div class="login-page__brand-head">
          <div class="login-page__logo">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h1 class="login-page__brand-title">OPC 规范支持中心</h1>
        </div>
        <p class="login-page__brand-subtitle">智能售前协作平台</p>
        <p class="login-page__brand-desc">专为售前团队打造的智能化项目管理系统，助力快速响应客户需求、高效产出方案文档</p>

        <div class="login-page__features">
          <article v-for="feature in features" :key="feature.title" class="login-page__feature">
            <div class="login-page__feature-icon" :class="`login-page__feature-icon--${feature.color}`">{{ feature.icon }}</div>
            <div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.desc }}</p>
            </div>
          </article>
        </div>

        <p class="login-page__copyright">© 2026 三坨理想泥. All rights reserved.</p>
      </section>

      <section class="login-page__panel">
        <div class="login-page__card">
          <div class="login-page__mobile-brand">
            <div class="login-page__logo login-page__logo--small">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div>
              <h2>OPC</h2>
              <p>智能售前协作平台</p>
            </div>
          </div>

          <div class="login-page__card-head">
            <h2>{{ isRegisterMode ? '创建账户' : '欢迎回来' }}</h2>
            <p>{{ isRegisterMode ? '注册后自动登录' : '登录您的账户以继续' }}</p>
          </div>

          <form class="login-page__form" @submit.prevent="handleSubmit">
            <label class="login-page__field">
              <span>邮箱地址</span>
              <input v-model="email" type="email" placeholder="your@email.com" required />
            </label>

            <label class="login-page__field">
              <span class="login-page__field-row">
                <span>密码</span>
                <button type="button">忘记密码？</button>
              </span>
              <input v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required />
            </label>

            <label v-if="isRegisterMode" class="login-page__field">
              <span>显示名称</span>
              <input v-model="displayName" type="text" placeholder="请输入显示名称（可选）" />
            </label>

            <label class="login-page__remember">
              <input v-model="remember" type="checkbox" />
              <span>保持登录状态</span>
            </label>

            <button class="login-page__submit" type="submit" :disabled="loading">
              {{ loading ? (isRegisterMode ? '注册中...' : '登录中...') : (isRegisterMode ? '注册并登录' : '登录') }}
            </button>
          </form>

          <!-- <div class="login-page__divider"><span>或使用以下方式登录</span></div>

          <div class="login-page__social">
            <button type="button">Facebook</button>
            <button type="button">Google</button>
          </div> -->

          <p class="login-page__register">
            {{ isRegisterMode ? '已有账户？' : '还没有账户？' }}
            <button type="button" @click="toggleRegisterMode">{{ isRegisterMode ? '去登录' : '立即注册' }}</button>
          </p>
        </div>

        <div class="login-page__links">
          <a href="#">帮助中心</a>
          <span>·</span>
          <a href="#">隐私政策</a>
          <span>·</span>
          <a href="#">服务条款</a>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const displayName = ref('')
const remember = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const isRegisterMode = ref(false)

const features = [
  { icon: '✓', title: '智能需求分析', desc: 'AI 辅助需求理解与风险识别', color: 'blue' },
  { icon: '盾', title: '多团队协作', desc: '8 大团队模块无缝协作', color: 'purple' },
  { icon: '⚡', title: '高效文档产出', desc: '自动生成 PRD、PPT、原型', color: 'green' },
]

const toggleRegisterMode = () => {
  isRegisterMode.value = !isRegisterMode.value
}

const handleSubmit = async () => {
  if (!email.value.trim() || !password.value) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  loading.value = true
  try {
    if (isRegisterMode.value) {
      await authStore.register(email.value.trim(), password.value, displayName.value.trim())
      ElMessage.success('注册成功，已自动登录')
    }
    else {
      await authStore.login(email.value.trim(), password.value)
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/projects'
    router.replace(redirect)
  }
  catch (error) {
    ElMessage.error(error instanceof Error ? error.message : isRegisterMode.value ? '注册失败' : '登录失败')
  }
  finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, #eff6ff, #fff, #faf5ff);
}

.login-page__bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.login-page__blob {
  position: absolute;
  width: 288px;
  height: 288px;
  border-radius: 999px;
  filter: blur(64px);
  opacity: 0.2;
}

.login-page__blob--blue {
  top: 80px;
  left: 40px;
  background: #93c5fd;
}

.login-page__blob--purple {
  top: 160px;
  right: 40px;
  background: #c4b5fd;
}

.login-page__blob--pink {
  bottom: -80px;
  left: 50%;
  background: #f9a8d4;
}

.login-page__grid {
  position: relative;
  z-index: 1;
  display: grid;
  width: 100%;
  max-width: 1152px;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.login-page__brand {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 32px;
}

.login-page__brand-head,
.login-page__mobile-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.login-page__logo {
  display: inline-flex;
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
  color: #fff;
}

.login-page__logo svg {
  width: 32px;
  height: 32px;
}

.login-page__logo--small {
  padding: 8px;
}

.login-page__logo--small svg {
  width: 24px;
  height: 24px;
}

.login-page__brand-title {
  margin: 0;
  background: linear-gradient(90deg, #2563eb, #9333ea);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 30px;
  font-weight: 700;
}

.login-page__brand-subtitle {
  margin: 0;
  color: #475569;
  font-size: 20px;
}

.login-page__brand-desc {
  margin: 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.625;
}

.login-page__features {
  display: grid;
  gap: 16px;
}

.login-page__feature {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(4px);
}

.login-page__feature h3 {
  margin: 0 0 4px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}

.login-page__feature p {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

.login-page__feature-icon {
  display: inline-flex;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.login-page__feature-icon--blue {
  background: #dbeafe;
  color: #2563eb;
}

.login-page__feature-icon--purple {
  background: #ede9fe;
  color: #7c3aed;
}

.login-page__feature-icon--green {
  background: #dcfce7;
  color: #16a34a;
}

.login-page__copyright {
  margin: 0;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 12px;
}

.login-page__panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.login-page__card {
  width: 100%;
  max-width: 448px;
  padding: 32px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  box-shadow: 0 25px 50px rgba(15, 23, 42, 0.15);
}

.login-page__mobile-brand {
  display: flex;
  margin-bottom: 32px;
}

.login-page__mobile-brand h2 {
  margin: 0;
  font-size: 24px;
}

.login-page__mobile-brand p {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

.login-page__card-head h2 {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 24px;
  font-weight: 700;
}

.login-page__card-head p {
  margin: 0 0 32px;
  color: #475569;
  font-size: 14px;
}

.login-page__form {
  display: grid;
  gap: 24px;
}

.login-page__field {
  display: grid;
  gap: 8px;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
}

.login-page__field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.login-page__field-row button {
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.login-page__field input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  font: inherit;
}

.login-page__remember {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 14px;
}

.login-page__submit {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #2563eb, #1d4ed8);
  box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

.login-page__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-page__divider {
  position: relative;
  margin: 24px 0;
  text-align: center;
}

.login-page__divider::before {
  content: '';
  position: absolute;
  inset: 50% 0 auto;
  height: 1px;
  background: #e2e8f0;
}

.login-page__divider span {
  position: relative;
  padding: 0 8px;
  background: #fff;
  color: #64748b;
  font-size: 12px;
}

.login-page__social {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.login-page__social button,
.login-page__register button {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  color: #334155;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 500;
}

.login-page__social button {
  padding: 10px;
}

.login-page__register {
  margin: 24px 0 0;
  text-align: center;
  color: #475569;
  font-size: 14px;
}

.login-page__register button {
  margin-left: 4px;
  padding: 0;
  border: none;
  background: transparent;
  color: #2563eb;
  font-weight: 600;
}

.login-page__links {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  color: #64748b;
  font-size: 12px;
}

.login-page__links a {
  color: inherit;
  text-decoration: none;
}

@media (min-width: 1024px) {
  .login-page__brand {
    display: flex;
  }

  .login-page__mobile-brand {
    display: none;
  }
}
</style>
