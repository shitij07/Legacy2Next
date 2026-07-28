import { useState } from 'react'
import { FileIcon, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from '@/components/ui/dialog'
import { useAnalysisFiles } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'
import { AIResponseCard } from '../common/AIResponseCard'
import { LoadingSkeleton } from '../common/LoadingSkeleton'
import type { AIResponse, AnalysisFile } from '@/lib/types'

interface FileExplanationSectionProps {
  analysisId: number
  onGenerate: (fileId: number) => void
  isGenerating: boolean
  response: AIResponse | null
  error: Error | null
  onRegenerate: (fileId: number) => void
}

export function FileExplanationSection({
  analysisId,
  onGenerate,
  isGenerating,
  response,
  error,
  onRegenerate,
}: FileExplanationSectionProps) {
  const [selectedFile, setSelectedFile] = useState<AnalysisFile | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [filePage, setFilePage] = useState(1)
  const debouncedSearch = useDebounce(search, 300)

  const { data: filesData, isLoading: filesLoading } = useAnalysisFiles(analysisId, {
    page: filePage,
    size: 20,
    search: debouncedSearch || undefined,
  })

  const files = filesData?.items ?? []
  const totalPages = filesData?.pages ?? 1

  const handleSelectFile = (file: AnalysisFile) => {
    setSelectedFile(file)
    setDialogOpen(false)
    onGenerate(file.id)
  }

  const handleRegenerate = () => {
    if (selectedFile) onRegenerate(selectedFile.id)
  }

  return (
    <AIResponseCard
      title="File Explanation"
      description="Select a file from the codebase to get an AI-generated explanation of its purpose and functionality."
      onGenerate={() => setDialogOpen(true)}
      isGenerating={isGenerating}
      response={response}
      error={error}
      onRegenerate={handleRegenerate}
    >
      <div className="mb-4">
        {!response && !isGenerating && !error && (
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <FileIcon className="h-4 w-4" aria-hidden="true" />
                {selectedFile ? selectedFile.file_name : 'Choose File...'}
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>Select a File</DialogTitle>
                <DialogDescription>
                  Choose a file from the analysis to explain.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
                  <Input
                    placeholder="Search files..."
                    value={search}
                    onChange={(e) => { setSearch(e.target.value); setFilePage(1) }}
                    className="pl-9"
                    aria-label="Search files"
                  />
                </div>
                {filesLoading ? (
                  <LoadingSkeleton />
                ) : (
                  <div className="max-h-72 space-y-1 overflow-y-auto">
                    {files.map((file) => (
                      <button
                        key={file.id}
                        onClick={() => handleSelectFile(file)}
                        className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/30"
                        aria-label={`Explain file ${file.file_name}`}
                      >
                        <FileIcon className="h-4 w-4 shrink-0 text-neutral-500" aria-hidden="true" />
                        <div className="min-w-0 flex-1">
                          <p className="truncate font-medium text-neutral-900">{file.file_name}</p>
                          <p className="truncate text-xs text-neutral-500">{file.relative_path}</p>
                        </div>
                        {file.language && (
                          <Badge variant="info" size="sm">{file.language}</Badge>
                        )}
                      </button>
                    ))}
                    {files.length === 0 && (
                      <p className="py-4 text-center text-sm text-neutral-500">No files found</p>
                    )}
                  </div>
                )}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFilePage((p) => Math.max(1, p - 1))}
                      disabled={filePage <= 1}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-neutral-600">
                      Page {filePage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFilePage((p) => Math.min(totalPages, p + 1))}
                      disabled={filePage >= totalPages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}
        {selectedFile && (isGenerating || response) && (
          <div className="flex items-center gap-2 rounded-md bg-neutral-100 px-3 py-2">
            <FileIcon className="h-4 w-4 text-neutral-500" aria-hidden="true" />
            <span className="text-sm font-medium text-neutral-800">{selectedFile.file_name}</span>
            <span className="text-xs text-neutral-500">{selectedFile.relative_path}</span>
          </div>
        )}
      </div>
    </AIResponseCard>
  )
}
