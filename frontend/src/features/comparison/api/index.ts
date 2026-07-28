import { client } from '@/services/client'
import type { ComparisonResponse, ComparisonListResponse, ComparisonCreatePayload, ComparisonListParams } from '../types'

function cleanParams(params: object): Record<string, string> {
  const cleaned: Record<string, string> = {}
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = String(value)
    }
  }
  return cleaned
}

export async function compareAnalyses(data: ComparisonCreatePayload): Promise<ComparisonResponse> {
  return client.post('comparison', { json: data }).json()
}

export async function getComparison(comparisonId: number): Promise<ComparisonResponse> {
  return client.get(`comparison/${comparisonId}`).json()
}

export async function getComparisonHistory(params: ComparisonListParams): Promise<ComparisonListResponse> {
  return client.get(`comparison/project/${params.project_id}`, { searchParams: cleanParams({ page: params.page, size: params.size }) }).json()
}

export async function deleteComparison(comparisonId: number): Promise<void> {
  await client.delete(`comparison/${comparisonId}`)
}
