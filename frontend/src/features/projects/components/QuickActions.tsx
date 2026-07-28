import { Upload, BarChart3, FileText, GitCompare } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface QuickActionsProps {
  projectId: number
}

export function QuickActions({ projectId }: QuickActionsProps) {
  const navigate = useNavigate()

  const actions = [
    {
      label: 'Upload Codebase',
      description: 'Upload your legacy codebase for analysis',
      icon: Upload,
      onClick: () => navigate(`/projects/${projectId}/uploads`),
    },
    {
      label: 'Run Analysis',
      description: 'Start a new analysis of the uploaded codebase',
      icon: BarChart3,
      disabled: true,
    },
    {
      label: 'View Reports',
      description: 'View analysis reports and insights',
      icon: FileText,
      onClick: () => navigate(`/projects/${projectId}/reports`),
    },
    {
      label: 'Compare Analyses',
      description: 'Compare two analyses side by side',
      icon: GitCompare,
      onClick: () => navigate(`/projects/${projectId}/comparison`),
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-3">
          {actions.map((action) => {
            const Icon = action.icon
            return (
              <Button
                key={action.label}
                variant="outline"
                disabled={action.disabled}
                onClick={action.onClick}
                className="flex h-auto flex-col items-center gap-2 py-4 text-center"
                title={action.disabled ? 'Coming soon' : action.label}
              >
                <Icon className="h-5 w-5 text-neutral-500" aria-hidden="true" />
                <div>
                  <p className="text-sm font-medium text-neutral-800">{action.label}</p>
                  <p className="mt-0.5 text-xs text-neutral-500">{action.description}</p>
                </div>
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
