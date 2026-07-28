import { client } from './client'
import type { AIResponse } from '@/lib/types'

export async function generateSummary(analysisId: number): Promise<AIResponse> {
  return client.post(`ai/analysis/${analysisId}/summary`).json()
}

export async function generateArchitecture(analysisId: number): Promise<AIResponse> {
  return client.post(`ai/analysis/${analysisId}/architecture`).json()
}

export async function generateTechnicalDebt(analysisId: number): Promise<AIResponse> {
  return client.post(`ai/analysis/${analysisId}/technical-debt`).json()
}

export async function generateModernization(analysisId: number): Promise<AIResponse> {
  return client.post(`ai/analysis/${analysisId}/modernization`).json()
}

export async function generateFileExplanation(
  analysisId: number,
  fileId: number,
): Promise<AIResponse> {
  return client.post(`ai/analysis/${analysisId}/file/${fileId}/explain`).json()
}

export async function generateModuleExplanation(
  analysisId: number,
  modulePath: string,
): Promise<AIResponse> {
  return client
    .post(`ai/analysis/${analysisId}/module`, { json: { module_path: modulePath } })
    .json()
}
