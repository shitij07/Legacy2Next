import { AIResponseCard } from '../common/AIResponseCard'
import type { AIResponse } from '@/lib/types'

interface ModernizationSectionProps {
  onGenerate: () => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: () => void
}

export function ModernizationSection({
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: ModernizationSectionProps) {
  return (
    <AIResponseCard
      title="Modernization Recommendations"
      description="Get actionable recommendations for modernizing the legacy codebase, including technology upgrades and architectural improvements."
      onGenerate={onGenerate}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={onRegenerate}
    />
  )
}
