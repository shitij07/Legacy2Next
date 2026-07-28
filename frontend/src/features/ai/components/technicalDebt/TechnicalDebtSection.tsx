import { AIResponseCard } from '../common/AIResponseCard'
import type { AIResponse } from '@/lib/types'

interface TechnicalDebtSectionProps {
  onGenerate: () => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: () => void
}

export function TechnicalDebtSection({
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: TechnicalDebtSectionProps) {
  return (
    <AIResponseCard
      title="Technical Debt Assessment"
      description="Identify areas of technical debt, code quality issues, and improvement opportunities."
      onGenerate={onGenerate}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={onRegenerate}
    />
  )
}
