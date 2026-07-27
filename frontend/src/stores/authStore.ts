import { create } from 'zustand'
import type { User } from '@/lib/types'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  isInitialized: boolean
}

export const useAuthStore = create<AuthState>(() => ({
  token: null,
  user: null,
  isAuthenticated: false,
  isInitialized: false,
}))
