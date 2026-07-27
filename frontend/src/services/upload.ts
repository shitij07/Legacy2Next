import { client } from './client'
import { useAuthStore } from '@/stores/authStore'
import type { Upload, PaginatedResponse } from '@/lib/types'

export async function getUploads(
  projectId: number,
  page = 1,
  size = 20,
): Promise<PaginatedResponse<Upload>> {
  return client
    .get(`projects/${projectId}/uploads`, {
      searchParams: { page, size },
    })
    .json()
}

export async function getUpload(id: number): Promise<Upload> {
  return client.get(`uploads/${id}`).json()
}

export async function uploadFile(
  projectId: number,
  file: File,
  signal?: AbortSignal,
): Promise<Upload[]> {
  const token = useAuthStore.getState().token
  const formData = new FormData()
  formData.append('files', file)

  return client
    .post(`projects/${projectId}/uploads`, {
      body: formData,
      signal,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      timeout: 600_000,
    })
    .json()
}

export async function deleteUpload(id: number): Promise<void> {
  const token = useAuthStore.getState().token
  await client.delete(`uploads/${id}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
}

export const UPLOAD_CONSTRAINTS = {
  MAX_FILE_SIZE: 50 * 1024 * 1024,
  ALLOWED_EXTENSIONS: ['.zip'],
} as const

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${units[i]}`
}
