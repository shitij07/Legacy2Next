import ky from 'ky'
import { env } from '@/config/env'

export const client = ky.create({
  prefixUrl: env.API_BASE_URL,
  timeout: 30_000,
  retry: 1,
  headers: {
    'Content-Type': 'application/json',
  },
})
