import { useMock } from '@/config/env'
import { mockApi } from '@/mock/client'
import http from '@/services/http'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  display_name?: string
}

export interface LoginResponse {
  token: string
  email: string
  display_name: string
}

export interface UserInfo {
  email: string
  display_name: string
}

const DEMO_EMAIL = 'demo@example.com'
const DEMO_PASSWORD = 'demo123'

export const authService = {
  async login(payload: LoginRequest) {
    if (useMock) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const email = payload.email.trim().toLowerCase()
      if (email !== DEMO_EMAIL || payload.password !== DEMO_PASSWORD) {
        throw new Error('邮箱或密码错误')
      }
      return {
        data: {
          token: `mock_${Date.now()}`,
          email: DEMO_EMAIL,
          display_name: DEMO_EMAIL.split('@')[0],
        } satisfies LoginResponse,
      }
    }
    return http.post<LoginResponse>('/auth/login', payload)
  },

  async register(payload: RegisterRequest) {
    if (useMock) {
      await new Promise((resolve) => setTimeout(resolve, 400))
      const email = payload.email.trim().toLowerCase()
      return {
        data: {
          token: `mock_${Date.now()}`,
          email,
          display_name: payload.display_name?.trim() || email.split('@')[0],
        } satisfies LoginResponse,
      }
    }
    return http.post<LoginResponse>('/auth/register', payload)
  },

  async logout() {
    if (useMock) return
    await http.post('/auth/logout')
  },

  async me() {
    if (useMock) {
      return {
        data: {
          email: DEMO_EMAIL,
          display_name: DEMO_EMAIL.split('@')[0],
        } satisfies UserInfo,
      }
    }
    return http.get<UserInfo>('/auth/me')
  },
}
