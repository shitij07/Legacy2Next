import { memo } from 'react'
import { FileCode, Trash2 } from 'lucide-react'
import type { Project } from '@/lib/types'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface ProjectCardProps {
  project: Project
  onDelete: (project: Project) => void
}

export const ProjectCard = memo(function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <Card className="group relative flex flex-col p-5">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500/10">
            <FileCode className="h-5 w-5 text-primary-500" aria-hidden="true" />
          </div>
          <div>
            <h3 className="font-medium text-neutral-900">{project.name}</h3>
            <p className="text-xs text-neutral-500">
              Created {formatDate(project.created_at)}
            </p>
          </div>
        </div>
      </div>

      {project.description && (
        <p className="mb-3 line-clamp-2 text-sm text-neutral-600">{project.description}</p>
      )}

      <div className="mt-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={project.status === 'completed' ? 'success' : 'default'}>
            {project.status}
          </Badge>
          <span className="text-xs text-neutral-500">
            {project.file_count} file{project.file_count !== 1 ? 's' : ''}
          </span>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(project)}
          aria-label={`Delete ${project.name}`}
          className="opacity-0 group-hover:opacity-100 focus:opacity-100"
        >
          <Trash2 className="h-4 w-4 text-error" aria-hidden="true" />
        </Button>
      </div>
    </Card>
  )
})
