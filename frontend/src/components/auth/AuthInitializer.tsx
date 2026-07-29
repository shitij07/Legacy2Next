import { useEffect, type ReactNode } from 'react'
import { useAuthStore, AUTH_TOKEN_KEY } from '@/stores/authStore'
import { getCurrentUser } from '@/services/auth'

export function AuthInitializer({ children }: { children: ReactNode }) {
  const setToken = useAuthStore((s) => s.setToken)
  const setUser = useAuthStore((s) => s.setUser)

  useEffect(() => {
    const init = async () => {
      const savedToken = localStorage.getItem(AUTH_TOKEN_KEY)

      if (!savedToken) {
        useAuthStore.setState({ isInitialized: true })
        return
      }

      setToken(savedToken)

      try {
        const user = await getCurrentUser()
        setUser(user)
      } catch {
        localStorage.removeItem(AUTH_TOKEN_KEY)
        setToken(null)
        useAuthStore.setState({ isInitialized: true })
      }
    }

    init()
  }, [setToken, setUser])

  return children
}
