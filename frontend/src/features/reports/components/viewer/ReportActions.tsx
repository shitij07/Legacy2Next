import { Copy, Download, Trash2, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

interface ReportActionsProps {
  title: string
  content: string
  reportId: number
  projectId: number
  onDelete: () => void
  format: string
}

export function ReportActions({ title, content, projectId, onDelete, format }: ReportActionsProps) {
  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content)
      toast.success('Report content copied')
    } catch {
      toast.error('Failed to copy')
    }
  }

  function handleDownload() {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const ext = format === 'json' ? 'json' : 'md'
    a.download = `${title.replace(/\s+/g, '_').toLowerCase()}.${ext}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="ghost" size="sm" asChild>
        <Link to={`/projects/${projectId}/reports`}>
          <ArrowLeft className="h-4 w-4" />
          Back
        </Link>
      </Button>
      <Button variant="outline" size="sm" onClick={handleCopy} aria-label="Copy report content">
        <Copy className="h-4 w-4" />
        Copy
      </Button>
      <Button variant="outline" size="sm" onClick={handleDownload} aria-label="Download report">
        <Download className="h-4 w-4" />
        Download
      </Button>
      <Button variant="danger" size="sm" onClick={onDelete} aria-label="Delete report">
        <Trash2 className="h-4 w-4" />
        Delete
      </Button>
    </div>
  )
}
