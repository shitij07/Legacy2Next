import type { Project } from '@/lib/types'
import { ProjectCard } from './ProjectCard'

interface ProjectListProps {
  projects: Project[]
  onDelete: (project: Project) => void
}

export function ProjectList({ projects, onDelete }: ProjectListProps) {
  if (projects.length === 0) return null

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} onDelete={onDelete} />
      ))}
    </div>
  )
}
