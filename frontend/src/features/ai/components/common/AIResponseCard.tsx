import { Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { MarkdownViewer } from './MarkdownViewer'
import { LoadingSkeleton } from './LoadingSkeleton'
import { ErrorCard } from './ErrorCard'
import { GenerateButton } from './GenerateButton'
import { CopyButton } from './CopyButton'
import { PromptHeader } from './PromptHeader'
import { SectionCard, CardHeader, CardContent } from './SectionCard'
import type { AIResponse } from '@/lib/types'

interface AIResponseCardProps {
  title: string
  description: string
  onGenerate: () => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: () => void
  children?: React.ReactNode
}

export function AIResponseCard({
  title,
  description,
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
  children,
}: AIResponseCardProps) {
  const showResult = response || isGenerating || error || children

  return (
    <SectionCard>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <PromptHeader title={title} description={description} />
        {!response && !isGenerating && !error && !children && (
          <GenerateButton onClick={onGenerate} isLoading={isGenerating} />
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {showResult && (
          <div className="space-y-4">
            {children}

            {isGenerating && <LoadingSkeleton />}

            {error && <ErrorCard message={error.message} />}

            {response && (
              <>
                <div className="flex items-center gap-2">
                  <Badge variant="info" size="sm" className="gap-1">
                    <Sparkles className="h-3 w-3" aria-hidden="true" />
                    {response.model}
                  </Badge>
                </div>
                <div className="min-w-0">
                  <MarkdownViewer content={response.content} />
                </div>
                <div className="flex items-center gap-2">
                  <CopyButton text={response.content} />
                  {onRegenerate && (
                    <GenerateButton
                      onClick={onRegenerate}
                      isLoading={isGenerating}
                      label="Regenerate"
                    />
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </CardContent>
    </SectionCard>
  )
}
