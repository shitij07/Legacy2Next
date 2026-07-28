import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useProjectAnalyses } from '@/hooks/useAnalysis'
import { ReportFormat } from '../../types'
import type { ReportCreatePayload } from '../../types'

interface GenerateReportDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  projectId: number
  onGenerate: (data: ReportCreatePayload) => void
  isGenerating: boolean
}

export function GenerateReportDialog({
  open,
  onOpenChange,
  projectId,
  onGenerate,
  isGenerating,
}: GenerateReportDialogProps) {
  const { data: analysesData } = useProjectAnalyses(projectId)
  const analyses = analysesData?.items ?? []

  const [title, setTitle] = useState('Analysis Report')
  const [analysisId, setAnalysisId] = useState('')
  const [format, setFormat] = useState<ReportFormat>(ReportFormat.MARKDOWN)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!analysisId) return
    onGenerate({
      project_id: projectId,
      analysis_id: Number(analysisId),
      title,
      format,
    })
  }

  function handleOpenChange(open: boolean) {
    if (!open) {
      setTitle('Analysis Report')
      setAnalysisId('')
      setFormat(ReportFormat.MARKDOWN)
    }
    onOpenChange(open)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Report</DialogTitle>
          <DialogDescription>
            Create a new analysis report. Choose the format and select an analysis.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="report-title">Title</Label>
            <Input
              id="report-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Analysis Report"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="report-analysis">Analysis</Label>
            <Select value={analysisId} onValueChange={setAnalysisId} required>
              <SelectTrigger id="report-analysis" aria-label="Select analysis">
                <SelectValue placeholder="Select an analysis" />
              </SelectTrigger>
              <SelectContent>
                {analyses.map((a) => (
                  <SelectItem key={a.id} value={String(a.id)}>
                    Analysis #{a.id} — {a.status}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="report-format">Format</Label>
            <Select
              value={format}
              onValueChange={(v) => setFormat(v as ReportFormat)}
            >
              <SelectTrigger id="report-format" aria-label="Select format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ReportFormat.MARKDOWN}>Markdown</SelectItem>
                <SelectItem value={ReportFormat.JSON}>JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isGenerating}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isGenerating} disabled={!analysisId}>
              Generate
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
