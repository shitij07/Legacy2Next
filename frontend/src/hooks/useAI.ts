import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  generateSummary,
  generateArchitecture,
  generateTechnicalDebt,
  generateModernization,
  generateFileExplanation,
  generateModuleExplanation,
} from '@/services/ai'

export function useGenerateSummary() {
  return useMutation({
    mutationFn: (analysisId: number) => generateSummary(analysisId),
    onSuccess: () => toast.success('Project summary generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate summary'),
    retry: 1,
  })
}

export function useGenerateArchitecture() {
  return useMutation({
    mutationFn: (analysisId: number) => generateArchitecture(analysisId),
    onSuccess: () => toast.success('Architecture analysis generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate architecture analysis'),
    retry: 1,
  })
}

export function useGenerateTechnicalDebt() {
  return useMutation({
    mutationFn: (analysisId: number) => generateTechnicalDebt(analysisId),
    onSuccess: () => toast.success('Technical debt report generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate technical debt report'),
    retry: 1,
  })
}

export function useGenerateModernization() {
  return useMutation({
    mutationFn: (analysisId: number) => generateModernization(analysisId),
    onSuccess: () => toast.success('Modernization recommendations generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate modernization recommendations'),
    retry: 1,
  })
}

export function useGenerateFileExplanation() {
  return useMutation({
    mutationFn: ({ analysisId, fileId }: { analysisId: number; fileId: number }) =>
      generateFileExplanation(analysisId, fileId),
    onSuccess: () => toast.success('File explanation generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate file explanation'),
    retry: 1,
  })
}

export function useGenerateModuleExplanation() {
  return useMutation({
    mutationFn: ({ analysisId, modulePath }: { analysisId: number; modulePath: string }) =>
      generateModuleExplanation(analysisId, modulePath),
    onSuccess: () => toast.success('Module explanation generated'),
    onError: (err: Error) => toast.error(err.message ?? 'Failed to generate module explanation'),
    retry: 1,
  })
}
