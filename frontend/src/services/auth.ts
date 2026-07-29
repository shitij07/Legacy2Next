import { client } from './client'
import type { User } from '@/lib/types'

interface LoginRequest {
  email: string
  password: string
}

interface RegisterRequest {
  email: string
  password: string
  name: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  return client.post('auth/login', { json: data }).json()
}

export async function register(data: RegisterRequest): Promise<User> {
  return client.post('auth/register', { json: data }).json()
}

export async function getCurrentUser(): Promise<User> {
  return client.get('auth/me').json()
}
