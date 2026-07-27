import { Calendar, Clock, FileCode, Tag } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Project } from '@/lib/types'

interface ProjectMetadataProps {
  project: Project
}

export function ProjectMetadata({ project }: ProjectMetadataProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const rows: { icon: React.ReactNode; label: string; value: string }[] = [
    {
      icon: <Tag className="h-4 w-4" aria-hidden="true" />,
      label: 'Language',
      value: project.language === 'unknown' ? 'Not detected' : project.language,
    },
    {
      icon: <FileCode className="h-4 w-4" aria-hidden="true" />,
      label: 'Framework',
      value: project.framework === 'unknown' ? 'Not detected' : project.framework,
    },
    {
      icon: <Calendar className="h-4 w-4" aria-hidden="true" />,
      label: 'Created',
      value: formatDate(project.created_at),
    },
    {
      icon: <Clock className="h-4 w-4" aria-hidden="true" />,
      label: 'Updated',
      value: formatDate(project.updated_at),
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Project Info</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-neutral-600">Status</span>
          <Badge variant={project.status === 'completed' ? 'success' : 'default'}>
            {project.status}
          </Badge>
        </div>

        {project.description && (
          <div>
            <p className="mb-1 text-sm text-neutral-600">Description</p>
            <p className="text-sm text-neutral-800">{project.description}</p>
          </div>
        )}

        <div className="space-y-3">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center gap-3">
              <span className="flex h-8 w-8 items-center justify-center rounded-md bg-neutral-200 text-neutral-500">
                {row.icon}
              </span>
              <div>
                <p className="text-xs text-neutral-600">{row.label}</p>
                <p className="text-sm text-neutral-800">{row.value}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
