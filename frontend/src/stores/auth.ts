import { defineStore } from 'pinia'

const STORAGE_KEY = 'currentUser'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUser: localStorage.getItem(STORAGE_KEY) ?? '',
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.currentUser),
    displayName: (state) => (state.currentUser ? state.currentUser.split('@')[0] : ''),
  },
  actions: {
    login(email: string) {
      this.currentUser = email.trim()
      localStorage.setItem(STORAGE_KEY, this.currentUser)
    },
    logout() {
      this.currentUser = ''
      localStorage.removeItem(STORAGE_KEY)
    },
    hydrate() {
      this.currentUser = localStorage.getItem(STORAGE_KEY) ?? ''
    },
  },
})
