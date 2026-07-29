import ky from 'ky'
import { env } from '@/config/env'
import { useAuthStore } from '@/stores/authStore'

export const client = ky.create({
  prefixUrl: env.API_BASE_URL,
  timeout: 30_000,
  retry: 1,
  headers: {
    'Content-Type': 'application/json',
  },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = useAuthStore.getState().token
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
  },
})
