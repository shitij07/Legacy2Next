import { AIResponseCard } from '../common/AIResponseCard'
import type { AIResponse } from '@/lib/types'

interface ArchitectureSectionProps {
  onGenerate: () => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: () => void
}

export function ArchitectureSection({
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: ArchitectureSectionProps) {
  return (
    <AIResponseCard
      title="Architecture Analysis"
      description="Understand the software architecture of the codebase, including component relationships and design patterns."
      onGenerate={onGenerate}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={onRegenerate}
    />
  )
}
