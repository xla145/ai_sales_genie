import { defineStore } from 'pinia'
import { authService } from '@/services/modules/auth.service'

const USER_KEY = 'currentUser'
const TOKEN_KEY = 'authToken'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUser: localStorage.getItem(USER_KEY) ?? '',
    token: localStorage.getItem(TOKEN_KEY) ?? '',
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.currentUser),
    displayName: (state) => (state.currentUser ? state.currentUser.split('@')[0] : ''),
  },
  actions: {
    async login(email: string, password: string) {
      const { data } = await authService.login({ email, password })
      this.currentUser = data.email
      this.token = data.token
      localStorage.setItem(USER_KEY, this.currentUser)
      localStorage.setItem(TOKEN_KEY, this.token)
    },
    async register(email: string, password: string, displayName?: string) {
      const { data } = await authService.register({ email, password, display_name: displayName })
      this.currentUser = data.email
      this.token = data.token
      localStorage.setItem(USER_KEY, this.currentUser)
      localStorage.setItem(TOKEN_KEY, this.token)
    },
    async logout() {
      try {
        await authService.logout()
      }
      finally {
        this.currentUser = ''
        this.token = ''
        localStorage.removeItem(USER_KEY)
        localStorage.removeItem(TOKEN_KEY)
      }
    },
    hydrate() {
      this.currentUser = localStorage.getItem(USER_KEY) ?? ''
      this.token = localStorage.getItem(TOKEN_KEY) ?? ''
    },
  },
})

export const getAuthToken = () => localStorage.getItem(TOKEN_KEY) ?? ''
