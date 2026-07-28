import { AIResponseCard } from '../common/AIResponseCard'
import type { AIResponse } from '@/lib/types'

interface SummarySectionProps {
  onGenerate: () => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: () => void
}

export function SummarySection({
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: SummarySectionProps) {
  return (
    <AIResponseCard
      title="Project Summary"
      description="Get an AI-generated overview of the analysed codebase, including its purpose, structure, and key characteristics."
      onGenerate={onGenerate}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={onRegenerate}
    />
  )
}
