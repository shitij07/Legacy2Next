import { Plus } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'

interface ReportsHeaderProps {
  projectName?: string
  onGenerate: () => void
}

export function ReportsHeader({ projectName, onGenerate }: ReportsHeaderProps) {
  return (
    <PageHeader
      title={`Reports${projectName ? ` — ${projectName}` : ''}`}
      description="Generate and manage analysis reports."
      actions={
        <Button onClick={onGenerate}>
          <Plus className="h-4 w-4" />
          Generate Report
        </Button>
      }
    />
  )
}
