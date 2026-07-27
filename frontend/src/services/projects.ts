import { client } from './client'
import type { Project, PaginatedResponse } from '@/lib/types'

export interface CreateProjectPayload {
  name: string
  description?: string
}

export async function getProjects(page = 1, size = 20): Promise<PaginatedResponse<Project>> {
  return client.get('projects', { searchParams: { page, size } }).json()
}

export async function getProject(id: number): Promise<Project> {
  return client.get(`projects/${id}`).json()
}

export async function createProject(data: CreateProjectPayload): Promise<Project> {
  return client.post('projects', { json: data }).json()
}

export async function updateProject(
  id: number,
  data: Partial<CreateProjectPayload>,
): Promise<Project> {
  return client.patch(`projects/${id}`, { json: data }).json()
}

export async function deleteProject(id: number): Promise<void> {
  await client.delete(`projects/${id}`)
}
