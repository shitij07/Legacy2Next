import { useState, useRef, useEffect } from 'react'
import { FolderOpen } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { AIResponseCard } from '../common/AIResponseCard'
import type { AIResponse } from '@/lib/types'

interface ModuleExplanationSectionProps {
  onGenerate: (modulePath: string) => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: (modulePath: string) => void
}

export function ModuleExplanationSection({
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: ModuleExplanationSectionProps) {
  const [modulePath, setModulePath] = useState('')
  const [storedPath, setStoredPath] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (response && !isGenerating) {
      setModulePath(storedPath)
    }
  }, [response, isGenerating, storedPath])

  const handleGenerate = () => {
    const path = modulePath.trim()
    if (!path) {
      inputRef.current?.focus()
      return
    }
    setStoredPath(path)
    onGenerate(path)
  }

  const handleRegenerate = () => {
    if (storedPath) onRegenerate(storedPath)
  }

  return (
    <AIResponseCard
      title="Module Explanation"
      description="Enter a directory path to get an AI-generated explanation of that module's structure and purpose."
      onGenerate={handleGenerate}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={handleRegenerate}
    >
      {!response && !isGenerating && !error && (
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <FolderOpen className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
            <Input
              ref={inputRef}
              placeholder="e.g., src/components/ or backend/app/"
              value={modulePath}
              onChange={(e) => setModulePath(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleGenerate()
              }}
              className="pl-9"
              aria-label="Module path"
            />
          </div>
        </div>
      )}
      {storedPath && (isGenerating || response) && (
        <div className="flex items-center gap-2 rounded-md bg-neutral-100 px-3 py-2">
          <FolderOpen className="h-4 w-4 text-neutral-500" aria-hidden="true" />
          <span className="text-sm font-medium text-neutral-800">{storedPath}</span>
        </div>
      )}
    </AIResponseCard>
  )
}
