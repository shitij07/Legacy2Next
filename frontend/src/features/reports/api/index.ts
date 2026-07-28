import { client } from '@/services/client'
import type { ReportResponse, ReportListResponse, ReportCreatePayload, ReportListParams } from '../types'

function cleanParams(params: object): Record<string, string> {
  const cleaned: Record<string, string> = {}
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = String(value)
    }
  }
  return cleaned
}

export async function generateReport(data: ReportCreatePayload): Promise<ReportResponse> {
  return client.post('reports', { json: data }).json()
}

export async function getReports(params: ReportListParams): Promise<ReportListResponse> {
  return client.get('reports', { searchParams: cleanParams(params) }).json()
}

export async function getReport(reportId: number): Promise<ReportResponse> {
  return client.get(`reports/${reportId}`).json()
}

export async function deleteReport(reportId: number): Promise<void> {
  await client.delete(`reports/${reportId}`)
}
